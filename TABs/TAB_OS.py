class TAB_OS:
  not_initiated = True

  def __init__(self):
    if self.not_initiated:
      for k,v in self.DPP.GetInfoDict("InputRangeNum", "InputRanges").items(): 
        self.gui.InputRange.addItem('ADC range: {} V'.format(k), userData = v)
      for k,v in self.DPP.GetInfoDict("NumVirtualProbes1", "SupportedVirtualProbes1").items(): 
        self.gui.Virtual_1.addItem( 'A: {} '.format(k),  userData = v)
      for k,v in self.DPP.GetInfoDict("NumVirtualProbes2", "SupportedVirtualProbes2").items(): 
        self.gui.Virtual_2.addItem( 'B: {} '.format(k),  userData = v)
      for k,v in self.DPP.GetInfoDict("NumDigitalProbes1", "SupportedDigitalProbes1").items(): 
        self.gui.Digital_1.addItem( 'C: {} '.format(k),  userData = v)
      for v in [1, 4, 16, 64]: 
        self.gui.PeakMean.addItem(' Peak Mean:   {} sample{}'.format(v, 's'*bool(v-1)), userData = v)
        self.gui.BaseMean.addItem(' Base Mean:   {} sample{}'.format(v, 's'*bool(v-1)), userData = v)
        self.gui.Smoothin.addItem('Smoothing: {} sample{}'.format(v, 's'*bool(v-1)), userData = v)
      self.gui.InputPolarity.addItem( 'Pulse: POSITIVE', userData = 0)
      self.gui.InputPolarity.addItem( 'Pulse: NEGATIVE', userData = 1)
      self.gui.TriggerMode.addItem('Mode: normal',       userData = 0)
      self.gui.TriggerMode.addItem('Mode: norm. single', userData = 1)
      self.gui.TriggerMode.addItem('Mode: auto',         userData = 2)
      self.gui.TriggerMode.addItem('Mode: auto single',  userData = 3)
      self.gui.TriggerMode.addItem('Mode: external',     userData = 4)
      self.gui.TriggerMode.addItem('Mode: ext. single',  userData = 5)
      self.gui.InputRange.currentIndexChanged.connect(   self.__IRC)
      self.gui.InputPolarity.currentIndexChanged.connect(self.__IPP)
      self.gui.Virtual_1.currentIndexChanged.connect(    self.__VP1)
      self.gui.Virtual_2.currentIndexChanged.connect(    self.__VP2)
      self.gui.Digital_1.currentIndexChanged.connect(    self.__DP1)
      self.gui.PeakMean.currentIndexChanged.connect(     self.__PeakMean)
      self.gui.BaseMean.currentIndexChanged.connect(     self.__BaseMean)
      self.gui.Smoothin.currentIndexChanged.connect(     self.__Smoothin)

      self.gui.FineGainSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
      self.gui.DCoffsetSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
      self.gui.RiseTimeSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
      self.gui.DecayTimeSpinBox.valueChanged.connect(   self.__SpinBox_Value_Changed)
      self.gui.FlatTopSpinBox.valueChanged.connect(     self.__SpinBox_Value_Changed)
      self.gui.PeakDelaySpinBox.valueChanged.connect(   self.__SpinBox_Value_Changed)
      self.gui.PeakHoldoffSpinBox.valueChanged.connect( self.__SpinBox_Value_Changed)
      self.gui.BaseHoldoffSpinBox.valueChanged.connect( self.__SpinBox_Value_Changed)
      self.gui.TriggerButton.clicked.connect(          self.gui.QScope.ButtonPressed)
      self.gui.TriggerMode.currentIndexChanged.connect(self.gui.QScope.Trigger)
      self.gui.TriggerLevel.valueChanged.connect(      self.gui.QScope.Trigger)
      self.gui.TriggerIntro.valueChanged.connect(      self.gui.QScope.Trigger)
      self.gui.TriggerRiseTime.valueChanged.connect(   self.gui.QScope.Trigger)
      self.gui.TriggerHoldoff.valueChanged.connect(    self.gui.QScope.Trigger)
      self.gui.ScaleA.valueChanged.connect(self.gui.QScope.Legend)
      self.gui.ShiftA.valueChanged.connect(self.gui.QScope.Legend)
      self.gui.ScaleB.valueChanged.connect(self.gui.QScope.Legend)
      self.gui.ShiftB.valueChanged.connect(self.gui.QScope.Legend)
      self.gui.ScaleT.valueChanged.connect(self.gui.QScope.Legend)
      self.gui.ShiftT.valueChanged.connect(self.gui.QScope.Legend)
      self.not_initiated = False

    self.DPP.acqMode = 0 # Waveform = 0, Histogram = 1
    self.Read_Scope_Parameters()

  def Init_Scope_Parameters(self):    
    self.DPP.Init_DGTZ_Parameters()
    self.DPP.GetInputRange(self.DPP.CH)
    self.Apply_Scope_Parameters()

  def Read_Scope_Parameters(self):    
    self.DPP.Read_DGTZ_Parameters()
    self.DPP.SetInputRange(self.DPP.CH)
    self.Apply_Scope_Parameters()

  def Apply_Scope_Parameters(self):    
    self.DPP.boardConfig.ChannelMask = self.DPP.CH+1
    self.DPP.Board_Reconfigure(self.DPP.CH)
    self.gui.groupBox_10.setTitle('Analog Input (CH %1d)' % self.DPP.CH)
    self.gui.QScope.Prepare(self.DPP, self.gui)

    self.gui.fill_initials = True
    self.__SetInitialField(self.gui.InputRange,     self.DPP.inputRange[self.DPP.CH])
    self.__SetInitialField(self.gui.Virtual_1,      self.DPP.boardConfig.WFParams.vp1)
    self.__SetInitialField(self.gui.Virtual_2,      self.DPP.boardConfig.WFParams.vp2)
    self.__SetInitialField(self.gui.Digital_1,      self.DPP.boardConfig.WFParams.dp1)
    self.__SetInitialField(self.gui.InputPolarity,  self.DPP.boardConfig.PulsePolarity[self.DPP.CH])
    self.__SetInitialField(self.gui.PeakMean,       self.DPP.boardConfig.DPPParams.nspk[self.DPP.CH])
    self.__SetInitialField(self.gui.BaseMean,       self.DPP.boardConfig.DPPParams.nsbl[self.DPP.CH])
    self.__SetInitialField(self.gui.Smoothin,       self.DPP.boardConfig.DPPParams.a[self.DPP.CH])

    self.gui.FineGainSpinBox.setValue(          self.DPP.boardConfig.DPPParams.enf[ self.DPP.CH])
    self.gui.DCoffsetSpinBox.setValue(int(100 - self.DPP.boardConfig.DCoffset[self.DPP.CH]/327.67))
    self.gui.RiseTimeSpinBox.setValue(   1e-3 * self.DPP.boardConfig.DPPParams.k[   self.DPP.CH])
    self.gui.DecayTimeSpinBox.setValue(  1e-3 * self.DPP.boardConfig.DPPParams.M[   self.DPP.CH])
    self.gui.FlatTopSpinBox.setValue(    1e-3 * self.DPP.boardConfig.DPPParams.m[   self.DPP.CH])
    self.gui.PeakDelaySpinBox.setValue(  1e-3 * self.DPP.boardConfig.DPPParams.ftd[ self.DPP.CH])
    self.gui.PeakHoldoffSpinBox.setValue(1e-3 * self.DPP.boardConfig.DPPParams.pkho[self.DPP.CH])
    self.gui.BaseHoldoffSpinBox.setValue(1e-3 * self.DPP.boardConfig.DPPParams.blho[self.DPP.CH])
    self.gui.TriggerRiseTime.setValue(   1e-3 * self.DPP.boardConfig.DPPParams.b[ self.DPP.CH])
    self.gui.TriggerHoldoff.setValue(    1e-3 * self.DPP.boardConfig.DPPParams.trgho[ self.DPP.CH])
    self.gui.TriggerLevel.setValue(             self.DPP.boardConfig.DPPParams.thr[ self.DPP.CH])
    self.gui.TriggerIntro.setValue(   .5*1e-3 * self.DPP.boardConfig.WFParams.preTrigger)
    self.gui.fill_initials = False
    self.__ADC()
    
  def __SpinBox_Value_Changed(self):
    if not self.gui.fill_initials:
      self.DPP.boardConfig.DCoffset[self.DPP.CH]       = int((100 - self.gui.DCoffsetSpinBox.value()) * 327.67)
      self.DPP.boardConfig.DPPParams.enf[ self.DPP.CH] =            self.gui.FineGainSpinBox.value()
      self.DPP.boardConfig.DPPParams.k[   self.DPP.CH] = int(1000 * self.gui.RiseTimeSpinBox.value())
      self.DPP.boardConfig.DPPParams.M[   self.DPP.CH] = int(1000 * self.gui.DecayTimeSpinBox.value())
      self.DPP.boardConfig.DPPParams.m[   self.DPP.CH] = int(1000 * self.gui.FlatTopSpinBox.value())
      self.DPP.boardConfig.DPPParams.ftd[ self.DPP.CH] = int(1000 * self.gui.PeakDelaySpinBox.value())
      self.DPP.boardConfig.DPPParams.pkho[self.DPP.CH] = int(1000 * self.gui.PeakHoldoffSpinBox.value())
      self.DPP.boardConfig.DPPParams.blho[self.DPP.CH] = int(1000 * self.gui.BaseHoldoffSpinBox.value())
      self.DPP.Board_Reconfigure(self.DPP.CH)
      self.__ADC()

  def __SetInitialField(self, A, B): 
    for index in range(A.count()):
      if A.itemData(index) == B: A.setCurrentIndex(index); break

  def __ADC(self): # ADC Configuration
    POL = self.DPP.boardConfig.PulsePolarity[self.DPP.CH] 
    INR = self.DPP.inputRange[          self.DPP.CH]
    DCO = self.DPP.boardConfig.DCoffset[self.DPP.CH]   # in units of LSB 
    if   POL == 0: 
      if DCO < 25000: zero = 16989.5 - 0.273058 * DCO  # positive polarity
      else:           zero = 17035.6 - 0.274045 * DCO  # positive polarity
    elif POL == 1: 
      if DCO < 25000: zero = -606.92 + 0.272018 * DCO  # negative polarity
      else:           zero = -653.33 + 0.274035 * DCO  # negative polarity
    gain = self.DPP.inputRanges[INR]/(1<<self.DPP.boardInfo.ADC_NBits)
    self.gui.QScope.Scale(zero, gain)
    self.gui.QScope.Legend()
    self.gui.QScope.Trigger()

  def __IRC(self, index): # input range control
    self.DPP.inputRange[self.DPP.CH] = self.gui.InputRange.itemData(index)
    self.DPP.SetInputRange(self.DPP.CH)
    self.__ADC()
    
  def __IPP(self, index): # input pulse polarity
    self.DPP.boardConfig.PulsePolarity[self.DPP.CH] = self.gui.InputPolarity.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)
    self.__ADC()
    
  def __VP1(self, index): # virtual probe 1
    self.DPP.boardConfig.WFParams.vp1 = self.gui.Virtual_1.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)
    
  def __VP2(self, index): # virtual probe 2
    self.DPP.boardConfig.WFParams.vp2 = self.gui.Virtual_2.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)
    
  def __DP1(self, index): # digital probe 1
    self.DPP.boardConfig.WFParams.dp1 = self.gui.Digital_1.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)
    
  def __PeakMean(self, index):
    self.DPP.boardConfig.DPPParams.nspk[self.DPP.CH] = self.gui.PeakMean.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)

  def __BaseMean(self, index):
    self.DPP.boardConfig.DPPParams.nsbl[self.DPP.CH] = self.gui.BaseMean.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)

  def __Smoothin(self, index):
    self.DPP.boardConfig.DPPParams.a[self.DPP.CH] = self.gui.Smoothin.itemData(index)
    self.DPP.Board_Reconfigure(self.DPP.CH)

    
