# GoPi

GoPi is an application designed to record SPL RoboCup games using a GoPro camera, controlled by a Raspberry Pi. 
The Raspberry Pi listens for new game events from the GameController and manages the GoPro to start or stop recording 
based on the game state. The application's status is displayed via LEDs (see LED states below) connected to the 
Raspberry Pi. Additionally, GoPi logs the mapping of video filenames to their respective games and includes a small 
web page that shows the current messages on the message bus.

## Setup Raspberry Pi
[Setup Guide](./docs/Raspi-Setup.md)

## Installation
- there is an `install.sh` script, which installs the required dependencies
- root permissions are required for the installation script for:
  - register GoPi as systemd service
  - set a new hostname (optional)
  - set a static ip address (optional)
- the required python packages are installed into a virtual environment (`.venv`) in the project directory
- after installation a reboot may be required (if hostname or static ip was set)
- other options for the `install.sh`:
  - `uninstall` un-installs everything
  - `check` checks the required dependencies
  - `ip` setups the static ip configuration only
  - `help` shows the help message


### Variant #1
- connect to the Raspberry Pi and run
```shell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/BerlinUnited/RoboCupTools/master/GoPro/shell/install.sh)"
# or
sh -c "$(wget -qO- https://raw.githubusercontent.com/BerlinUnited/RoboCupTools/master/GoPro/shell/install.sh)"
# or
wget https://raw.githubusercontent.com/BerlinUnited/RoboCupTools/master/GoPro/shell/install.sh
sh install.sh
```
### Variant #2
- connect to the Raspberry Pi
- checkout or download the project
```shell
git clone https://github.com/BerlinUnited/RoboCupTools.git
# or just the latest code
git clone --depth=1 https://github.com/BerlinUnited/RoboCupTools.git
```
- `cd` to the `GoPro` directory
- execute the install script
  - `sudo ./shell/install.sh`

### Requirements
- python3 python3-pip python3-venv bluez
- python modules: open_gopro pyzmq RPi.GPIO websockets bleak goprocam

## Running

If the startup script and the config was set correctly the systemd service starts on the next (re-)boot of the Raspberry Pi.

GoPi can be controlled with the following commands:  
  `sudo gopro start`  
  `sudo gopro stop`  
  `sudo gopro status` 

To manually start GoPi with systemd:  
  `sudo systemctl start gopro`  
  `sudo systemctl stop gopro`  
  `sudo systemctl status gopro`

### Manually run python scripts

- start the GoPi directly
  - `.venv/bin/python main.py gopi`
- for help use:
  - `.venv/bin/python main.py -h`
- the individual services can be started separately:
  - `.venv/bin/python main.py service [bus|led|gl|gc|gopro|web]`
- there are also some scripts that may be useful:
  - `.venv/bin/python main.py script [ble|pair|gc|video|wake]`

NOTE: everything can also be started as a python module, eg:  
`.venv/bin/python -m services.bus`  
`.venv/bin/python -m scripts.bus`
    
### LED States
|  blue |     green     | red   | Description                                           |
|:-------------:|:-------------:|:-----:|-------------------------------------------------------|
| blink (short) |               |       | Wifi network is not available/visible                 |
| blink (1/2s)  |               |       | Currently not connected to network / GoPro            |
| blink (~1s))  |               | blink | Connect to GoPro, but no sd card available            |
|      On       |               |       | Connected to GoPro and ready for recording            |
|               |      Off      |       | No GameController available                           |
|               | blink (~1/2s) |       | Invalid GameController source/IP                      |
|               |  blink (~1s)  |       | A game vs. INVISIBLES                                 |
|               |      On       |       | A game with two teams - GameController is 'connected' |
|               |               | blink | Camera is recording                                   |
|               |               | Off   | Camera is NOT recording                               |
|     Off       |      Off      | Off   | Raspi is not powered or isn't connected to anything   |

### Logging

By default, GoPi just prints out its log stdout. If started via systemd service, the log can be viewed   
  `journalctl -u gopro [-f]`  

Logs of the recorded games are created in the `path/to/GoPro/logs/` directory. Each log contains the file name of the recorded video files separated by ';'.

### Tests
Some tests to check the functionality of the GoPro setup
- normal: run a complete game with 2 teams; the camera should record both halfs and a video log should be written
- normal invisible: run a complete game with only one team; no video should be recorded, but an empty video log is still created
- missing GameController: the leds should indicate that the GameController is missing
- missing wifi: the leds should indicate that
     - ... the wifi network is missing
     - ... the raspi can not log in to the network (not implemented!)
- loosing wifi:
    - not in game / recording: the leds should indicate that
    - while recording: the leds should indicate this, and when the network is back, it should reconnect
- raspi loosing power:
    - not in game / recording
        - and comes back when not in game: raspi should reconnect
        - and comes back when in game: raspi should reconnect and start the recording
        - and comes back and no GameController available: the leds should indicate this
    - while recording
        - and comes back while still in game: raspi should reconnect and continue recording
        - and comes back while not any more in game (GC in finish): raspi should reconnect and stop recording
        - and comes back and no GameController available: raspi should reconnect and stop recording
- manual recording: ???
- camera has no card: the leds should indicate that the card is missing
- long run:
        - normal run, but never press "FINISH": after a certain time, the raspi should stop recording
        - normal run, but never press "PLAY": after a certain time, the raspi should stop recording


## Bluetooth

For a detailed description, how to control a GoPro from a RaspberryPi over Bluetooth, see:  
https://github.com/KonradIT/goprowifihack/blob/master/Bluetooth/Platforms/RaspberryPi.md

In order to pair the GoPro with the RaspberryPi, use the following example:
```shell
bluetoothctl
> scan on
> scan off
> scan le
> scan off
> trust DE:AD:BE:EF
> pair DE:AD:BE:EF
> connect DE:AD:BE:EF
> disconnect
> untrust DE:AD:BE:EF
> remove DE:AD:BE:EF
```

Alternatively use the commands directly from the terminal
```shell
bluetoothctl scan on
bluetoothctl scan off
bluetoothctl trust DE:AD:BE:EF
bluetoothctl pair DE:AD:BE:EF
bluetoothctl untrust DE:AD:BE:EF
bluetoothctl remove DE:AD:BE:EF
# list the trusted/paired devies
bluetoothctl devices Trusted
bluetoothctl devices Paired
```

### Older OS version
With older OS version of the Raspi OS, we had also success using the following commands:
```
sudo gatttool -t random -b F8:D2:E9:F0:AC:0B -I
connect
# beep on/off
char-write-req 2f 03160101
char-write-req 2f 03160100

# wifi on/off
char-write-req 2f 03170101
char-write-req 2f 03170100

# example send the command noninteractive in one line
sudo gatttool -i hci0 -t random -b F8:D2:E9:F0:AC:0B --char-write-req --handle 0x002f --value 03170101
```

And some handles from the GoPro bluetooth:

    handle: 0x0001, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x0002, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x0003, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0004, uuid: 00002a00-0000-1000-8000-00805f9b34fb
    handle: 0x0005, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0006, uuid: 00002a01-0000-1000-8000-00805f9b34fb
    handle: 0x0007, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0008, uuid: 00002a04-0000-1000-8000-00805f9b34fb
    handle: 0x0009, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x000a, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x000b, uuid: 00002a07-0000-1000-8000-00805f9b34fb
    handle: 0x000c, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x000d, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x000e, uuid: 00002a19-0000-1000-8000-00805f9b34fb
    handle: 0x000f, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x0010, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x0011, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0012, uuid: 00002a29-0000-1000-8000-00805f9b34fb
    handle: 0x0013, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0014, uuid: 00002a24-0000-1000-8000-00805f9b34fb
    handle: 0x0015, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0016, uuid: 00002a25-0000-1000-8000-00805f9b34fb
    handle: 0x0017, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0018, uuid: 00002a27-0000-1000-8000-00805f9b34fb
    handle: 0x0019, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x001a, uuid: 00002a26-0000-1000-8000-00805f9b34fb
    handle: 0x001b, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x001c, uuid: 00002a28-0000-1000-8000-00805f9b34fb
    handle: 0x001d, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x001e, uuid: 00002a23-0000-1000-8000-00805f9b34fb
    handle: 0x001f, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0020, uuid: 00002a50-0000-1000-8000-00805f9b34fb
    handle: 0x0021, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x0022, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0023, uuid: b5f90002-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0024, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0025, uuid: b5f90003-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0026, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0027, uuid: b5f90004-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0028, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0029, uuid: b5f90005-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x002a, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x002b, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x002c, uuid: b5f90006-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x002d, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x002e, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x002f, uuid: b5f90072-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0030, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0031, uuid: b5f90073-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0032, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x0033, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0034, uuid: b5f90074-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0035, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0036, uuid: b5f90075-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0037, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x0038, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0039, uuid: b5f90076-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x003a, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x003b, uuid: b5f90077-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x003c, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x003d, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x003e, uuid: b5f90078-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x003f, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0040, uuid: b5f90079-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0041, uuid: 00002902-0000-1000-8000-00805f9b34fb
    handle: 0x0042, uuid: 00002800-0000-1000-8000-00805f9b34fb
    handle: 0x0043, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0044, uuid: b5f90091-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0045, uuid: 00002803-0000-1000-8000-00805f9b34fb
    handle: 0x0046, uuid: b5f90092-aa8d-11e3-9046-0002a5d5c51b
    handle: 0x0047, uuid: 00002902-0000-1000-8000-00805f9b34fb


## Video Tutorial
A Video explaining the setup and handling of the GoPro - Pi Setup can be found at https://www2.informatik.hu-berlin.de/~naoth/ressources/howto-robocup-gopro-small.mp4

## Known Issues
- Not every USB Port of Pi gives enough power to load the GoPro
  - if the Raspi supplies too little power via the USB port, no "PC connection" is recognised by the GoPro and therefore the USB Ethernet interface is not activated
  - a stronger power source on the Raspi or a separate power source for the GoPro (USB hub) can solve the problem
- with BlueZ version 5.66 the paired GoPro is unpaired, when `disconnect` is called via python
  - with a newer version (5.70+) this behavior did not occur
  - the behavior can be shown, when setting the log level to `DEBUG`
    - the communication with BlueZ is shown on the terminal
    - the following output is displayed if the "error" occurs
      - `[DEBUG]: received D-Bus signal: org.freedesktop.DBus.Properties.PropertiesChanged (/org/bluez/hci0/dev_FB_D2_7D_86_13_F8): ['org.bluez.Device1', {'Paired': <dbus_fast.signature.Variant ('b', False)>, 'Connected': <dbus_fast.signature.Variant ('b', False)>}, []]`
    - otherwise, the "paired" part is not shown
      - `[DEBUG]: received D-Bus signal: org.freedesktop.DBus.Properties.PropertiesChanged (/org/bluez/hci0/dev_FB_D2_7D_86_13_F8): ['org.bluez.Device1', {'Connected': <dbus_fast.signature.Variant ('b', False)>}, []]`
