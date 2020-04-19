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
  __single  = True
  
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    FigureCanvas.__init__(self, fig)
    self.figure.subplotpars.left, self.figure.subplotpars.right = 0.005, 0.995
    self.figure.subplotpars.top, self.figure.subplotpars.bottom = 0.995, 0.12
    self._plot_ref, self._nsample, self._tsamp = None, None, None
    for ch in range(5):
      self.__labels[ch] = self.figure.text(0.025 + 0.18*ch, 0.025, "***", 
                                         color    = self.__colors[ch], 
                                         family   = 'monospace', 
                                         fontsize = 14)
    self.osc = self.figure.add_subplot(111)

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
#    print(zero,gain)
    
  def ButtonPressed(self):
    button        = self.gui.TriggerButton.text()
    if  'Start' in button: 
      self.Measure()
      if not self.__single:
        self.gui.TriggerButton.setText('Stop')
        self.gui.timerB.start(499)
        self.gui.timerB.timeout.connect(self.Measure)
    elif 'Stop' in button: 
      self.gui.timerB.timeout.disconnect(self.Measure)
      self.gui.timerB.stop()
      self.gui.TriggerButton.setText('Start')
    
  def Measure(self):
    status                     = self.DPP.IsChannelAcquiring(self.DPP.CH)
    if status is 0:              self.DPP.StartAcquisition(  self.DPP.CH)
    self._nsample, self._tsamp = self.DPP.GetWaveform(       self.DPP.CH)
    if self.__single:            self.DPP.StopAcquisition(   self.DPP.CH)
    self.Legend()
 
  def Visualize(self):
    for to in range(self._nsample):
      if self.DPP.Traces.DT2[to]: break
    PA,  QA  = self.__gain/self.__AScale, self.__AShift/self.__AScale
    PB,  QB  = self.__gain/self.__BScale, self.__BShift/self.__BScale
    PT,  QT  = self._tsamp/self.__TScale, self.__TShift/self.__TScale; QT -= to*PT
    if self.DPP.boardConfig.WFParams.vp1 is 0: QA -= self.__zero * PA
    if self.DPP.boardConfig.WFParams.vp2 is 0: QB -= self.__zero * PB
    for t in range(self._nsample): 
      self.__A[t] = PA * self.DPP.Traces.AT1[t] + QA
      self.__B[t] = PB * self.DPP.Traces.AT2[t] + QB
      self.__C[t] = 6. * self.DPP.Traces.DT1[t] - 3.
      self.__T[t] = PT *                     t  + QT

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
    self.__AScale = self.__vscale[self.gui.ScaleA.value()]
    self.__AShift = 0.1 * self.__AScale * self.gui.ShiftA.value()
    if         self.__AScale < 1.00: text  = 'A:{:4.0f}mV\n'.format(1000*self.__AScale)
    else:                            text  = 'A:{:4.1f} V\n'.format(     self.__AScale)
    if -1.00 < self.__AShift < 1.00: text += 'Δ:{:+4.0f}mV'.format( 1000*self.__AShift)
    else:                            text += 'Δ:{:+4.1f} V'.format(      self.__AShift)
    self.__labels[0].set_text(text)

    self.__BScale = self.__vscale[self.gui.ScaleB.value()]
    self.__BShift = 0.1 * self.__BScale * self.gui.ShiftB.value()
    if         self.__BScale < 1.00: text  = 'B:{:4.0f}mV\n'.format(1000*self.__BScale)
    else:                            text  = 'B:{:4.1f} V\n'.format(     self.__BScale)
    if -1.00 < self.__BShift < 1.00: text += 'Δ:{:+4.0f}mV'.format( 1000*self.__BShift)
    else:                            text += 'Δ:{:+4.1f} V'.format(      self.__BShift)
    self.__labels[1].set_text(text)

    self.__TScale = self.__hscale[self.gui.ScaleT.value()]
    self.__TShift = 0.1 * self.__TScale * self.gui.ShiftT.value()
    if         self.__TScale < 1e+3: text  = 'T:{:4.0f}ns\n'.format(     self.__TScale)
    else:                            text  = 'T:{:4.0f}μs\n'.format(1e-3*self.__TScale)
    if -1e+3 < self.__TShift < 1e+3: text += 'Δ:{:+4.0f}ns'.format(      self.__TShift)
    else:                            text += 'Δ:{:+4.1f}μs'.format( 1e-3*self.__TShift)
    self.__labels[3].set_text(text)    

    onehalf = 3*self.__AScale
    if     onehalf < 1.00: text  = 'C₁={:+4.0f}mV\nC₀={:+4.0f}mV'.format(1000*onehalf,-1000*onehalf)
    else:                  text  = 'C₁={:+4.0f} V\nC₀={:+4.0f} V'.format(     onehalf,     -onehalf)
    self.__labels[2].set_text(text)    
    
    if self._nsample is None: self.draw()
    else:               self.Visualize()

  def Trigger(self, index):
    TL = self.gui.TriggerLevel.value()
    PT = self.gui.TriggerPrologue.value()                                                              # μs
    text = 'level:  {:5.0f}mV\npreamble: {:3.1f}μs'.format(1e+3*TL*self.__gain, PT)                    # mV, μs
    self.__labels[4].set_text(text)
    self.DPP.boardConfig.DPPParams.thr[self.DPP.CH]       = TL                                         # lsb
    self.DPP.boardConfig.WFParams.preTrigger              = int(2e+3*PT)                               # ns
    self.DPP.boardConfig.DPPParams.a[ self.DPP.CH]        =          self.gui.TriggerSmoothing.value() # samples
    self.DPP.boardConfig.DPPParams.b[ self.DPP.CH]        = int(1e+3*self.gui.TriggerRiseTime.value()) # ns
    self.DPP.boardConfig.DPPParams.trgho[ self.DPP.CH]    = int(1e+3*self.gui.TriggerHoldoff.value())  # ns
    if index in (2,3):   self.DPP.trigger = 1
    else:                self.DPP.trigger = 0
    if index in (1,3,5): self.__single = True
    else:                self.__single = False
    self.DPP.Board_Reconfigure(self.DPP.CH)
    self.draw()
#    if self._nsample is None: self.draw()
#    else:               self.Visualize()
    
    

