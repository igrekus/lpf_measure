import serial
from PyQt5.QtCore import QObject, QModelIndex, pyqtSignal, QDate

from arduino import Arduino
from arduinomock import ArduinoMock
from obzor304 import Obzor304
from obzor304mock import Obzor304Mock

# MOCK
def_mock = True


class MeasureContext:

    def __init__(self, model):
        self._model = model

    def __enter__(self):
        print('Начинаем измерения...')
        self._model._analyzer.init_instrument()

    def __exit__(self, *args):
        self._model._analyzer.finish()
        # self._model._arduino.disconnect()
        print('Конец измерений.')


class DomainModel(QObject):

    COMMAND = 'LPF,'
    OSC_ADDR = 'TCPIP::192.168.0.3::INSTR'
    MAXREG = 127

    dataPointMeasured = pyqtSignal()
    measurementFinished = pyqtSignal()
    harmonicMeasured = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._arduino = None
        self._analyzer = None

        self._lastMeasurement = None

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

    def measureCode(self, harmonic=1, code=0):
        cmd = self.COMMAND + str(code)
        print(f'\nИзмерение: code={str(code).zfill(3)}, bin={bin(code)}, command: {cmd}')
        if not self._arduino.set_lpf_code(cmd):
            print('Ошибка при записи регистра:', cmd)
            return

        self._lastMeasurement = self._analyzer.measure(code)
        self.dataPointMeasured.emit()

    def measure(self):
        regs = self.MAXREG + 1
        # MOCK
        if def_mock:
            regs = 5

        with MeasureContext(self):
            for code in range(regs):
                self.measureCode(code=code)

        self._arduino.disconnect()
        self.measurementFinished.emit()

    def measureHarmonic(self, harmonic, code):
        print(f'Измеряем {harmonic} гармонику для code={code}...')
        print(self._arduino.is_open())
        try:
            with MeasureContext(self):
                self.measureCode(harmonic=harmonic, code=code)
        except Exception as ex:
            print(ex)

        # self._arduino.disconnect()
        self.harmonicMeasured.emit()

    @property
    def instrumentsReady(self):
        return bool(self._arduino) and bool(self._analyzer)

