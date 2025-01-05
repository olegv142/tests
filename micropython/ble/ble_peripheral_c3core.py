import bluetooth
import struct
import time
import machine
import ubinascii
from ble_advertising import advertising_payload
from micropython import const
from machine import Pin
from machine import WDT

# https://github.com/micropython/micropython/blob/master/examples/bluetooth

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NORESP = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

_SERVICE_UUID = bluetooth.UUID(0xFFE0)
_CHAR = (
    bluetooth.UUID(0xFFE1),
    _FLAG_READ | _FLAG_WRITE_NORESP | _FLAG_WRITE | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_SERVICE = (
    _SERVICE_UUID,
    (_CHAR,),
)

class BLEPeripheral:
    def __init__(self, ble, name="mpy-uart"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_SERVICE_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback

def test():
    ble = bluetooth.BLE()
    p = BLEPeripheral(ble)
    p.on_write(lambda v: print("rx: ", v))
    led = Pin(8, Pin.OUT)
    led_on = False
    wdt = WDT(timeout=10000)
    counter = 0
    while True:
        p.send('#%d' % counter)
        if p.is_connected():
            led.off()
            led_on = False
        elif not (counter % 4):
            led_on = not led_on
            led(led_on)
        wdt.feed()
        time.sleep_ms(100)
        counter += 1

if __name__ == "__main__":
    test()
