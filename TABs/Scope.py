#from matplotlib import use
#use('Qt5Agg')
#import matplotlib.pyplot as plt
#import matplotlib as mpl
from ctypes import c_double
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import style
style.use('dark_background')

class OscCanvas(FigureCanvas):
  ArrayType = c_double*8192
  __A       = ArrayType() # Scope A
  __B       = ArrayType() # Scope B
  __C       = ArrayType() # Scope C
  __T       = ArrayType() # Scope T
  __colors  = ['#FF1493', '#7FFF00', '#00FFFF', '#FFFF00', '#F4A460']
  __labels  = ['']*5
  __vscale  = [1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1.00, 2.00, 5.00]
  __hscale  = [1e+2, 2e+2, 5e+2, 1e+3, 2e+3, 5e+3, 1e+4, 2e+4, 5e+4]
  __zero    = 0.0
  __gain    = 0.0
  
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    FigureCanvas.__init__(self, fig)
    self.figure.subplotpars.left, self.figure.subplotpars.right = 0.005, 0.995
    self.figure.subplotpars.top, self.figure.subplotpars.bottom = 0.995, 0.12
    self._plot_ref, self._nsample, self._tsample = None, None, None
    for ch in range(5):
      self.__labels[ch] = self.figure.text(0.025 + 0.18*ch, 0.025, "***", 
                                         color    = self.__colors[ch], 
                                         family   = 'monospace', 
                                         fontsize = 14)
    self.osc = self.figure.add_subplot(111)

#  def access_DPP(self, DPP): self.DPP = DPP
#  def access_gui(self, gui): self.gui = gui

  def Prepare(self, DPP, gui):  
    self.DPP = DPP
    self.gui = gui
    self.osc.set_xlim(-4,  4);        self.osc.xaxis.set_ticklabels('')
    self.osc.set_ylim(-4 , 4);        self.osc.yaxis.set_ticklabels('')
    self.osc.set_autoscale_on(False); self.osc.set_axisbelow(False)
    self.osc.grid(ls = ':', c = 'w')
    self.osc.tick_params(direction='in', length=4, width=1, bottom=1, top=1, left=1, right=1)

  def Scale(self, zero, gain):
    self.__zero, self.__gain = zero, gain
    print(zero,gain)
    
  def Loop(self):
    if self.gui.TriggerSingle.isChecked(): 
      self.gui.timerB.timeout.disconnect(self.Measure)
      self.gui.timerB.stop()
      self.DPP.StopAcquisition(self.DPP.CH)
    else:                                  
      self.gui.timerB.start(499)
      self.gui.timerB.timeout.connect(self.Measure)
      self.DPP.StartAcquisition(self.DPP.CH)

  def Measure(self):
    if self.gui.TriggerSingle.isChecked():  self.DPP.StartAcquisition(self.DPP.CH)
    self._nsample, self._tsample = self.DPP.GetWaveform(self.DPP.CH)
    if self.gui.TriggerSingle.isChecked():  self.DPP.StopAcquisition(self.DPP.CH)
    self.Legend()
  
  def IGV(self, code, offset): # i. e. Input Graph Voltage  
    return ((code - self.__zero)*self.__gain + self.__voltshift)/self.__voltscale
  
  def Visualize(self):
#    print('Virtual 1 average = {:.2f} lsb'.format(0.01*sum(self.DPP.Traces.AT1[0:100])))
#    print('Virtual 2 average = {:.2f} lsb'.format(0.01*sum(self.DPP.Traces.AT2[0:100])))
#    print('Digital 1 average = {:.2f} lsb'.format(0.01*sum(self.DPP.Traces.DT1[0:100])))
    """ # This was used for zero determination procedure:
    D, A = 0.25*DC_Offset, 0.01*sum(self.DPP.Traces.AT2[0:100])
    print('Signal DC offset = {:.2f} lsb'.format(D))
    print('Signal 2 average = {:.2f} lsb'.format(A))
    s = '{:6.2f}  {:6.2f}\n'.format(D,A)
    with open('negative.txt', 'a') as fp: fp.write(s)
    """

    for to in range(self._nsample):
      if self.DPP.Traces.DT2[to]: break
    for t in range(self._nsample): 
      self.__T[t] = ((t-to)*self._tsample + self.__timeshift)/self.__timescale # this is for X-sxis: (t-to) in [ns]
      self.__A[t] = self.IGV(self.DPP.Traces.AT1[t], True)
      self.__B[t] = self.IGV(self.DPP.Traces.AT2[t], False)
      self.__C[t] = self.DPP.Traces.DT1[t]*6.0 - 3.0
#      print(self.__T[t], self.__A[t])

    if self._plot_ref is None:
      A = self.osc.plot(self.__T[:self._nsample], self.__A[:self._nsample], '-', color=self.__colors[0])[0]
      B = self.osc.plot(self.__T[:self._nsample], self.__B[:self._nsample], '-', color=self.__colors[1])[0]
      C = self.osc.plot(self.__T[:self._nsample], self.__C[:self._nsample], '-', color=self.__colors[2])[0]
      self._plot_ref = [A, B, C]
    else:
      self._plot_ref[0].set_xdata(self.__T[:self._nsample])
      self._plot_ref[0].set_ydata(self.__A[:self._nsample])
      self._plot_ref[1].set_xdata(self.__T[:self._nsample])
      self._plot_ref[1].set_ydata(self.__B[:self._nsample])
      self._plot_ref[2].set_xdata(self.__T[:self._nsample])
      self._plot_ref[2].set_ydata(self.__C[:self._nsample])
    self.draw()

  def Legend(self):
    self.__voltscale = self.__vscale[self.gui.VScale.value()]
    self.__voltshift = 0.1 * self.__voltscale * self.gui.Offset.value()
    if         self.__voltscale < 1.00: text  = 'A:{:4.0f}mV\n'.format(1000*self.__voltscale)
    else:                               text  = 'A:{:4.1f} V\n'.format(     self.__voltscale)
    if -1.00 < self.__voltshift < 1.00: text += 'Δ:{:+4.0f}mV'.format( 1000*self.__voltshift)
    else:                               text += 'Δ:{:+4.1f} V'.format(      self.__voltshift)
    self.__labels[0].set_text(text)

    self.__timescale = self.__hscale[self.gui.HScale.value()]
    self.__timeshift = 0.1 * self.__timescale * self.gui.Delay.value()
    if         self.__timescale < 1e+3: text  = 'T:{:4.0f}ns\n'.format(     self.__timescale)
    else:                               text  = 'T:{:4.0f}μs\n'.format(1e-3*self.__timescale)
    if -1e+3 < self.__timeshift < 1e+3: text += 'Δ:{:+4.0f}ns'.format(       self.__timeshift)
    else:                               text += 'Δ:{:+4.1f}μs'.format(  1e-3*self.__timeshift)
    self.__labels[3].set_text(text)    

    onehalf = 3*self.__voltscale
    if     onehalf < 1.00: text  = 'C₁={:+4.0f}mV\nC₀={:+4.0f}mV'.format(1000*onehalf,-1000*onehalf)
    else:                  text  = 'C₁={:+4.0f} V\nC₀={:+4.0f} V'.format(     onehalf,     -onehalf)
    self.__labels[2].set_text(text)    
    
    if self._nsample is None: self.draw()
    else:               self.Visualize()

  def Trigger(self):
    TL = self.gui.TriggerLevel.value()
    PT = self.gui.TriggerPrologue.value()                                                              # μs
    text = 'level:  {:5.0f}mV\npreamble: {:3.1f}μs'.format(1e+3*TL*self.__gain, PT)                    # mV, μs
    self.__labels[4].set_text(text)
    self.DPP.boardConfig.DPPParams.thr[self.DPP.CH]       = TL                                         # lsb
    self.DPP.boardConfig.WFParams.preTrigger              = int(2e+3*PT)                               # ns
    self.DPP.boardConfig.DPPParams.a[ self.DPP.CH]        =          self.gui.TriggerSmoothing.value() # samples
    self.DPP.boardConfig.DPPParams.b[ self.DPP.CH]        = int(1e+3*self.gui.TriggerRiseTime.value()) # ns
    self.DPP.boardConfig.DPPParams.trgho[ self.DPP.CH]    = int(1e+3*self.gui.TriggerHoldoff.value())  # ns
    self.DPP.trigger = int(self.gui.TriggerAuto.isChecked())
#    if self.gui.TriggerAuto.isChecked(): self.DPP.trigger = 1
#    else:                                self.DPP.trigger = 0
    self.DPP.SetBoardConfiguration()
    self.draw()
#    if self._nsample is None: self.draw()
#    else:               self.Visualize()
    
    

