This setup works with any Raspberry Pi with Raspbian Stretch Lite with Wi-fi and an Ethernet Port and the following 
GoPro models: Session 4 and GoPro5. It might work with GoPro 3 and 6 as well.

#### Setup the scripts

- connect to the Raspberry Pi

Setup Startup-Script:
- copy the "gopro.service" file to "/lib/systemd/system/"  
	`sudo cp gopro.service /lib/systemd/system/`
- make it executable  
	`sudo chmod 644 /lib/systemd/system/gopro.service`  
- update services  
    `sudo systemctl daemon-reload`  
    `sudo systemctl enable gopro.service`  

Setup GoPro-Controller-Script:
- copy all python files to "/home/pi/GoPro/"

**Note:** if an other directory or user is used, the path to the main script in the GoPro.service file has to be
adjusted!

- make main python file executable
	`chmod +x /home/pi/GoPro/main.py`

Config:
- Adjust the "config.py" file for the used GoPro (ssid and password). This information should be provided by the GoPro.

#### RUNNING

If the startup script and the config was set correctly the init script starts on the next (re-)boot of the Raspberry Pi.

The GoPro Controller know the following commands:  
  `sudo service gopro start`
  `sudo service gopro stop`
  `sudo service gopro status`

To manually start the gopro-controller with the init-script:  
  `sudo service gopro start`

OR  

start the gopro-controller directly  
  `sudo /home/pi/GoPro/main.py -b -c -v --syslog`  

For help use:  
  `/home/pi/GoPro/main.py -h`  

With other options, one can test, if the raspi can connect to a (new) GoPro  
  `sudo /home/pi/GoPro/main.py -c -v --syslog`  
or without config file  
  `sudo /home/pi/GoPro/main.py -v --syslog -s new_gopro_ssid -p new_gopro_passwd`  

#### Logging

By default the gopro-controller just prints outs its log ouput. With the "--syslog" option, the log is written to the
systems log deamon too. To view all output use:`cat /var/log/syslog`  

If the gopro-controller is running in the background (using option "-b"), nothing is printed out or logged. Not until
the "--syslog" option is used!  
