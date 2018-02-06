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
        self.set_active_window(1)
        self.make_data_dir()
        self.set_touchstone_file_type(TOUCHSTONE_S2P)

    def set_touchstone_file_type(self, ftype: str):
        # print("OBZOR-304: устанавливаем тип выходного файла", self._inst.write("MMEM:STOR:SNP:TYPE:" + ftype + " 1,2"),
        #       "| file_type=" + ftype)
        print("OBZOR-304: устанавливаем тип выходного файла", self._inst.write("MMEM:STOR:SNP:TYPE:" + ftype),
              "| file_type=" + ftype)

    def set_active_window(self, num: int):
        print("OBZOR-304: устанавливаем активное окно:", self._inst.write("DISP:WIND" + str(num) + ":ACT"))

    def make_data_dir(self):
        self._folder = r'C:\!meas\LPF_' + datetime.date.today().isoformat()
        print("OBZOR-304: создаём папку для сохранения результатов измерений:",
              self._inst.write("MMEM:MDIR " + '"' + self._folder + '"'), "| dir=", self._folder)

    def measure(self, n: int):
        meas_file_name = self._folder + "\\" + "lpf_" + str(n).zfill(3) + ".s2p"
        print("OBZOR-304: запускаем измерение:", self._inst.write("INIT1"))
        # TODO: get confirmation for measurement end
        sleep(1.5)
        # freqs = planar.query("SENS:FREQ:DATA?")
        # amps = planar.query("CALC1:DATA:FDAT?")
        # print("freqs:", freqs.count(",") + 1, freqs)
        # print("amp:", amps.count(",") + 1, amps)
        print("OBZOR-304: сохраняем результат измерений: ",
              self._inst.write("MMEM:STOR:SNP " + '"' + meas_file_name + '"'), "\nФайл:", meas_file_name)
