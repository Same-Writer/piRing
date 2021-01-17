# https://www.raspberrypi.org/documentation/usage/gpio/python/README.md
# https://www.raspberrypi.org/forums/viewtopic.php?t=202568

from gpiozero import Button
from time import sleep

switchUp = Button(2)
switchDown = Button(3)

while True:
    if switchUp.is_pressed:
        print("Switch In \tUP\t\t Position...")
    elif switchDown.is_pressed:
        print("Switch In \tDOWN\t\t Position...")
    else:
        print("Switch In \tNEUTRAL\t\t Position...")
    sleep(.5)


