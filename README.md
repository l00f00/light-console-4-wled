# LabZero Light Control System

Questo progetto è un sistema di controllo luci basato su ESP32 e MicroPython, progettato per gestire l'illuminazione nel nostro laboratorio, LabZero (labzero.org). Il sistema include pulsanti, slider e funzionalità di rete per gestire e sincronizzare gli stati di illuminazione tra vari dispositivi.

## Installazione

### Clona il Repository

git clone https://github.com/labzero/labzero-light-control.git

### Installa le Dipendenze di Micropython
per il Sistema di Controllo Luci LabZero
Queste librerie sono per MicroPython e dovrebbero essere installate usando mip o Thonny

micropython-ujson
micropython-machine
micropython-network
micropython-requests
micropython-urequests
micropython-socket

#### Utilizzando mip
Per installare le librerie richieste utilizzando mip, esegui i seguenti comandi nel tuo ambiente MicroPython:

import mip

mip.install('micropython-ujson')
mip.install('micropython-machine')
mip.install('micropython-network')
mip.install('micropython-requests')
mip.install('micropython-urequests')
mip.install('micropython-socket')

#### Utilizzando Thonny
In alternativa, puoi installare le librerie usando Thonny:

1. Apri Thonny IDE.
2. Vai su Strumenti -> Gestisci pacchetti.
3. Cerca ogni pacchetto (ad esempio, micropython-ujson) e installalo.
4. Assicurati che il tuo ESP32 sia collegato al computer e che Thonny sia configurato per utilizzare MicroPython (ESP32).

## Configurazione

### Configurazione WiFi
Configura le impostazioni WiFi nella funzione `connect_wifi`:

import network

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

connect_wifi('XXX', 'passWORD')

### Configurazione Pulsanti
Definisci i pulsanti e i relativi pin nella lista `buttons_config`:

buttons_config = [
    {
        "input_pin": 12,
        "output_pin": [23],
        "state_name": "MODALITA_MODIFICA",
        "ip_addresses": [],
    },
    {
        "input_pin": 14,
        "output_pin": [22],
        "state_name": "COLONNE_STATE",
        "ip_addresses": ["http://192.168.1.108/json/state"]
    },
    # Aggiungi altre configurazioni di pulsanti se necessario
]

buttons = [Button(**config) for config in buttons_config]

### Configurazione Slider
Definisci gli slider e i relativi pin nella lista `sliders_config`:

sliders_config = [
    {"pin": 39, "name": "slider_R"},
    {"pin": 34, "name": "slider_G"},
    {"pin": 35, "name": "slider_B"}
]

sliders = [Slider(**config) for config in sliders_config]

## Utilizzo

### Avvio del Sistema
Per avviare il sistema di controllo luci, chiama la funzione `main`:

print("Initialize Consolle")
main()

### Gestione Pulsanti
I pulsanti sono inizializzati con pin di input e output e un nome di stato opzionale. Quando premuti, cambiano il loro stato e inviano richieste agli indirizzi IP configurati, se applicabile.

### Gestione Slider
Gli slider leggono i valori di input analogici e aggiornano lo stato globale con i valori RGB, che vengono poi inviati agli indirizzi IP configurati.

### Gestione Preset
- Salva Preset: Salva la configurazione di illuminazione corrente in uno slot preset.
- Prossimo/Precedente Preset: Naviga tra i preset salvati.

### Controllo del Pannello del Tetto
Pulsanti speciali sono configurati per controllare i pannelli del tetto, cambiando il loro stato e inviando richieste agli indirizzi IP specificati.

### Stato Globale
Il sistema mantiene uno stato globale per tracciare le pressioni dei pulsanti, i valori degli slider e gli indirizzi IP selezionati. Questo stato è utilizzato per sincronizzare le configurazioni di illuminazione su più dispositivi.

## Funzioni

- send_request(url, data): Invia una richiesta HTTP POST con i dati forniti.
- Button: Classe per gestire gli input dei pulsanti e i loro stati.
- Slider: Classe per gestire gli input degli slider e i loro valori.
- connect_wifi(ssid, password): Connette l'ESP32 alla rete WiFi specificata.
- read_sliders(): Legge i valori correnti da tutti gli slider.
- send_slider_data(): Invia i valori correnti degli slider agli indirizzi IP selezionati.
- save_preset(): Salva la configurazione corrente come un nuovo preset.
- next_preset(): Passa al preset successivo.
- prev_preset(): Passa al preset precedente.
- toggle_tetto(): Cambia lo stato dei pannelli del tetto.

## Contributi

I contributi sono benvenuti! Si prega di fare un fork del repository e inviare una pull request con le proprie modifiche.

## Licenza

Questo progetto è concesso in licenza sotto la licenza MIT. Vedi il file LICENSE per i dettagli.
