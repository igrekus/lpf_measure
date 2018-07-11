import serial
from arduino import Arduino


class ArduinoMock(Arduino):

    def __init__(self, port='COM5', baudrate=115200, parity=serial.PARITY_NONE, bytesize=8,
                 stopbits=serial.STOPBITS_ONE, timeout=1):
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._bytesize = bytesize
        self._stopbits = stopbits
        self._timeout = timeout

    def __str__(self):
        return f'Arduino at {self._port}'

    def set_lpf_code(self, command: str) -> bool:
        msg = command.encode('ascii')
        print('Arduino mock: set_lpf_code():', msg)
        return True

    def is_open(self):
        print('arduino mock: is_open()')
        return True

    def disconnect(self):
        print('Arduino mock: disconnect()')


