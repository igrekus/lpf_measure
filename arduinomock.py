import serial
# from time import sleep


class ArduinoMock:
    def __init__(self, port="COM5", baudrate=115200, parity=serial.PARITY_NONE, bytesize=8, stopbits=serial.STOPBITS_ONE,
                         timeout=1):
        pass

    def disconnect(self):
        print("arduino mock: disconnect()")

    def set_lpf_code(self, command: str) -> bool:
        msg = command.encode("ascii")
        print("Arduino mock: set_lpf_code():", msg)
        return True

    def is_open(self):
        print("arduino mock: is_open()")
