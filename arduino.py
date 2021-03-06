from time import sleep

import serial
# from time import sleep


class Arduino:

    def __init__(self, port='COM5', baudrate=115200, parity=serial.PARITY_NONE, bytesize=8, stopbits=serial.STOPBITS_ONE,
                         timeout=1):

        self._port = serial.Serial(port=port, baudrate=baudrate, parity=parity, bytesize=bytesize, stopbits=stopbits,
                                   timeout=timeout)

    def __str__(self):
        return f'Arduino at {self._port.port}'

    def disconnect(self):
        print('Arduino: disconnect()')
        self._port.close()

    def set_lpf_code(self, command: str) -> bool:
        msg = command.encode('ascii')
        print('Arduino: send:', msg)

        self._port.write(msg)

        sleep(2)
        print('Arduino: response:', self._port.read_until('\n'))
        # sleep(0.5)
        return True

    def is_open(self):
        return self._port.is_open
