import sys
import serial
import xlsxwriter
from os import listdir
from os.path import isfile, join, isdir, exists
from PyQt5.QtWidgets import QApplication
from matplotlib import pyplot as plt
from mainwindow import MainWindow
# from time import sleep
from arduino import Arduino
from obzor304 import Obzor304
import matplotlib

COMMAND = "LPF,"
OSC_ADDR = "TCPIP::192.168.0.3::INSTR"
MAXREG = 127

def log(msg: str):
    print(msg)

def find_available_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    # ports = ['COM%s' % (i + 1) for i in range(256)]
    ports = ['COM%s' % (i + 1) for i in range(10)]
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

def process_stats(work_dir: str):

    def get_file_list(data_path):
        return [l for l in listdir(data_path) if isfile(join(data_path, l)) and ".s2p" in l]

    def parse_files(data_path):
        freq = list()
        amp = list()
        for s2p in s2p_files:
            freq_data = list()
            amp_data = list()
            with open(data_path + s2p) as f:
                lines = f.readlines()[5:]
                for l in lines:
                    floats = [float(s) for s in l.replace(",", ".").split()]
                    freq_data.append(floats[0] / MHz)
                    amp_data.append(floats[3])
            freq.append(freq_data)
            amp.append(amp_data)
        return freq, amp

    def calc_cutoff_freq():
        l = list()
        for a, f in zip(amp, freq):
            l.append(f[a.index(min(a, key=lambda x: abs(-6 - x)))])
        return l

    def calc_cutoff_freq_delta():
        l = list()
        for i in range(len(cutoff_freq_y[:-1])):
            d = abs(cutoff_freq_y[i + 1] - cutoff_freq_y[i])
            l.append(d)
        return l

    def export_to_xlsx(cutoff_x, cutoff_y, delta_x, delta_y):

        def write_file(name, a1, b1, xlist, ylist):
            wb = xlsxwriter.Workbook(name)
            ws = wb.add_worksheet("Sheet1")

            ws.write("A1", a1)
            ws.write("B1", b1)

            start_row = 0
            row = 0
            for x, y in zip(xlist, ylist):
                row += 1
                ws.write(start_row + row, 0, x)
                ws.write(start_row + row, 1, y)

            chart = wb.add_chart({"type": "scatter",
                                  "subtype": "smooth"})
            chart.add_series({"name": "Sheet1!$B$1",
                              "categories": "=Sheet1!$A$2:$A$" + str(row + 1),
                              "values": "=Sheet1!$B$2:$B$" + str(row + 1)})
            chart.set_x_axis({"name": a1})
            chart.set_y_axis({"name": b1})
            ws.insert_chart("D3", chart)

            wb.close()

        cutoff_file_name = "cutoff_freq.xlsx"
        delta_file_name = "cutoff_delta.xlsx"

        write_file(cutoff_file_name, "Код", "Частота среза", cutoff_x, cutoff_y)
        write_file(delta_file_name, "Код", "Дельта", delta_x, delta_y)

    MHz = 1000000

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
    cutoff_freq_y = calc_cutoff_freq()
    cutoff_freq_x = range(len(cutoff_freq_y))

    print("Ищем дельту.")
    cutoff_freq_delta_y = calc_cutoff_freq_delta()
    cutoff_freq_delta_x = range(len(cutoff_freq_delta_y))

    print("Пишем .xlsx файлы.")
    export_to_xlsx(cutoff_freq_x, cutoff_freq_y, cutoff_freq_delta_x, cutoff_freq_delta_y)

    print("Строим графики.")
    matplotlib.use('TkAgg', warn=False, force=True)
    plt.subplots_adjust(left=0.06, bottom=0.1, right=0.98, top=0.95, hspace=0.4, wspace=0.2)

    plt.subplot(221)
    for f, a in zip(freq, amp):
        plt.plot(f, a, color="0.4")

    plt.axhline(-6, 0, 1, linewidth=0.8, color="0.3", linestyle="--")
    plt.yticks(list(plt.yticks()[0]) + [-6])
    plt.title("Коэффициент преобразования")
    plt.xscale("log")
    plt.xlabel("F, МГц")
    plt.ylabel("К-т пр., дБ")
    plt.ylim([-60, 10])
    plt.grid(b=True, which="minor", color="0.7", linestyle='--')
    plt.grid(b=True, which="major", color="0.5", linestyle='-')

    plt.subplot(222)
    plt.plot(cutoff_freq_x, cutoff_freq_y, color="0.4")
    plt.title("Частота среза")
    plt.xlabel("Код")
    plt.ylabel("F, МГц")
    plt.yscale("log")
    plt.grid(b=True, which="minor", color="0.7", linestyle='--')
    plt.grid(b=True, which="major", color="0.5", linestyle='-')

    plt.subplot(224)
    plt.plot(cutoff_freq_delta_x, cutoff_freq_delta_y, color="0.4")
    plt.title("Дельта частоты среза")
    plt.xlabel("Код")
    plt.ylabel("dF, МГц")
    plt.grid(True)

    print("Сохраняем графики в файл.")
    plt.savefig("plots.png", dpi=300)

    print("Выводим графики на экран.")
    plt.show()

def usage():
    print("\nИспользование: lpt_measure.exe <command>\n\n"
          "    Команды:\n\n"
          "    /measure          - начать процесс измерений (при наличии подключения к контроллеру Arduino и "
          "спектроанализатору OBZOR 304\n"
          "    /stats <dir>      - провести статобработку .s2p файлов в <dir>")

def start_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

def main(args):
    if len(args) > 1:
        if args[1] == "/stats":
            if len(args) > 2:
                process_stats(args[2])
            else:
                usage()
        if args[1] == "/measure":
            measure()
    else:
        usage()
        start_gui()

if __name__ == '__main__':
    main(sys.argv)
    # input("\nНажмите Enter для завершения работы.")
