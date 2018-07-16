from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
import numpy

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
        plt.ylim([-60, 10])
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

    def parseMeasurementStr(self, string):
        return [float(num) for num in string.split(',')]

    @property
    def cutoffMag(self):
        return self._cutoffMag

    @cutoffMag.setter
    def cutoffMag(self, value: float):
        self._cutoffMag = value
        self._cutoffTickAdded = False

    @pyqtSlot()
    def processDataPoint(self):
        print('processing measurement')
        freq = self.parseMeasurementStr(self._domainModel._lastMeasurement[0])
        amp = self.parseMeasurementStr(self._domainModel._lastMeasurement[1])

        self.freqs.append(freq)
        self.amps.append(amp)

        if not self._cutoffTickAdded:
            # plt.yticks(list(plt.yticks())[0] + [self._cutoffMag])
            plt.yticks(list(range(-60, 10, 10)) + [self._cutoffMag])
            self._cutoffTickAdded = True

        plt.figure(1)
        plt.plot(freq, amp, color="0.4")

        self.mainFigure.canvas.draw()

        # print(self._domainModel._lastMeasurement)

    @pyqtSlot()
    def measurementFinished(self):
        for a, f in zip(self.amps, self.freqs):
            self.cutoff_freq_y.append(f[a.index(min(a, key=lambda x: abs(self._cutoffMag - x)))])

        self.cutoff_freq_y = list(reversed(self.cutoff_freq_y))
        self.cutoff_freq_x = range(len(self.cutoff_freq_y))

        plt.figure(2)
        plt.plot(self.cutoff_freq_x, self.cutoff_freq_y, color="0.4")

        # for i in range(len(self.cutoff_freq_y[:-2])):
        for i in range(len(self.cutoff_freq_y[:-1])):
            d = abs(self.cutoff_freq_y[i + 1] - self.cutoff_freq_y[i])
            self.cutoff_freq_delta_y.append(d)

        self.cutoff_freq_delta_x = range(len(self.cutoff_freq_delta_y))

        plt.figure(3)
        plt.plot(self.cutoff_freq_delta_x, self.cutoff_freq_delta_y, color="0.4")


