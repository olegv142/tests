from machine import Pin, Timer

led = Pin(8, Pin.OUT)
tim = Timer(1)
cnt = 0
def tick(timer):
    global cnt
    cnt += 1
    led(cnt % 2)

tim.init(period=1000, mode=Timer.PERIODIC, callback=tick)

while True:
    pass
