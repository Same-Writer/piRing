
from rpi_ws281x import PixelStrip, Color
import sys, os, time, signal

def getHourAnimation(name):     #this might be unnecessarily overcomplicating things...
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

