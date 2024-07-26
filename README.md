<<<<<<< HEAD
# light-console-4-wled
custom light console for wled setup
=======
# LabZero Light Control System

This project is for a custom peripheral based on ESP32 and MicroPython, designed to control the lights in our lab, LabZero (labzero.org). The system includes buttons, sliders, and network capabilities to manage and synchronize lighting states across various devices.

## Installation

### Clone the Repository

````bash
git clone https://github.com/labzero/labzero-light-control.git

Install Dependencies using Thonny
Alternatively, you can install the libraries using Thonny:

Open Thonny IDE.
Go to Tools -> Manage Packages.
Search for each package (e.g., micropython-ujson) and install it.
Make sure your ESP32 is connected to your computer and Thonny is configured to use MicroPython (ESP32).
I use Pymark extension for Vs Code ([Pymark](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr))

Libs:
micropython-ujson
micropython-machine
micropython-network
micropython-requests
micropython-urequests
micropython-socket



Certamente! Ecco tutto il contenuto del README.md in inglese:

markdown
Copy code
# LabZero Light Control System

This project is for a custom peripheral based on ESP32 and MicroPython, designed to control the lights in our lab, LabZero (labzero.org). The system includes buttons, sliders, and network capabilities to manage and synchronize lighting states across various devices.

## Installation

### Clone the Repository
```bash
git clone https://github.com/labzero/labzero-light-control.git
Install Dependencies
Create a requirements.txt file with the following content:

plaintext
Copy code
# requirements.txt for LabZero Light Control System
# These libraries are for MicroPython and should be installed using mip or Thonny

micropython-ujson
micropython-machine
micropython-network
micropython-requests
micropython-urequests
micropython-socket
Install Dependencies using mip
To install the required libraries using mip, run the following commands in your MicroPython environment:

python
Copy code
import mip

mip.install('micropython-ujson')
mip.install('micropython-machine')
mip.install('micropython-network')
mip.install('micropython-requests')
mip.install('micropython-urequests')
mip.install('micropython-socket')
Install Dependencies using Thonny
Alternatively, you can install the libraries using Thonny:

Open Thonny IDE.
Go to Tools -> Manage Packages.
Search for each package (e.g., micropython-ujson) and install it.
Make sure your ESP32 is connected to your computer and Thonny is configured to use MicroPython (ESP32).

Configuration
WiFi Setup
Configure your WiFi settings in the connect_wifi function:

python
Copy code
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
Buttons Configuration
Define the buttons and their corresponding pins in the buttons_config list:

python
Copy code
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
    // Add more button configurations as needed
]

buttons = [Button(**config) for config in buttons_config]
Sliders Configuration
Define the sliders and their corresponding pins in the sliders_config list:

python
Copy code
sliders_config = [
    {"pin": 39, "name": "slider_R"},
    {"pin": 34, "name": "slider_G"},
    {"pin": 35, "name": "slider_B"}
]

sliders = [Slider(**config) for config in sliders_config]
Usage
Running the System
To start the light control system, call the main function:

python
Copy code
print("Initialize Consolle")
main()
Button Handling
Buttons are initialized with input and output pins and an optional state name. When pressed, they toggle their state and send requests to configured IP addresses if applicable.

Slider Handling
Sliders read analog input values and update the global state with the RGB values, which are then sent to the configured IP addresses.

Preset Management
Save Preset: Saves the current lighting configuration to a new preset slot.
Next/Previous Preset: Navigates through the saved presets.
Roof Panel Control
Special buttons are configured to control roof panels, toggling their state and sending requests to specified IP addresses.

Global State
The system maintains a global state to track button presses, slider values, and selected IP addresses. This state is used to synchronize lighting configurations across multiple devices.

Functions
send_request(url, data): Sends an HTTP POST request with the provided data.
Button: Class to manage button inputs and their states.
Slider: Class to manage slider inputs and their values.
connect_wifi(ssid, password): Connects the ESP32 to the specified WiFi network.
read_sliders(): Reads the current values from all sliders.
send_slider_data(): Sends the current slider values to the selected IP addresses.
save_preset(): Saves the current configuration as a new preset.
next_preset(): Switches to the next preset.
prev_preset(): Switches to the previous preset.
toggle_tetto(): Toggles the state of the roof panels.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
````
>>>>>>> master
