#!/usr/bin/env python3

from rpi_ws281x import PixelStrip, Color
import time, signal
from datetime import datetime

from fastapi import FastAPI

import yaml

from animations import *

#################################################
### Constants to be used across script.
#################################################

#   https://flaviocopes.com/rgb-color-codes/

WHITE =         Color(127, 127, 127)
RED =           Color(255, 0, 0)
ORANGE =        Color(255, 69, 0)
GOLD =          Color(255, 215, 0)
GREEN =         Color(0, 255, 0)
BLUE =          Color(0, 0, 255)
LIGHT_BLUE =    Color(0, 191, 255)
MIDNIGHT_BLUE = Color(25, 25, 112)
INDIGO =        Color(75, 0, 130)
VOILET =        Color(238, 130, 238)
DARK_MAGENTA =  Color(139, 0, 139)
PINK =          Color(255, 20, 147)
BLACK =         Color(0, 0, 0)


#################################################
### Signal Handling
#################################################

def receiveSignal(signalNumber, frame):
    print('Received:', signalNumber)
    raise NameError('HiThere')


#################################################
### PixelRing class
#################################################

class PixelRing(PixelStrip):

    def __init__(self, num, pin, color0, color1, color2, color3, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None, gamma=None, rotation=0):
        super().__init__(num, pin, freq_hz, dma, invert, brightness, channel, strip_type, gamma)
        
        self.rotation = rotation

        self.color0 = color0        #seconds
        self.color1 = color1        #minute fill
        self.color2 = color2        #hour ticks
        self.color3 = color3        #current hour
    
    def clear(self):
        for i in range(self.numPixels()):
            self[i] = Color(0,0,0)

    # override the following to inlcude rotation:
    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
        """
        n = (n + self.rotation) % int(self.numPixels())
        self[n] = color
            
    # other methods that will need an override to include rotation, if used
    # def setPixelColorRGB(self, n, red, green, blue, white=0):
    # def getPixelColor(self, n):
    # def getPixelColorRGB(self, n):

#################################################
### State Machine functions
#################################################

def importSettings(filename):
    with open(filename, 'r') as file:
        settings = yaml.load(file, Loader=yaml.SafeLoader)
    return settings

def init():
    #check NTP connection, AP mode, etc
    pass

def main():
    
    DEBUG = True

    #parse arguments here (if any alowed)

    #params = read_settings() from yaml

    if DEBUG:
        print(help(PixelStrip))
        pass
    

    settings = importSettings("/home/zam/piRing/config/settings.yaml")
    # check if WIFI is configured and connected
    # ping NTP to confirm that's all good
    # if not, fall back to AP mode + static pattern / status LEDs

    try:
    
        strip = PixelRing(settings['LED_COUNT'], settings['LED_PIN'], settings['COLOR_0'],
                           settings['COLOR_1'], settings['COLOR_2'], settings['COLOR_3'], 
                           settings['LED_FREQ_HZ'], settings['LED_DMA'], settings['LED_INVERT'], 
                           settings['LED_BRIGHTNESS'], settings['LED_CHANNEL'], rotation=settings['ROTATION'])
        # strip = PixelRing(settings)

        strip.begin()

        #opening animation here
        rainbowCycle(strip, wait_ms=10, iterations=1)

        now = datetime.now()
        last = now

        #Clock startup:
        animateClockStartup(strip, now, 10)
    
        while True:
            #get current time here
            now = datetime.now()

            if DEBUG:
                current_time = now.strftime("%H:%M:%S")
                print("Time: ", current_time)    
            
            if last.hour < now.hour:
                hAnimation = "flavortown"
                hourChangeAnimation(strip, now, last, hAnimation)     
                pass
            elif last.minute < now.minute and now.minute % 15 == 0:
                mAnimaiton = "crisscross"
                minuteChangeAnimation(strip, now, last, mAnimaiton)
            elif last.minute < now.minute:
                mAnimaiton = "pong"
                minuteChangeAnimation(strip, now, last, mAnimaiton)

            drawClock(strip, now)
            strip.show()

            #check for stop condition /interrupt here
            time.sleep(.01)
            last = now

        #elif static:
            #static(params)
        #elif game:
        #    wheelOfFortune()

    except KeyboardInterrupt:
        colorWipe(strip, BLACK, 10, reversed=True) 


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, receiveSignal)
    main()