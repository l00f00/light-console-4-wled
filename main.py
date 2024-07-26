import time
import ujson
from machine import Pin, ADC
import network
import requests
import urequests
import json
import random
import socket

# Stato globale in cui si trova il sistema (stato dei pulsanti, valori degli slider, array di ip a cui inviare le richieste)
global_state = {
    "buttons": {
        "MODALITA_MODIFICA": 0,
        "COLONNE_STATE": 0,
        "LEDTETTO_STATE": 0,
        "BANCONI_STATE": 0,
        "PREVIOUS": 0,
        "NEXT": 0,
        "SAVE": 0,
    },
    "ip_addresses_selected": [],
    "sliders": {"slider_R": 0, "slider_G": 0, "slider_B": 0},
    "output_pins_state": {},  # Nuova chiave per lo stato degli output pin
    "bigblue": False,
    "preset_saved": False,   # Flag per indicare se il preset è stato salvato
    "next_executed": False,  # Flag per indicare se next_preset è stato eseguito
    "previous_executed": False # Flag per indicare se prev_preset è stato eseguito
}

# Funzione per inviare richieste
def send_request(url, data):
    headers = {'Content-Type': 'application/json; charset=utf8'}
    try:
        req = requests.post(url, json=data, headers=headers, timeout=0.25)
        print(req.text)
    except Exception as e:
        pass

# Gestione dei pulsanti
class Button:
    def __init__(self, input_pin, output_pin=None, state_name=None, ip_addresses=None, check_ledstrip_on=None):
        self.input_pin = Pin(input_pin, Pin.IN, Pin.PULL_UP)
        self.output_pin = [Pin(pin, Pin.OUT) for pin in output_pin] if output_pin else None
        self.state_name = state_name
        self.ip_addresses = ip_addresses or []
        self.check_ledstrip_on = check_ledstrip_on
        self.input_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.handle_interrupt)
        self.last_press_time = 0
        print(f"Button initialized with input pin {input_pin}, output pin {output_pin}, state name {state_name}, ip addresses {ip_addresses}")

    def handle_interrupt(self, pin):
        current_time = time.ticks_ms()
        button_pressed = self.input_pin.value() == 0
        time_since_last_press = time.ticks_diff(current_time, self.last_press_time)

        if button_pressed and time_since_last_press < 400:  # Button is released and pressed again within 0.5 seconds
            self.last_press_time = current_time  # Update last press time to current time
            print(f"Button {self.state_name} - {self.input_pin} ignored")
        
        elif button_pressed and time_since_last_press > 800:  # Button is pressed and more than 1 second has passed
            self.last_press_time = current_time
            self.toggle_state()
            print(f"Button {self.state_name} - {self.input_pin} toggled")

    def toggle_state(self):
        if self.state_name:
            if self.state_name not in global_state["buttons"]:
                global_state["buttons"][self.state_name] = 0
            global_state["buttons"][self.state_name] = not global_state["buttons"][self.state_name]
            if global_state["buttons"][self.state_name]:
                for ip in self.ip_addresses:
                    if ip not in global_state["ip_addresses_selected"]:
                        global_state["ip_addresses_selected"].append(ip)
                        send_request(ip, self.format_slider_data())
            else:
                for ip in self.ip_addresses:
                    if ip in global_state["ip_addresses_selected"]:
                        global_state["ip_addresses_selected"].remove(ip)

        if self.output_pin:
            for pin in self.output_pin:
                pin_state = global_state["buttons"][self.state_name]
                pin.value(pin_state)
                global_state["output_pins_state"][str(pin)] = pin_state  # Convert pin to string for readability

    def format_slider_data(self):
        return {
            "on": True,
            "bri": 255,
            "seg": [{
            "on": True,
            "id": 0,
            "sel": True,
                "col": [
                    [global_state["sliders"]["slider_R"], global_state["sliders"]["slider_G"], global_state["sliders"]["slider_B"]]
                ]
            }]
        }

# Gestione degli slider
class Slider:
    def __init__(self, pin, name):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.name = name

    def read(self):
        raw_value = self.adc.read()
        mapped_value = int((raw_value / 4095) * 255)
        global_state["sliders"][self.name] = mapped_value
        print(f"Slider {self.name} value: {mapped_value}")

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f'Connecting to network {ssid}...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print(f'Connected to network {ssid}')
    print('Network configuration:', wlan.ifconfig())

def read_sliders():
    for slider in sliders:
        slider.read()

def send_slider_data():
    data = {
        "on": True,
        "bri": 255,
        "v": True,
        "seg": [{
            "on": True,
            "id": 0,
            "sel": True,
            "col": [
                [global_state["sliders"]["slider_R"], global_state["sliders"]["slider_G"], global_state["sliders"]["slider_B"]]
            ]
        }]
    }
    for url in global_state["ip_addresses_selected"]:
        send_request(url, data)

# Inizializzazione WiFi
connect_wifi('Lab', 'itsnotabugitsafeature')

# Configurazione dei pulsanti
buttons_config = [
    {
        "input_pin": 12,
        "output_pin": [23],
        "state_name": "MODALITA_MODIFICA",
        "ip_addresses": [],
        "check_ledstrip_on": {"on": True,"bri": 255,"seg": [{"on": True,"id": 0,"sel": True,}]},
    },
    {
        "input_pin": 14,
        "output_pin": [22],
        "state_name": "COLONNE_STATE",
        "ip_addresses": ["http://192.168.1.108/json/state"]
    },
    {
        "input_pin": 27,
        "output_pin": [19],
        "state_name": "BANCONI_STATE",
        "ip_addresses": ["http://192.168.1.194/json/state"]
    },
    {
        "input_pin": 26,
        "output_pin": [21],
        "state_name": "LEDTETTO_STATE",
        "ip_addresses": ["http://192.168.1.41/json/state"]
    },
    {
        "input_pin": 25,
        "state_name": "PREVIOUS",
        "ip_addresses": []
    },
    {
        "input_pin": 33,
        "state_name": "NEXT",
        "ip_addresses": []
    },
    {
        "input_pin": 13,
        "state_name": "SAVE",
        "ip_addresses": []
    },
]

buttons = [Button(**config) for config in buttons_config]

# Configurazione degli slider
sliders_config = [
    {"pin": 39, "name": "slider_R"},
    {"pin": 34, "name": "slider_G"},
    {"pin": 35, "name": "slider_B"}
]

sliders = [Slider(**config) for config in sliders_config]

# Configurazione dei pannelli del tetto
tetto_config = [
    {
        "input_pin": 15,
        "state_name": "T1-portone",
        "ip_addresses": ["http://192.168.1.29/json/state/"],
    },
    {
        "input_pin": 16,
        "state_name": "T2-biliardino",
        "ip_addresses": ["http://192.168.1.217/json/state/"],
    },
    {
        "input_pin": 32,
        "state_name": "T3-Bar",
        "ip_addresses": ["http://192.168.1.46/json/state/"],
    },
    {
        "input_pin": 4,
        "state_name": "T4-Scala",
        "ip_addresses": ["http://192.168.1.41/json/state/"],
    }
]

# Funzione per inviare richieste per i pannelli del tetto
def send_request_tetto(url, data, method="POST"):
    json_data = json.dumps(data)
    try:
        if method == "POST":
            headers = {"Content-Type": "application/json"}
            req = requests.post(url, data=json_data, headers=headers, timeout=0.5)
        elif method == "GET":
            req = requests.get(url, timeout=0.5)
        return req
    except Exception as e:
        print(f"Timeout error sending request to {url}: {e}")
    return None

# Funzione per controllare e inviare i dati del tetto
def toggle_tetto():
    for config in tetto_config:
        input_pin = Pin(config["input_pin"], Pin.IN, Pin.PULL_UP)
        if input_pin.value() == 0:  # Se il pulsante è premuto
            print(f"Toggling tetto for {config['state_name']}")
            for url in config["ip_addresses"]:
                tetto_data = {
                    "seg": [
                        {
                            "id": 1,
                            "start": 210,
                            "stop": 211,
                            "on": "toggle"
                        }
                    ]
                }
                send_request_tetto(url, tetto_data, method="POST")
            time.sleep(0.1)  # Ritardo tra le richieste successive

        
# Funzione per gestire il salvataggio del preset
def save_preset():
    if not global_state["preset_saved"]:
        #new_preset_number = random.randint(12, 249)
        new_preset_number = get_presets() + 1
        ips = ["http://192.168.1.108/json/state", "http://192.168.1.194/json/state", "http://192.168.1.41/json/state"]
        print(f"Saving preset in slot {new_preset_number}")
        for ip in ips:
            try:
                data = {"psave": new_preset_number}
                send_request(ip, data)
                print(f"Preset saved in slot {new_preset_number} for {ip}")
            except Exception as e:
                print(f"Error saving preset to {ip}: {e}")
        print("out the loop")
        global_state["preset_saved"] = True  # Imposta il flag a True

    
# Funzione per gestire il passaggio al preset successivo
def next_preset():
    if not global_state["next_executed"]:
        presets = get_presets_as_json()
        print(presets)
        
        # Cast to string, since the value is an integer and subsequent call to index() will fail
        # because the keys are strings.
        ps = str(get_wled_state())
        if ps == "-1":
            ps = "1"
        print(ps)
        
        keys = list(presets.keys())
        index = keys.index(ps)
        next_index = (index + 1) % len(keys)
        next_preset = keys[next_index]
        print(keys)
        print(index)
        
        print("The next preset is: " + next_preset)
        data = {"on": True, "bri": 255, "transition": 7, "pl": -1, "ps": next_preset, "v": True}  # qui to string
        ips = ["http://192.168.1.108/json/state", "http://192.168.1.194/json/state", "http://192.168.1.41/json/state"]
        
        #ips = ["http://192.168.1.194/json/state"]
        
        for ip in ips:
            send_request(ip, data)
            print(f"Switched to the next preset for {ip}  and data {data}")
        global_state["next_executed"] = True  # Imposta il flag a True
# Funzione per gestire il passaggio al preset precedente
def prev_preset():
    if not global_state["previous_executed"]:
        presets = get_presets_as_json()
        print(presets)
        
        # Cast to string, since the value is an integer and subsequent call to index() will fail
        # because the keys are strings.
        ps = str(get_wled_state())
        if ps == "-1":
            ps = "1"
        print(ps)
        
        keys = list(presets.keys())
        index = keys.index(ps)
        next_index = (index - 1) % len(keys)
        next_preset = keys[next_index]
        print(keys)
        print(index)
        
        print("The next preset is: " + next_preset)
        data = {"on": True, "bri": 255, "transition": 7, "pl": -1, "ps": next_preset, "v": True}  # qui to string
        ips = ["http://192.168.1.108/json/state", "http://192.168.1.194/json/state", "http://192.168.1.41/json/state"]
        
        #ips = ["http://192.168.1.194/json/state"]
        
        for ip in ips:
            send_request(ip, data)
            print(f"Switched to the next preset for {ip}  and data {data}")
        global_state["previous_executed"] = True  # Imposta il flag a True

def get_wled_state():
    # URL del file JSON
    url = "http://192.168.1.194/json/state"
    
    try:
        # Funzione per fare una richiesta HTTP GET
        def http_get(url):
            _, _, host, path = url.split('/', 3)
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.connect(addr)
            s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
            response = b''
            headers_received = False
            content_length = 0
            while True:
            
                data = s.recv(1000)
                if data:
                    response += data
                    if not headers_received:
                        if b'\r\n\r\n' in response:
                            header_data, response = response.split(b'\r\n\r\n', 1)
                            headers = header_data.decode().split('\r\n')
                            for header in headers:
                                if header.lower().startswith('content-length'):
                                    content_length = int(header.split(':')[1].strip())
                                    break
                            headers_received = True
                            print(f"Content-Length: {content_length}")
                    
                    if headers_received and len(response) >= content_length:
                        break
                else:
                    break
            s.close()
            return response
        # Ottieni la risposta HTTP
        response = http_get(url)
        # Trova il corpo della risposta (dopo \r\n\r\n)
        if b'\r\n\r\n' in response:
            response = response.split(b'\r\n\r\n', 1)[1]
         # Decodifica il JSON
        json_data = ujson.loads(response)
        
        # Estrai i valori di ps e pl
        ps_value = json_data.get("ps", None)
        #ps_value = json_data.get("pl", None)##playlist value currently unuser
        
        print(f"Valore di ps: {ps_value}")
        #print(f"Valore di pl: {ps_value}")
        
        # Restituisci i valori di ps e pl
        return ps_value
    
    except Exception as e:
        print("Si è verificato un errore: ", e)
        return None
        
def get_presets():
    # URL del file JSON
    url = "http://192.168.1.194/presets.json"
    
    try:
        # Funzione per fare una richiesta HTTP GET
        def http_get(url):
            _, _, host, path = url.split('/', 3)
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.connect(addr)
            s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
            response = b''
            headers_received = False
            content_length = 0
            while True:
            
                data = s.recv(1000)
                if data:
                    response += data
                    if not headers_received:
                        if b'\r\n\r\n' in response:
                            header_data, response = response.split(b'\r\n\r\n', 1)
                            headers = header_data.decode().split('\r\n')
                            for header in headers:
                                if header.lower().startswith('content-length'):
                                    content_length = int(header.split(':')[1].strip())
                                    break
                            headers_received = True
                            print(f"Content-Length: {content_length}")
                    
                    if headers_received and len(response) >= content_length:
                        break
                else:
                    break
            s.close()
            return response
        # Ottieni la risposta HTTP
        response = http_get(url)
        # Trova il corpo della risposta (dopo \r\n\r\n)
        if b'\r\n\r\n' in response:
            response = response.split(b'\r\n\r\n', 1)[1]
        # Decodifica il JSON
        json_data = ujson.loads(response)
        # Conta il numero di oggetti nel JSON
        num_objects = len(json_data)
        print(f"Numero di oggetti nel JSON: {num_objects}")        
        print(json_data)
        print(ujson.dumps(json_data))
        # Stampa il JSON in formato leggibile
        # Restituisci il numero di oggetti
        return num_objects
    
    except Exception as e:
        print("Si è verificato un errore: ", e)
        
def get_presets_as_json():
    # URL del file JSON
    url = "http://192.168.1.194/presets.json"
    
    try:
        # Funzione per fare una richiesta HTTP GET
        def http_get(url):
            _, _, host, path = url.split('/', 3)
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.connect(addr)
            s.send(bytes('GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
            response = b''
            headers_received = False
            content_length = 0
            while True:
            
                data = s.recv(1000)
                if data:
                    response += data
                    if not headers_received:
                        if b'\r\n\r\n' in response:
                            header_data, response = response.split(b'\r\n\r\n', 1)
                            headers = header_data.decode().split('\r\n')
                            for header in headers:
                                if header.lower().startswith('content-length'):
                                    content_length = int(header.split(':')[1].strip())
                                    break
                            headers_received = True
                            print(f"Content-Length: {content_length}")
                    
                    if headers_received and len(response) >= content_length:
                        break
                else:
                    break
            s.close()
            return response
        # Ottieni la risposta HTTP
        response = http_get(url)
        # Trova il corpo della risposta (dopo \r\n\r\n)
        if b'\r\n\r\n' in response:
            response = response.split(b'\r\n\r\n', 1)[1]
        # Decodifica il JSON
        json_data = ujson.loads(response)    
        #print(json_data)
        #print(ujson.dumps(json_data))
        return json_data
    
    except Exception as e:
        print("Si è verificato un errore: ", e)

# Funzione principale per gestire il loop principale
def main():
    #print(global_state)
    
    while True:
        toggle_tetto()
        if global_state["buttons"]["MODALITA_MODIFICA"]:
            #print(global_state)
            read_sliders()
            send_slider_data()
        if global_state["buttons"]["SAVE"] and not global_state["preset_saved"]:
            save_preset()
        if not global_state["buttons"]["SAVE"]:
            global_state["preset_saved"] = False  # Resetta il flag quando il pulsante SAVE non è più premuto
        if global_state["buttons"]["NEXT"] and not global_state["next_executed"]:
            next_preset()
        if not global_state["buttons"]["NEXT"]:
            global_state["next_executed"] = False  # Resetta il flag quando il pulsante NEXT non è più premuto
        if global_state["buttons"]["PREVIOUS"] and not global_state["previous_executed"]:
            prev_preset()
        if not global_state["buttons"]["PREVIOUS"]:
            global_state["previous_executed"] = False  # Resetta il flag quando il pulsante PREVIOUS non è più premuto
        time.sleep(0.1)  # Sleep for a short while to avoid busy-waiting
        
        #print(global_state)  # Stampa il global_state dopo il busy-wait

print("Initialize Consolle")
main()
