# Setup a Raspberry Pi
### (1)  Setup the image
For setting up the image see the official docs: [Installation Guide](https://www.raspberrypi.org/documentation/installation/installing-images/)

**Note:** Make sure that a file `ssh` exists in the root folder of the sd card before booting the first time.


Connect to the Pi via standard username `pi` and standard password `raspberry`. 

### (2) Setup Wireless Network
Add the following lines to the `/etc/wpa_supplicant/wpa_supplicant.conf` file and change the ssid and psk accordingly:

```
network={
    ssid="myWifiSsid"
    psk="myWifiPassword"
}
```
and run the following commands:
```
wpa_cli
   interface wlan0
   reconfigure
   quit
```

More information about the Pi network configuration can be found in the 
[official docs](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md).

### (3) Setup Ethernet Network
The Raspberry Pi should be connected to the router via ethernet. In order to get the GameController data, the
Raspberry Pi has to be in the "10.0.x.x/16" subnet. Also make sure, there's no other device with the same IP!  

Setup a static IP using this [guide](https://www.modmypi.com/blog/how-to-give-your-raspberry-pi-a-static-ip-address-update)

### Misc
Changing the keyboard layout on the raspberry:
https://raspberrypi.stackexchange.com/questions/24161/change-keyboard-layout-in-console

---
This image shows where the colored wires have to go on the GPIO  pins:  
![GPIO Color Codes](https://github.com/BerlinUnited/RoboCupTools/blob/master/GoPro/gpio_color_codes.png)