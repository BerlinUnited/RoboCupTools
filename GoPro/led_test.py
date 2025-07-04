from gpiozero import LED
from time import sleep

red = LED(22)
green = LED(27)
blue = LED(17)

while True:
    red.on()
    blue.on()
    green.on()
    sleep(1)
    red.off()
    blue.off()
    green.off()
    sleep(1)