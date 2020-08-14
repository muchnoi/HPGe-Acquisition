from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import style
from ctypes import c_int64

class AcqCanvas(FigureCanvas):
  DataSize = 512
  DataType = c_int64*DataSize
  __X = DataType()
  __Y = DataType()
  __colors  = ['#080000']

  
  def __init__(self, parent=None, width=6, height=4, dpi=100):
    style.use('default')
    fig = Figure(figsize=(width, height), dpi=dpi)
    fig.patch.set_facecolor('#F0F0A0')
    fig.patch.set_alpha(0.75)
    FigureCanvas.__init__(self, fig)
    self.figure.subplotpars.left, self.figure.subplotpars.right = 0.075, 0.975
    self.figure.subplotpars.top, self.figure.subplotpars.bottom = 0.975, 0.100
    self.plt = self.figure.add_subplot(111)
#    self.plt.set_autoscale_on(False)
#    self.plt.set_axisbelow(False)
    self.plt.set_xlabel('channels', horizontalalignment='right', position=(1,25))
    self.plt.set_ylabel('counts')
    self.plt.patch.set_facecolor('#E0E0FF')
    self.plt.patch.set_alpha(0.75)
    self.plt.grid(ls = ':', c = '#000000')
    self._plot_ptr = None

  def Prepare(self, ext):
    self.H   = ext.Histogram
    self.ext = ext
#    ext.gui.addToolBar(0x4, NavigationToolbar(self, ext.gui))   
  
  def Show_Spectrum(self):
    cmin = self.ext.gui.HistogramScrollBar.value()
    cmax = self.ext.gui.HistogramScrollBar.value() + self.ext.PageStep
    step = (self.ext.PageStep+1)/self.DataSize
#    print(cmin, cmax, step)
    for x in range(self.DataSize):
      i = int(cmin + x*step)
      j = int(i + step)
      if i==j: self.__Y[x] = self.H[i]
      else:    self.__Y[x] = sum(self.H[i:j])
      self.__X[x] = (i+j)//2
    if self._plot_ptr is None:
      self._plot_ptr  = self.plt.step(self.__X, self.__Y, color = self.__colors[0])[0]
    else:
      self._plot_ptr.set_xdata(self.__X)
      self._plot_ptr.set_ydata(self.__Y)
      self.plt.set_xlim(left = cmin,                       right  = cmax + step)
      if self.ext.gui.LogScaleCheckBox.isChecked():
        self.plt.set_yscale('log')
        self.plt.set_ylim(top  = int(1.1*max(self.__Y) + 1), bottom = 1)
      else:
        self.plt.set_yscale('linear')
        self.plt.set_ylim(top  = int(1.1*max(self.__Y) + 1), bottom = 0)
    self.draw()

