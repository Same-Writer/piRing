#!/usr/bin/env python3

from rpi_ws281x import PixelStrip, Color
import sys, os, time, signal
from datetime import datetime
from gpiozero import Button
from time import sleep

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
#ALL_COLORS = []

def getHourAnimation(name):     # TODO: this might be unnecessarily overcomplicating things...
    hourAnimations = {
        "ping":         1,
        "pong":         2,
        "crisscross":   3,
        "rollback":     4,
        "RGB":          5,
        "flavortown":   6,
        }
    return hourAnimations.get(name, 3)

def getMinuteAnimation(name):
    hourAnimations = {
        "ping":         1,
        "pong":         2,
        "crisscross":   3,
        "RGB":          4
        }
    return hourAnimations.get(name, 1)


#################################################
### PixelRing class
#################################################

class PixelRing(PixelStrip):

    def __init__(self, num, pin, color0, color1, color2, color3, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None, gamma=None, rotation=0):
        super().__init__(num, pin, freq_hz, dma, invert, brightness, channel, strip_type, gamma)
        
        # Program-exit signal handling
        signal.signal(signal.SIGTERM, self.clearandexit)
        self.exitnow = False        #property to allow main loop to exit with a SIGTERM from another program

        self.rotation = rotation

        self.color0 = color0        #seconds
        self.color1 = color1        #minute fill
        self.color2 = color2        #hour ticks
        self.color3 = color3        #current hour
    
    def clear(self):
        for i in range(self.numPixels()):
            self._led_data[i] = Color(0,0,0)

    def clearandexit(self, signum, frame):
        #self.clear()
        #self.show()
        self.exitnow = True

    # override the follwoing to inlcude rotation:
    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
        """
        n = (n + self.rotation) % int(self.numPixels())
        self._led_data[n] = color
            
    # other methods that will need an override to include rotation, if used
    # def setPixelColorRGB(self, n, red, green, blue, white=0):
    # def getPixelColor(self, n):
    # def getPixelColorRGB(self, n):

#################################################
### Pixel fill functions
#################################################

def colorWipe(strip, color, wait_ms=10, reversed=False, start=None, stop=None):
    
    #by default, sweep full strip
    if start == None:
        start = 0
    if stop == None:
        stop = strip.numPixels()

    # Wipe color across display a pixel at a time
    if not reversed:
        for i, j in enumerate(range(start,stop)):
            strip.setPixelColor(j, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
    else:
        for i, j in enumerate(range(start,stop)):
            strip.setPixelColor(stop-i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

def colorFill(strip, color, start=None, stop=None):
    if start == None:
        start = 0
    if stop == None:
        stop = strip.numPixels()

    for i in range(start, stop):
        strip.setPixelColor(i, color)

#################################################
### "Static" Animations
#################################################

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def rainbowCycle(strip, wait_ms=10, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(strip.numPixels() - (i + 1), wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

#################################################
### Clock-specific animations
#################################################

def animateClockStartup(strip, now, wait_ms):
    strip.clear()
    colorWipe(strip, strip.color1, wait_ms)

    for i, j in enumerate(range(now.minute, strip.numPixels())):
        strip.clear()
        drawHourTicks(strip, strip.color2)
        colorFill(strip, strip.color1, start=0, stop=int(strip.numPixels())-i)
        strip.show()
        time.sleep(wait_ms/1000.0)        

#################################################
### Clock-specific functions
#################################################

def drawClock(strip, now):
    
    #clear display first
    strip.clear()

    drawMinute(strip, now, strip.color1, fill=True)
    
    drawHourTicks(strip, strip.color2)

    drawHour(strip, now, strip.color3)

    if abs((now.hour % 12) * strip.numPixels() / 12 - now.minute) <= 1:
        #draw minute over the 3-wide hour
        drawMinute(strip, now, strip.color1, fill=False)

    #update second
    strip.setPixelColor(now.second, strip.color0)

    return 0

def drawHourTicks(strip, color):
    #update hour ticks
    for k in range(0, strip.numPixels(), int(strip.numPixels()/12)):
        strip.setPixelColor(k, color)

def drawHour(strip, now, color):

    #update current hour
    hour = now.hour % 12
    hour_pixel = hour * 5

    if hour_pixel - 1 < 0:  
        strip.setPixelColor(hour_pixel + 59, color)
    else:
        strip.setPixelColor(hour_pixel - 1, color)

    strip.setPixelColor(hour_pixel, color)
    strip.setPixelColor(hour_pixel + 1, color)

    pass

def drawMinute(strip, now, color, fill=None):
    
    if fill == None:
        fill = True
    
    if fill == True:
        for j in range(now.minute+1):
            strip.setPixelColor(j, strip.color1)
    else:
        strip.setPixelColor(now.minute, strip.color1)

    pass

def hourChangeAnimation(strip, now, last, animation):
    case = getHourAnimation(animation)
    if case == 1:
        #ping
        for i in len(strip.numPixels()):
            drawClock(strip, now)
            strip.setPixelColor(i, strip.color1)
            strip.show()
            time.sleep(.01)
        pass
    elif case == 2:
        #pong
        for i in len(strip.numPixels()):
            drawClock(strip, last)
            strip.setPixelColor(strip.numPixels() - i, strip.color1)
            strip.show()
            time.sleep(.01)
        pass
    elif case == 3:
        #crisscross
        pass
    elif case == 4:
        #rollback
        pass
    elif case == 5:
        #RGB
        pass
    elif case == 6:
        #flavortown
        colorWipe(strip, BLACK, reversed=True)  #wipe-erase strip
        drawHourTicks(strip, strip.color2)      
        strip.show()                            #draw hour ticks
        for j in range(256 * 1):
            for i in range(strip.numPixels()):
                drawHour(strip, now, wheel((i + j) & 255))      #draw next hour & rainbow flow those 3 LEDs
            strip.show()
            time.sleep(10 / 1000.0)

    pass

def minuteChangeAnimation(strip, now, last, animation):

    case = getMinuteAnimation(animation)

    if case == 1:
        # ping
        # CW from 0 to 60, second color

        length = strip.numPixels() + 1

        for i in range(length):
            drawClock(strip, now)
            strip.setPixelColor(i, strip.color0)
            strip.show()
            time.sleep(1 / length)
        pass
    elif case == 2:
        # pong
        # CCW from 60 to next minute, minute color

        length = strip.numPixels() - (now.minute + 1)

        for i in range(length):
            drawClock(strip, last)
            strip.setPixelColor(strip.numPixels() - i, strip.color1)
            strip.show()
            time.sleep(1 / length)
        pass
    elif case == 3:
        #crisscross
        length = strip.numPixels()

        for i in range(length):
            drawClock(strip, now)
            strip.setPixelColor(i, strip.color0)
            strip.setPixelColor(length - i, strip.color0)
            strip.show()
            time.sleep(1 / length)
        pass
    elif case == 4:
        #rollback
        pass
    elif case == 5:
        #RGB
        pass
    pass

#################################################
### State Machine functions
#################################################

def importSettings():
    #import settings from YAML file
    #return session settings and write props to strip init
    return 1

def init():
    #check NTP connection, AP mode, etc
    pass

def main():
    
    DEBUG = False

    # TODO: parse arguments here (if any alowed)

    # TODO: params = read_settings() from yaml

    if DEBUG:
        #print(help(PixelStrip))
        pass
    
    # Default LED strip configuration:
    # TODO: any parameters that for sure don't need to be changed by settings can be defaulted in the constructor and removed from main()
    
    LED_COUNT = 60        # Number of LED pixels.
    LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10          # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 200  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    ROTATION = 52

    # GPIO-read Switch Position
    switchUp = Button(2)
    switchDown = Button(3)
    currentPos = -1         # flag used to detect switch position changes

    # TODO: replace with file i/o
    COLOR_0 = RED                   #seconds
    COLOR_1 = GOLD                  #minute fill
    COLOR_2 = LIGHT_BLUE            #hour ticks
    COLOR_3 = DARK_MAGENTA          #current hour

    # TODO: check if WIFI is configured and connected
    # TODO: ping NTP to confirm that's all good
    # TODO: if not, fall back to AP mode + static pattern / status LEDs

    try:
        # get the strip initialized with parameters from above. 
        strip = PixelRing(LED_COUNT, LED_PIN, COLOR_0, COLOR_1, COLOR_2, COLOR_3, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, rotation=ROTATION)
        strip.begin()

        # main loop containing core functionality
        while not strip.exitnow:
            if switchUp.is_pressed: # check if switch state is UP
                
                if currentPos != 1: # only execute once on switch position change
                    currentPos = 1

                rainbow(strip, wait_ms=10, iterations=1)

            elif switchDown.is_pressed: # check if switch state is DOWN
                now = datetime.now()
                last = now

                #Clock startup:
                if currentPos != 2: # only execute once on switch position change
                    animateClockStartup(strip, now, 10)
                    currentPos = 2

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

                # TODO: check for stop condition/interrupt here
                last = now

            else: #switch state is NEUTRAL (or no switch is present)
                if currentPos != 3:
                    colorWipe(strip, BLACK, 10, reversed=True) 
                    currentPos = 3
                else:
                    time.sleep(.1)

            time.sleep(.01)

        colorWipe(strip, BLACK, 10, reversed=True)

    except KeyboardInterrupt:
        colorWipe(strip, BLACK, 10, reversed=True) 
    except NameError:
        print('An exception flew by!')
        raise


if __name__ == "__main__":
    main()