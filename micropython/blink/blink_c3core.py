import time
from machine import Pin, Timer

led = Pin(8, Pin.OUT)

while True:
    led.on()
    time.sleep(1)
    led.off()
    time.sleep(1)
