import sys

import serial
from os import listdir
from os.path import isfile, join, isdir, exists
from PyQt5.QtWidgets import QApplication
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar

from mainwindow import MainWindow
from arduino import Arduino
from obzor304 import Obzor304
import matplotlib

# TODO: begin with *CLS
# TODO: begin measure with SYSTem:REMote
# TODO: set trigger: TRIGger[:SEQuence]:SOURce {INTernal|EXTernal|MANual|BUS}

# TODO: auto-load instrument state: MMEMory:LOAD[:STATe] "<string>" (.sta)
# TODO: auto-load calibration data: MMEMory:LOAD:CKIT<Ck> "<string>" (.ckd)

# TODO: trigger measurement with *TRG, source is set with TRIG:SOUR)
# TODO: get end measure confirmation from analyzer (while OPC? )

# TODO: wait for cmd end on analyzer: *WAI (or "INIT: *OPC?")
#                               beep: SYSTem:BEEPer:COMPlete:IMMediate  -- test beep
#                          test beep: SYSTem:BEEPer:COMPlete:STATe {ON|OFF|1|0}
# TODO: read measures directly to the PC: SENSe<Ch>:FREQuency:DATA? (?)
# TODO: finish task with SYSTem:LOCal

# TODO: save png
# TODO: make config file (instr addresses)
# TODO: GUI stat analysis
# TODO: save settings and calibration from analyzer
# TODO: track measurement number, write successive measurements to a numbered forlder

# TODO: stimulate on one freq, measure x2 freq -> SENSe<Ch>:FREQuency[:CW] <frequency>
#                                                 SENSe<Ch>:FREQuency[:FIXed] <frequency>
#                                                 Стимул > Мощность > Фикс. частота

# sample program:

# !!!
# TODO: dupe files on a flash drive (MMEMory:MDIRectory <string> success = drive present?)

COMMAND = "LPF,"
OSC_ADDR = "TCPIP::192.168.0.3::INSTR"
MAXREG = 127

canvas11 = None
canvas12 = None
canvas22 = None
toolbar11 = None
toolbar12 = None
toolbar22 = None
cutoff_freq_x = list()
cutoff_freq_y = list()
cutoff_freq_delta_x = list()
cutoff_freq_delta_y = list()

def log(msg: str):
    print(msg)

def find_available_ports():
    """
        Lists serial port names
        :returns:
            A list of the serial ports available on the system
    """
    ports = ['COM%s' % (i + 1) for i in range(256)]
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def find_arduino(ports: list):
    for port in ports:
        s = serial.Serial(port=port, baudrate=115200, timeout=1)
        if s.is_open:
            s.write(bytes([0x23, 0x4E, 0x41, 0x4D, 0x45]))
            while s.in_waiting == 0:
                pass
            ans = s.read_all()
            if ans[:7] == "ARDUINO".encode("ascii"):
                return port

    return ""
    # return "COM5"


def measure():
    log("Сканируем доступные порты.")
    available_ports = find_available_ports()
    log("Доступны: " + " ".join(available_ports))

    log("Ищем Arduino.")
    arduino_port = find_arduino(available_ports)

    if not arduino_port:
        log("Ошибка: Arduino не найден.")
        return

    log("Подключаемся к Arduino: " + arduino_port)
    arduino = Arduino(port=arduino_port, baudrate=115200, parity=serial.PARITY_NONE, bytesize=8,
                      stopbits=serial.STOPBITS_ONE, timeout=1)

    log("Подключаемся к анализатору: " + OSC_ADDR)

    try:
        osc = Obzor304(OSC_ADDR)
    except Exception as ex:
        log("Ошибка: нет подключения к анализатору: " + str(ex))
        log("Проверьте найстройки анализатора: ")
        return
    log("Анализатор: " + str(osc))

    osc.init_instrument()

    log("Начинаем измерения...")
    for n in range(MAXREG + 1):
        cmd = COMMAND + str(n)
        log("\nИзмерение: code=" + str(n).zfill(3) + ", bin=" + bin(n) + ", command: " + cmd)
        if not arduino.set_lpf_code(cmd):
            log("Ошибка при записи регистра: " + cmd)
            continue

        osc.measure(n)

    arduino.disconnect()


def process_stats(work_dir: str, cutoff_mag=-6):

    def get_file_list(data_path):
        return [l for l in listdir(data_path) if isfile(join(data_path, l)) and ".s2p" in l]

    def parse_files(data_path):
        freq = list()
        amp = list()
        for s2p in s2p_files:
            with open(data_path + s2p) as f:
                lines = f.readlines()[5:]
                freq_data = list()
                amp_data = list()
                for l in lines:
                    # print(round(float(l.replace(",", ".").split()[0]) / MHz, 15))
                    floats = [round(float(s), 15) for s in l.split()]
                    freq_data.append(floats[0] / MHz)
                    amp_data.append(floats[3])
            freq.append(freq_data)
            amp.append(amp_data)
        # print("freqs2", freq[2])
        # print("freqs3", freq[3])
        # print("freqs4", freq[4])
        #
        # print("amp2", amp[2])
        # print("amp3", amp[3])
        # print("amp4", amp[4])
        return freq, amp

    def calc_cutoff_freq(cutoff_magnitude):
        l = list()
        for a, f in zip(amp, freq):
            l.append(f[a.index(min(a, key=lambda x: abs(cutoff_magnitude - x)))])
        return l

    def calc_cutoff_freq_delta():
        l = list()
        for i in range(len(cutoff_freq_y[:-2])):
            d = abs(cutoff_freq_y[i + 1] - cutoff_freq_y[i])
            l.append(d)
        return l

    MHz = float(1000000)
    GHz = float(1000000000)

    if not exists(work_dir) or not isdir(work_dir):
        print("Ощибка: директория", work_dir, "не найдена.")
        return

    if work_dir[:-1] != "\\":
        work_dir += "\\"

    print("Скаируем директорию", work_dir)
    s2p_files = get_file_list(work_dir)
    if not s2p_files:
        input("Ошибка: S2P файлы в заданной директории не найдены.\nЕажмите Enter для завершения работы...")
        sys.exit(1)
    else:
        print("Найдено", len(s2p_files), "файлов.")

    print("Извлекаем данные.")
    freq, amp = parse_files(work_dir)

    print("Ищем частоту среза.")
    global cutoff_freq_x
    global cutoff_freq_y
    cutoff_freq_y = calc_cutoff_freq(cutoff_mag)
    cutoff_freq_x = range(len(cutoff_freq_y))

    global cutoff_freq_delta_x
    global cutoff_freq_delta_y
    print("Ищем дельту.")
    cutoff_freq_delta_y = calc_cutoff_freq_delta()
    cutoff_freq_delta_x = range(len(cutoff_freq_delta_y))

    print("Строим графики.")
    matplotlib.use('Qt5Agg', warn=False, force=True)

    plt.figure(num=1)
    for f, a in zip(freq, amp):
        plt.plot(f, a, color="0.4")

    plt.subplots_adjust(bottom=0.150)
    plt.axhline(cutoff_mag, 0, 1, linewidth=0.8, color="0.3", linestyle="--")
    plt.yticks(list(plt.yticks()[0]) + [cutoff_mag])
    plt.title("Коэффициент преобразования")
    plt.xscale("log")
    plt.xlabel("F, МГц")
    plt.ylabel("К-т пр., дБ")
    plt.ylim([-60, 10])
    plt.grid(b=True, which="minor", color="0.7", linestyle='--')
    plt.grid(b=True, which="major", color="0.5", linestyle='-')

    plt.figure(2)
    plt.subplots_adjust(bottom=0.150)
    plt.plot(cutoff_freq_x, cutoff_freq_y, color="0.4")
    plt.title("Частота среза по уровню " + str(cutoff_mag) + " дБ")
    plt.xlabel("Код")
    plt.ylabel("F, МГц")
    plt.yscale("log")
    plt.grid(b=True, which="minor", color="0.7", linestyle='--')
    plt.grid(b=True, which="major", color="0.5", linestyle='-')

    plt.figure(3)
    plt.subplots_adjust(bottom=0.150)
    plt.plot(cutoff_freq_delta_x, cutoff_freq_delta_y, color="0.4")
    plt.title("Дельта частоты среза")
    plt.xlabel("Код")
    plt.ylabel("dF, МГц")
    plt.grid(True)

    figure11 = plt.figure(1)
    figure12 = plt.figure(2)
    figure22 = plt.figure(3)

    global canvas11
    canvas11 = FigureCanvas(figure11)
    global canvas12
    canvas12 = FigureCanvas(figure12)
    global canvas22
    canvas22 = FigureCanvas(figure22)

    global toolbar11
    toolbar11 = NavToolbar(canvas=canvas11, parent=None)
    global toolbar12
    toolbar12 = NavToolbar(canvas=canvas12, parent=None)
    global toolbar22
    toolbar22 = NavToolbar(canvas=canvas22, parent=None)

    # plt.show()

    # print("Сохраняем графики в файл.")
    # plt.savefig("plots.png", dpi=300)
    #
    # print("Выводим графики на экран.")
    # plt.show()

def usage():
    print("\nИспользование: lpt_measure.exe <command>\n\n"
          "    Команды:\n\n"
          "    /measure                     - начать процесс измерений (при наличии подключения к контроллеру Arduino и спектроанализатору OBZOR 304\n"
          "    /stats <dir>                 - провести статобработку .s2p файлов в <dir>\n"
          "    /stats <dir> /cutoff <mag>   - провести статобработку .s2p файлов в <dir> используя <mag> в качестве уровня для поиска частоты среза")

def start_gui(canvas11, canvas12, canvas22, cutoff_freq_x, cutoff_freq_y, cutoff_freq_delta_x, cutoff_freq_delta_y):
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.ui.vlChart11.addWidget(canvas11)
    window.ui.vlChart11.addWidget(canvas11.toolbar)

    window.ui.vlChart12.addWidget(canvas12)
    window.ui.vlChart12.addWidget(canvas12.toolbar)

    window.ui.vlChart22.addWidget(canvas22)
    window.ui.vlChart22.addWidget(canvas22.toolbar)

    window.cutoff_freq_x = cutoff_freq_x
    window.cutoff_freq_y = cutoff_freq_y
    window.cutoff_freq_delta_x = cutoff_freq_delta_x
    window.cutoff_freq_delta_y = cutoff_freq_delta_y

    sys.exit(app.exec_())

def main(args):
    if len(args) > 1:
        if args[1] == "/stats":
            if len(args) == 3:
                process_stats(args[2], -6)
                start_gui(canvas11=canvas11, canvas12=canvas12, canvas22=canvas22,
                          cutoff_freq_x=cutoff_freq_x,
                          cutoff_freq_y=cutoff_freq_y,
                          cutoff_freq_delta_x=cutoff_freq_delta_x,
                          cutoff_freq_delta_y=cutoff_freq_delta_y)
            elif len(args) == 5 and args[3] == "/cutoff":
                process_stats(args[2], int(args[4]))
                start_gui(canvas11=canvas11, canvas12=canvas12, canvas22=canvas22,
                          cutoff_freq_x=cutoff_freq_x,
                          cutoff_freq_y=cutoff_freq_y,
                          cutoff_freq_delta_x=cutoff_freq_delta_x,
                          cutoff_freq_delta_y=cutoff_freq_delta_y)
            else:
                usage()
        if args[1] == "/measure":
            measure()
    else:
        usage()

if __name__ == '__main__':
    main(sys.argv)
    # import visa
    # rm = visa.ResourceManager()
    # inst = rm.open_resource(OSC_ADDR)
    # print(inst.query("*IDN?\n"))
    #
    # inst.write(":TRIG:SOUR external\n")
    # inst.write(":TRIG:SING\n")
    # # inst.write("init1\n")
    # while not inst.query("*OPC?\n"):
    #     print("waiting")
    #
    # print("done measure")
    #
    # inst.write(":TRIG:SOUR internal")
    # inst.write("SYSTEM:LOCAL\n")



    # //
    # // Trigger measurement and wait for completion
    # //
    # viPrintf(instr, ":TRIG:SOUR BUS\n");
    # viPrintf(instr, ":TRIG:SING\n");
    # viQueryf(instr, "*OPC?\n", "%d", &temp);
    # //

    # // Read out measurement data
    # //
    # retCount = maxCnt * 2;
    # viQueryf(instr, "CALC:DATA:FDAT?\n", "%,#lf", &retCount, Data);
    # retCount = maxCnt;
    # viQueryf(instr, "SENS:FREQ:DATA?\n", "%,#lf", &retCount, Freq);

    # main(sys.argv)
    # input("\nНажмите Enter для завершения работы.")

    # import visa
    #
    # rm = visa.ResourceManager()
    # print(rm.list_resources())
    #
    # inst = rm.open_resource("USB0::0x4348::0x5537::NI-VISA-10002::RAW")
    #
    # # # # [SOURce[1|2]:]APPLy:<function> [<freq>[,<amp>[,<offset>]]]
    # # # ep_command.write("SOURce1:APPLy:SIN 10kHz\n".encode("ascii"))
    # # # # [SOURce[1|2]:]PHASe <value>[deg]
    # # # ep_command.write("SOURce1:PHASe 33deg\n".encode("ascii"))
    # # # # [OUTPut[1|2]:]LOAD <value>[Ohm]
    # # # ep_command.write("OUTPut1:LOAD 50Ohm\n".encode("ascii"))
    # # # # [SOURce[1|2]:]FREQuency <value>[unit]
    # # # ep_command.write("SOURce1:FREQuency 50kHz\n".encode("ascii"))
    # #
    # print("cls", inst.write("*CLS\n"))
    #
    # print("load", inst.write("OUTPut1:LOAD 50Ohm\n"))
    # print("load", inst.write("OUTPut2:LOAD 50Ohm\n"))
    # #
    # # print("sin", inst.write("SOURce1:APPLy:SINusoid 10kHz\n"))
    # # print("sin", inst.write("SOURce2:APPLy:SINusoid 10kHz\n"))
    # # print("volt", inst.write('SOURce1:VOLTage 10mV'))
    # # print("volt", inst.write('SOURce2:VOLTage 10mV'))
    # #
    # # print("offs", inst.write("SOURce1:VOLTage:OFFSet 0V\n"))
    # # print("offs", inst.write("SOURce2:VOLTage:OFFSet 0V\n"))
    #
    # # print("volt", inst.write('SOURce1:VOLTage 3dBm'))
    # # print("volt", inst.write('SOURce2:VOLTage 3dBm'))
    #
    # print("cls", inst.write("*CLS\n"))
    # print("local", inst.write("SYSTem:LOCal\n"))
