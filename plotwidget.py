import os
import errno

from PyQt5.QtCore import QObject, pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar

class PlotWidget(QObject):

    # TODO rewrite plotting

    def __init__(self, parent=None, domainModel=None):
        super().__init__(parent)

        self._domainModel = domainModel

        self._cutoffMag = -6.0
        self._cutoffTickAdded = False

        self.freqs = list()
        self.amps = list()

        self.codes = list()
        self.cutoff_freqs = list()
        self.loss_double_freq = list()
        self.loss_triple_freq = list()

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

        self.harmonicFigure = None
        self.harmonicCanvas = None
        self.harmonicToolbar = None

        self.doubleTripleFigure = None
        self.doubleTripleCanvas = None
        self.doubleTripleToolbar = None

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

        plt.figure(num=4)
        self.harmonicFigure = plt.figure(4)
        self.harmonicCanvas = FigureCanvas(self.harmonicFigure)
        self.harmonicToolbar = NavToolbar(canvas=self.harmonicCanvas, parent=None)
        self.parent()._ui.harmonicLayout.addWidget(self.harmonicCanvas)
        self.parent()._ui.harmonicLayout.addWidget(self.harmonicCanvas.toolbar)

        plt.figure(num=5)
        self.doubleTripleFigure = plt.figure(5)
        self.doubleTripleCanvas = FigureCanvas(self.doubleTripleFigure)
        self.doubleTripleToolbar = NavToolbar(canvas=self.doubleTripleCanvas, parent=None)
        self.parent()._ui.layoutDoubleTriple.addWidget(self.doubleTripleCanvas)
        self.parent()._ui.layoutDoubleTriple.addWidget(self.doubleTripleCanvas.toolbar)

        self.resetPlots()

    def resetPlots(self):
        # TODO: use self.XXXfigure
        plt.figure(1)
        plt.subplots_adjust(bottom=0.150)
        # plt.axhline(self._cutoffMag, 0, 1, linewidth=0.8, color='0.3', linestyle='--')
        plt.title('Коэффициент преобразования')
        plt.xscale('log')
        plt.xlabel('F, Гц')
        plt.ylabel('К-т пр., дБ')
        plt.ylim([-60, 30])
        plt.grid(b=True, which='minor', color='0.7', linestyle='--')
        plt.grid(b=True, which='major', color='0.5', linestyle='-')

        plt.figure(2)
        plt.subplots_adjust(bottom=0.150)
        plt.title('Частота среза по уровню ' + str(self._cutoffMag) + ' дБ')
        plt.xlabel('Код')
        plt.ylabel('F, МГц')
        plt.yscale('log')
        plt.grid(b=True, which='minor', color='0.7', linestyle='--')
        plt.grid(b=True, which='major', color='0.5', linestyle='-')

        plt.figure(3)
        plt.subplots_adjust(bottom=0.150)
        plt.title('Дельта частоты среза')
        plt.xlabel('Код')
        plt.ylabel('dF, МГц')
        plt.grid(True)

        plt.figure(4)
        plt.subplots_adjust(bottom=0.150)
        plt.title('Коэффициент преобразования для N-гармоники')
        plt.xscale('log')
        plt.xlabel('F, Гц')
        plt.ylabel('К-т пр., дБ')
        plt.ylim([-60, 30])
        plt.grid(b=True, which='minor', color='0.7', linestyle='--')
        plt.grid(b=True, which='major', color='0.5', linestyle='-')

        plt.figure(5)
        plt.subplots_adjust(bottom=0.150)
        plt.title('Затухание на двойной и тройной частоте среза')
        plt.xscale('log')
        plt.xlabel('Код')
        plt.ylabel('Подавление, дБ')
        plt.ylim([-60, 30])
        plt.grid(b=True, which='minor', color='0.7', linestyle='--')
        plt.grid(b=True, which='major', color='0.5', linestyle='-')

    def clearFigures(self):
        plt.figure(1).clear()
        plt.figure(2).clear()
        plt.figure(3).clear()
        plt.figure(4).clear()
        plt.figure(5).clear()
        self.resetPlots()

    def parseFreqStr(self, string):
        return [float(num) for num in string.split(',')]

    def parseAmpStr(self, string):
        return [float(num) for idx, num in enumerate(string.split(',')) if idx % 2 == 0]

    def exportPics(self, fmt='png'):
        if fmt.lower() == 'png':
            img_path = '.\\image\\'
            try:
                os.makedirs(img_path)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise IOError('Error creating image dir.')

            for index, fname in enumerate(['stats.png', 'cutoff.png', 'delta.png', 'harmonic.png']):
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

        fig = plt.figure(1)
        # if not self._cutoffTickAdded:
        #     # plt.yticks(list(plt.yticks())[0] + [self._cutoffMag])
        #     plt.yticks(list(range(-60, 30, 10)) + [self._cutoffMag])
        #     self._cutoffTickAdded = True

        plt.plot(freq, amp, color='0.4')

        self.mainFigure.canvas.draw()

    @pyqtSlot(name='measurementFinished')
    def measurementFinished(self):
        print('Статобработка.')
        max_amp = max(map(max, self.amps))

        cutoff_mag = max_amp + self._cutoffMag

        for a, f in zip(self.amps, self.freqs):
            cutoff_freq = f[a.index(min(a, key=lambda x: abs(cutoff_mag - x)))]
            self.cutoff_freqs.append(cutoff_freq)

            double_f = cutoff_freq * 2
            triple_f = cutoff_freq * 3
            double_f_index = f.index(min(f, key=lambda x: abs(double_f - x)))
            triple_f_index = f.index(min(f, key=lambda x: abs(triple_f - x)))

            self.loss_double_freq.append(a[double_f_index])
            self.loss_triple_freq.append(a[triple_f_index])

        self.cutoff_freqs = list(reversed(self.cutoff_freqs))
        self.codes = range(len(self.cutoff_freqs))

        fig = plt.figure(1)
        plt.axhline(cutoff_mag, 0, 1, linewidth=0.8, color='0.3', linestyle='--')
        plt.yticks(list(plt.yticks()[0]) + [cutoff_mag])
        fig.canvas.draw()

        fig = plt.figure(2)
        plt.plot(self.codes, self.cutoff_freqs, color='0.4')
        fig.canvas.draw()

        # for i in range(len(self.cutoff_freq_y[:-2])):
        for i in range(len(self.cutoff_freqs[:-1])):
            d = abs(self.cutoff_freqs[i + 1] - self.cutoff_freqs[i])
            self.cutoff_freq_delta_y.append(d)

        self.cutoff_freq_delta_x = range(len(self.cutoff_freq_delta_y))

        fig = plt.figure(3)
        plt.plot(self.cutoff_freq_delta_x, self.cutoff_freq_delta_y, color='0.4')
        fig.canvas.draw()

        fig = plt.figure(5)
        try:
            plt.plot(self.codes, self.loss_double_freq, color='blue')
            plt.plot(self.codes, self.loss_triple_freq, color='red')
        except Exception as ex:
            print(ex)
        fig.canvas.draw()

    @pyqtSlot(name='harmonicMeasured')
    def harmonicMeasured(self):
        self.clearFigures()
        self.resetPlots()

        xs = self.parseFreqStr(self._domainModel._lastMeasurement[0])
        ys = self.parseAmpStr(self._domainModel._lastMeasurement[1])
        cutoff_mag = self._cutoffMag
        print('Рисуем график для N гармоники.')

        fig = plt.figure(4)
        plt.plot(xs, ys, color='0.4')
        plt.axhline(cutoff_mag, 0, 1, linewidth=0.8, color='0.3', linestyle='--')
        plt.yticks(list(plt.yticks()[0]) + [cutoff_mag])
        fig.canvas.draw()
