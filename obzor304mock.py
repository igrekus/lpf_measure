import datetime

from obzor304 import Obzor304

TOUCHSTONE_S2P = "S2P"


class Obzor304Mock(Obzor304):

    def __init__(self, address: str):
        self._address = address
        self._idn = 'OBZOR 304 IDN'
        self._folder = ""

    def send(self, command):
        print('Obzor304 mock:', command)
        return 'success'

    def measure(self, n: int):
        meas_file_name = self._folder + f'\\lpf_{str(n).zfill(3)}.s2p'
        print('\nOBZOR-304: запускаем измерение:', self.send('INIT1; *OPC?'))

        freqs = self.query('SENS:FREQ:DATA?')
        amps = self.query('CALC1:DATA:FDAT?')

        freqs = '300000,400000,500000,600000,700000'
        amps = '10,5,0,-10,-40'
        print('freqs:', freqs.count(',') + 1, freqs)
        print('amp:', amps.count(',') + 1, amps)

        print('OBZOR-304: сохраняем результат измерений: ',
              self.send(f'MMEM:STOR:SNP "{meas_file_name}"'), f'\nФайл:{meas_file_name}')
        return freqs, amps

    def query(self, question):
        print('Obzor304 mock', question)
        return 'success'
