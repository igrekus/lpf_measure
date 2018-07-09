import datetime
import visa
from time import sleep

TOUCHSTONE_S2P = "S2P"


class Obzor304:
    def __init__(self, address: str):
        # TODO: move resource manager out of this class
        self._rm = visa.ResourceManager()
        self._inst = self._rm.open_resource(address)
        self._idn = self._inst.query("*IDN?")
        self._folder = ""

    def __str__(self):
        return self._idn

    def init_instrument(self):
        # self.reset_instrument()
        self.set_active_window(1)
        self.make_data_dir()
        self.set_touchstone_file_type(TOUCHSTONE_S2P)
        self.set_trigger_source("INT")

    def set_touchstone_file_type(self, ftype: str):
        # print("OBZOR-304: устанавливаем тип выходного файла", self._inst.write("MMEM:STOR:SNP:TYPE:" + ftype + " 1,2"),
        #       "| file_type=" + ftype)
        print("OBZOR-304: устанавливаем тип выходного файла", self._inst.write("MMEM:STOR:SNP:TYPE:" + ftype),
              "| file_type=" + ftype)

    def set_active_window(self, num: int):
        print("OBZOR-304: устанавливаем активное окно:", self._inst.write("DISP:WIND" + str(num) + ":ACT"))

    def set_trigger_source(self, source: str):
        print("OBZOR-304: устанавливаем источник триггер-сигнала:", self._inst.write("TRIG:SOUR " + source))

    def make_data_dir(self):
        self._folder = r'C:\!meas\LPF_' + datetime.date.today().isoformat()
        print("OBZOR-304: создаём папку для сохранения результатов измерений:",
              self._inst.write("MMEM:MDIR " + '"' + self._folder + '"'), "| dir=", self._folder)

    def reset_instrument(self):
        print(self._inst.write("*CLS"))

    def measure(self, n: int):
        meas_file_name = self._folder + "\\" + "lpf_" + str(n).zfill(3) + ".s2p"
        print("OBZOR-304: запускаем измерение:", self._inst.write("INIT1; *OPC?"))

        # FIXME: detector doesn't work
        # print("OBZOR-304: запускаем измерение:", self._inst.write("TRIGger:SEQuence:SINGle"))
        # TODO: get confirmation for measurement end
        # print(self._inst.query("*OPC?"))
        # while self._inst.query("*OPC?") != '1':
        #     print("waiting")

        sleep(1.5)
        freqs = self._inst.query("SENS:FREQ:DATA?")
        amps = self._inst.query("CALC1:DATA:FDAT?")
        # print("freqs:", freqs.count(",") + 1, freqs)
        # print("amp:", amps.count(",") + 1, amps)
        print("OBZOR-304: сохраняем результат измерений: ",
              self._inst.write("MMEM:STOR:SNP " + '"' + meas_file_name + '"'), "\nФайл:", meas_file_name)
        return freqs, amps

    def finish(self):
        print("OBZOR-304: выключаем непрерывную подачу триггер-сигнала:", self._inst.write("INITiate1:CONTinuous OFF"))
        self.set_trigger_source("INT")
