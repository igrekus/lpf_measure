import os
import errno

from PyQt5.QtCore import QObject, pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar

class PlotWidget(QObject):

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)

        self._domainModel = domainModel

        self._cutoffMag = -6.0
        self._cutoffTickAdded = False

        self.freqs = list()
        self.amps = list()

        self.cutoff_freq_x = list()
        self.cutoff_freq_y = list()

        self.cutoff_freq_delta_y = list()
        self.cutoff_freq_delta_x = list()

        self.mainFigure = None
        self.mainCanvas = None
        self.mainToolbar = None

        self.cutoffFreqFigure = None
        self.cutoffFreqCanvas = None
        self.cutoffFreqToolbar = None

        self.cutoffDeltaFigure = None
        self.cutoffDeltaCanvas = None
        self.cutoffDeltaToolbar = None

    def initPlots(self):
        plt.figure(num=1)
        self.mainFigure = plt.figure(1)
        self.mainCanvas = FigureCanvas(self.mainFigure)
        self.mainToolbar = NavToolbar(canvas=self.mainCanvas, parent=None)
        self.parent()._ui.layoutMainPlot.addWidget(self.mainCanvas)
        self.parent()._ui.layoutMainPlot.addWidget(self.mainCanvas.toolbar)

        plt.figure(num=2)
        self.cutoffFreqFigure = plt.figure(2)
        self.cutoffFreqCanvas = FigureCanvas(self.cutoffFreqFigure)
        self.cutoffFreqToolbar = NavToolbar(canvas=self.cutoffFreqCanvas, parent=None)
        self.parent()._ui.cutoffFreqLayut.addWidget(self.cutoffFreqCanvas)
        self.parent()._ui.cutoffFreqLayut.addWidget(self.cutoffFreqCanvas.toolbar)

        plt.figure(num=3)
        self.cutoffDeltaFigure = plt.figure(3)
        self.cutoffDeltaCanvas = FigureCanvas(self.cutoffDeltaFigure)
        self.cutoffDeltaToolbar = NavToolbar(canvas=self.cutoffDeltaCanvas, parent=None)
        self.parent()._ui.cutoffDeltaLayout.addWidget(self.cutoffDeltaCanvas)
        self.parent()._ui.cutoffDeltaLayout.addWidget(self.cutoffDeltaCanvas.toolbar)

        self.resetPlots()

    def resetPlots(self):
        plt.figure(1)
        plt.subplots_adjust(bottom=0.150)
        # plt.axhline(self._cutoffMag, 0, 1, linewidth=0.8, color="0.3", linestyle="--")
        plt.title("Коэффициент преобразования")
        plt.xscale("log")
        plt.xlabel("F, Гц")
        plt.ylabel("К-т пр., дБ")
        plt.ylim([-60, 30])
        plt.grid(b=True, which="minor", color="0.7", linestyle='--')
        plt.grid(b=True, which="major", color="0.5", linestyle='-')

        plt.figure(2)
        plt.subplots_adjust(bottom=0.150)
        plt.title("Частота среза по уровню " + str(self._cutoffMag) + " дБ")
        plt.xlabel("Код")
        plt.ylabel("F, МГц")
        plt.yscale("log")
        plt.grid(b=True, which="minor", color="0.7", linestyle='--')
        plt.grid(b=True, which="major", color="0.5", linestyle='-')

        plt.figure(3)
        plt.subplots_adjust(bottom=0.150)
        plt.title("Дельта частоты среза")
        plt.xlabel("Код")
        plt.ylabel("dF, МГц")
        plt.grid(True)

    def clearFigures(self):
        plt.figure(1).clear()
        plt.figure(2).clear()
        plt.figure(3).clear()
        self.resetPlots()

    def parseFreqStr(self, string):
        return [float(num) for num in string.split(',')]

    def parseAmpStr(self, string):
        return [float(num) for idx, num in enumerate(string.split(',')) if idx % 2 == 0]

    def exportPics(self, fmt='png'):
        if fmt.lower() == 'png':
            img_path = ".\\image\\"
            try:
                os.makedirs(img_path)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise IOError('Error creating image dir.')

            for index, fname in enumerate(['stats.png', 'cutoff.png', 'delta.png']):
                fig = plt.figure(index + 1)
                fig.savefig(img_path + fname, dpi=400)
        else:
            raise ValueError('Unsupported format')

    @property
    def cutoffMag(self):
        return self._cutoffMag

    @cutoffMag.setter
    def cutoffMag(self, value: float):
        self._cutoffMag = value
        self._cutoffTickAdded = False

    @pyqtSlot(name='processDataPoint')
    def processDataPoint(self):
        print('Обработка измерения.')
        freq = self.parseFreqStr(self._domainModel._lastMeasurement[0])
        amp = self.parseAmpStr(self._domainModel._lastMeasurement[1])

        self.freqs.append(freq)
        self.amps.append(amp)

        if not self._cutoffTickAdded:
            # plt.yticks(list(plt.yticks())[0] + [self._cutoffMag])
            plt.yticks(list(range(-60, 30, 10)) + [self._cutoffMag])
            self._cutoffTickAdded = True

        plt.figure(1)
        plt.plot(freq, amp, color="0.4")

        self.mainFigure.canvas.draw()

        # print(self._domainModel._lastMeasurement)

    @pyqtSlot(name='measurementFinished')
    def measurementFinished(self):
        print('Статобработка.')
        max_amp = max(map(max, self.amps))

        cutoff_mag = max_amp + self._cutoffMag

        for a, f in zip(self.amps, self.freqs):
            self.cutoff_freq_y.append(f[a.index(min(a, key=lambda x: abs(cutoff_mag - x)))])

        self.cutoff_freq_y = list(reversed(self.cutoff_freq_y))
        self.cutoff_freq_x = range(len(self.cutoff_freq_y))

        fig = plt.figure(1)
        plt.axhline(cutoff_mag, 0, 1, linewidth=0.8, color="0.3", linestyle="--")
        plt.yticks(list(plt.yticks()[0]) + [cutoff_mag])
        fig.canvas.draw()

        fig = plt.figure(2)
        plt.plot(self.cutoff_freq_x, self.cutoff_freq_y, color="0.4")
        fig.canvas.draw()

        # for i in range(len(self.cutoff_freq_y[:-2])):
        for i in range(len(self.cutoff_freq_y[:-1])):
            d = abs(self.cutoff_freq_y[i + 1] - self.cutoff_freq_y[i])
            self.cutoff_freq_delta_y.append(d)

        self.cutoff_freq_delta_x = range(len(self.cutoff_freq_delta_y))

        fig = plt.figure(3)
        plt.plot(self.cutoff_freq_delta_x, self.cutoff_freq_delta_y, color="0.4")
        fig.canvas.draw()

