import time
import neopixel
from machine import Pin, Timer

led = neopixel.NeoPixel(Pin(8), 1)
on = (0, 0, 255)
off = (0, 0, 0)

while True:
    led[0] = on
    led.write()
    time.sleep(1)
    led[0] = off
    led.write()
    time.sleep(1)
