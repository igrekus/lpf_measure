import serial
from PyQt5.QtCore import QObject, QModelIndex, pyqtSignal, QDate

from arduino import Arduino
from arduinomock import ArduinoMock
from obzor304 import Obzor304
from obzor304mock import Obzor304Mock

# MOCK
def_mock = True

class DomainModel(QObject):

    COMMAND = 'LPF,'
    OSC_ADDR = 'TCPIP::192.168.0.3::INSTR'
    MAXREG = 127

    measurementFinished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._arduino = None
        self._analyzer = None

        self._lastMeasurement = None

        # data, make separate stat_processor class
        self.cutoff_freq_x = list()
        self.cutoff_freq_y = list()
        self.cutoff_freq_delta_x = list()
        self.cutoff_freq_delta_y = list()

    def findInstruments(self):

        def find_available_ports():
            ports = [f'COM{i+1}' for i in range(256)]
            result = list()
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                except (OSError, serial.SerialException):
                    pass
            return result

        def find_arduino(ports: list):
            # MOCK
            if not def_mock:
                for port in ports:
                    s = serial.Serial(port=port, baudrate=115200, timeout=1)
                    if s.is_open:
                        s.write(bytes([0x23, 0x4E, 0x41, 0x4D, 0x45]))
                        while s.in_waiting == 0:
                            pass
                        ans = s.read_all()
                        if ans[:7] == 'ARDUINO'.encode('ascii'):
                            return port
                else:
                    return ''
            else:
                return 'COM5'


        print('Сканируем доступные порты.')
        available_ports = find_available_ports()
        print('Доступны: ' + ' '.join(available_ports))

        print('Ищем Arduino.')
        arduino_port = find_arduino(available_ports)

        if not arduino_port:
            print('Ошибка: Arduino не найден.')
            return False

        print('Подключаемся к Arduino: ' + arduino_port)

        # MOCK:
        if def_mock:
            self._arduino = ArduinoMock(port=arduino_port, baudrate=115200, parity=serial.PARITY_NONE, bytesize=8,
                                        stopbits=serial.STOPBITS_ONE, timeout=1)
        else:
            self._arduino = Arduino(port=arduino_port, baudrate=115200, parity=serial.PARITY_NONE, bytesize=8,
                                    stopbits=serial.STOPBITS_ONE, timeout=1)

        print('Подключаемся к анализатору: ' + self.OSC_ADDR)

        if def_mock:
            self._analyzer = Obzor304Mock(self.OSC_ADDR)
        else:
            try:
                self._analyzer = Obzor304(self.OSC_ADDR)
            except Exception as ex:
                print('Ошибка: нет подключения к анализатору: ' + str(ex))
                print('Проверьте найстройки анализатора: ')
                return False

        print('Анализатор:', str(self._analyzer))
        return True

    def measure(self):
        print('Начинаем измерения...')
        self._analyzer.init_instrument()

        regs = self.MAXREG + 1

        # MOCK:
        if def_mock:
            regs = 5

        for n in range(regs):
            cmd = self.COMMAND + str(n)
            print(f'\nИзмерение: code={str(n).zfill(3)}, bin={bin(n)}, command: {cmd}')
            if not self._arduino.set_lpf_code(cmd):
                print('Ошибка при записи регистра:', cmd)
                continue

            self._lastMeasurement = self._analyzer.measure(n)
            self.measurementFinished.emit()

        self._analyzer.finish()
        self._arduino.disconnect()
        print('Конец измерений.')

    @property
    def instrumentsReady(self):
        return bool(self._arduino) and bool(self._analyzer)
