from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import style
from ctypes import c_int64, c_float

class AcqCanvas(FigureCanvas):
  DataSize = 512
  XDataType = c_float*DataSize
  YDataType = c_int64*DataSize
  __X = XDataType()
  __Y = YDataType()
  __Z = None
  __colors  = ['#101010', '#FF0000', '#00FF00', '#FFFF00']
  
  def __init__(self, parent=None, width=6, height=4, dpi=100):
    style.use('default')
    fig = Figure(figsize=(width, height), dpi=dpi)
    fig.patch.set_facecolor('#F0F0A0')
    fig.patch.set_alpha(0.75)
    FigureCanvas.__init__(self, fig)
    self.figure.subplotpars.left, self.figure.subplotpars.right = 0.10, 0.98
    self.figure.subplotpars.top, self.figure.subplotpars.bottom = 0.98, 0.10
    self.plt = self.figure.add_subplot(111)
#    self.plt.set_autoscale_on(False)
#    self.plt.set_axisbelow(False)

  def Prepare(self, ext):
    self.ext = ext
    self.plt.cla()
    if self.__Z is None: self.__Z = [None for el in range(ext.ScaleSize)]
    if 'spectrum' in ext.Visualize:
      self.plt.set_ylabel('counts')
      self.plt.patch.set_facecolor('#E0E0FF')
      self.plt.patch.set_alpha(0.75)
      self.plt.grid(ls = ':', c = '#000000')
      self._pH = None
    else:
      self.__T = [(el - ext.ScaleSize + 1)*ext.AcqPar['UpdateTime'] for el in range(ext.ScaleSize)]
      self.plt.set_xlabel('time [s]', horizontalalignment='right', position=(1,25))
      self.plt.set_ylabel('rates A, B, C [counts / s]')
      self.plt.patch.set_facecolor('#000000')
      self.plt.patch.set_alpha(0.99)
      self.plt.grid(ls = ':', c = '#F0F0A0')
      self._pS = None
      
  
  def Show_Spectrum(self):
    if self.ext.keV == 1.0: self.plt.set_xlabel('channels',     horizontalalignment='right', position=(1, 25))
    else:                   self.plt.set_xlabel('energy [keV]', horizontalalignment='right', position=(1, 25))
    cmin = self.ext.gui.HistogramScrollBar.value()
    cmax = self.ext.gui.HistogramScrollBar.value() + self.ext.PageStep
    step = (self.ext.PageStep+1)/self.DataSize
    for x in range(self.DataSize):
      i = int(cmin + x*step)
      j = int(i + step)
      if i==j: self.__Y[x] = self.ext.Histogram[i]
      else:    self.__Y[x] = sum(self.ext.Histogram[i:j])
      self.__X[x] = 0.5*(i+j)*self.ext.keV #      self.__X[x] = (i+j)//2
    if self._pH is None:
      self._pH  = self.plt.step(self.__X, self.__Y, linewidth = 1, color = self.__colors[0])[0]
    else:
      self._pH.set_xdata(self.__X)
      self._pH.set_ydata(self.__Y)
      self.plt.set_xlim(left = cmin*self.ext.keV, right  = (cmax + step)*self.ext.keV)
      if self.ext.gui.LogScaleCheckBox.isChecked():
        self.plt.set_yscale('log')
        self.plt.set_ylim(top  = int(1.1*max(self.__Y) + 1), bottom = 0.1)
      else:
        self.plt.set_yscale('linear')
        self.plt.set_ylim(top  = int(1.1*max(self.__Y) + 1), bottom = 0)
    self.draw()

  def Show_Counting(self):
    L = self.ext.ScalesMax
    if self._pS is None:
      A  = self.plt.step(self.__T, self.ext.ScaleList[0], linewidth = 1, color = self.__colors[1])[0]
      B  = self.plt.step(self.__T, self.ext.ScaleList[1], linewidth = 1, color = self.__colors[2])[0]
      C  = self.plt.step(self.__T, self.ext.ScaleList[2], linewidth = 1, color = self.__colors[3])[0]
      self.plt.legend((A, B, C), ('Rate A', 'Rate B', 'Rate C'))
      self._pS = [A, B, C]
    else:
      if self.ext.gui.ACheckBox.isChecked(): self._pS[0].set_ydata(self.ext.ScaleList[0])
      else:                                  self._pS[0].set_ydata(self.__Z);  L[0] = 0
      if self.ext.gui.BCheckBox.isChecked(): self._pS[1].set_ydata(self.ext.ScaleList[1])
      else:                                  self._pS[1].set_ydata(self.__Z);  L[1] = 0
      if self.ext.gui.CCheckBox.isChecked(): self._pS[2].set_ydata(self.ext.ScaleList[2])
      else:                                  self._pS[2].set_ydata(self.__Z);  L[2] = 0
    self.plt.set_ylim(top = int(1.1*max(L) + 1), bottom = 0)
    self.draw()

