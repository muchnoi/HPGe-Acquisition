class TAB_OS:
  _ADC     = 16383. # i. e. 14-bit ADC
  _zero    = 0.0    # ADC channel for V_Input = 0.0
  _gain    = 0.0    # i. e. [V / channel]

  def __init__(self):
    self.DPP.acqMode = 0 # Waveform = 0, Histogram = 1
    self.DPP.Read_DGTZ_Parameters()
    self.DPP.GetInputRange(self.DPP.CH)
    self.DPP.boardConfig.ChannelMask = self.DPP.CH+1
    self.DPP.SetBoardConfiguration()
    self.gui.QScope.Prepare(self.DPP, self.gui)
    self.__ADC() # tells QScope zero and gain parameters
    
#    self.DPP.StartAcquisition(self.DPP.CH)
    
    for k,v in self.DPP.GetInfoDict("InputRangeNum", "InputRanges").items(): 
      self.gui.InputRange.addItem('Range: {} V'.format(k), userData = v)
    for k,v in self.DPP.GetInfoDict("NumVirtualProbes1", "SupportedVirtualProbes1").items(): 
      self.gui.Virtual_1.addItem( 'A: {} '.format(k),  userData = v)
    for k,v in self.DPP.GetInfoDict("NumVirtualProbes2", "SupportedVirtualProbes2").items(): 
      self.gui.Virtual_2.addItem( 'B: {} '.format(k),  userData = v)
    for k,v in self.DPP.GetInfoDict("NumDigitalProbes1", "SupportedDigitalProbes1").items(): 
      self.gui.Digital_1.addItem( 'C: {} '.format(k),  userData = v)
    self.gui.InputPolarity.addItem( 'Pulse: Positive', userData = 0)
    self.gui.InputPolarity.addItem( 'Pulse: Negative', userData = 1)

#        printf("DCOffset\t\t\t= %.2f\n", ((float)(Params->DCoffset[ch]) / 655.35) - 50.0);
#        printf("Energy Normalization Factor\t= %.2f\n", Params->DPPParams.enf[ch]);
    self.gui.FineGainSpinBox.setValue(        self.DPP.boardConfig.DPPParams.enf[ self.DPP.CH])
    self.gui.DCoffsetSpinBox.setValue(self.DPP.boardConfig.DCoffset[self.DPP.CH]/655.35 - 50.0)
    self.gui.RiseTimeSpinBox.setValue(   1e-3*self.DPP.boardConfig.DPPParams.k[   self.DPP.CH])
    self.gui.DecayTimeSpinBox.setValue(  1e-3*self.DPP.boardConfig.DPPParams.M[   self.DPP.CH])
    self.gui.FlatTopSpinBox.setValue(    1e-3*self.DPP.boardConfig.DPPParams.m[   self.DPP.CH])
    self.gui.PeakDelaySpinBox.setValue(  1e-3*self.DPP.boardConfig.DPPParams.ftd[ self.DPP.CH])
    self.gui.PeakMeanSpinBox.setValue(        self.DPP.boardConfig.DPPParams.nspk[self.DPP.CH])
    self.gui.PeakHoldoffSpinBox.setValue(1e-3*self.DPP.boardConfig.DPPParams.pkho[self.DPP.CH])
    self.gui.BaseMeanSpinBox.setValue(        self.DPP.boardConfig.DPPParams.nsbl[self.DPP.CH])
    self.gui.BaseHoldoffSpinBox.setValue(1e-3*self.DPP.boardConfig.DPPParams.blho[self.DPP.CH])

    self.gui.TriggerNormal.setChecked(True)
    self.gui.TriggerSingle.setChecked(True)
    self.gui.TriggerSmoothing.setValue(       self.DPP.boardConfig.DPPParams.a[ self.DPP.CH])
    self.gui.TriggerRiseTime.setValue(   1e-3*self.DPP.boardConfig.DPPParams.b[ self.DPP.CH])
    self.gui.TriggerHoldoff.setValue(    1e-3*self.DPP.boardConfig.DPPParams.trgho[ self.DPP.CH])
    self.gui.TriggerLevel.setValue(           self.DPP.boardConfig.DPPParams.thr[ self.DPP.CH])
    self.gui.TriggerPrologue.setValue(.5*1e-3*self.DPP.boardConfig.WFParams.preTrigger)
    self.gui.TriggerSingle.toggled.connect(        self.gui.QScope.Loop)
    self.gui.TriggerButton.clicked.connect(        self.gui.QScope.Measure)
    self.gui.TriggerNormal.clicked.connect(        self.gui.QScope.Trigger)
    self.gui.TriggerExternal.clicked.connect(      self.gui.QScope.Trigger)
    self.gui.TriggerAuto.toggled.connect(          self.gui.QScope.Trigger)
    self.gui.TriggerLevel.valueChanged.connect(    self.gui.QScope.Trigger)
    self.gui.TriggerPrologue.valueChanged.connect( self.gui.QScope.Trigger)
    self.gui.TriggerSmoothing.valueChanged.connect(self.gui.QScope.Trigger)
    self.gui.TriggerRiseTime.valueChanged.connect( self.gui.QScope.Trigger)
    self.gui.TriggerHoldoff.valueChanged.connect(  self.gui.QScope.Trigger)
    self.gui.QScope.Trigger()

    self.gui.VScale.valueChanged.connect(self.gui.QScope.Legend)
    self.gui.HScale.valueChanged.connect(self.gui.QScope.Legend)
    self.gui.Offset.valueChanged.connect(self.gui.QScope.Legend)
    self.gui.Delay.valueChanged.connect( self.gui.QScope.Legend)
    
    self.gui.DCoffsetSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
    self.gui.FineGainSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
    self.gui.RiseTimeSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
    self.gui.DecayTimeSpinBox.valueChanged.connect(   self.__SpinBox_Value_Changed)
    self.gui.FlatTopSpinBox.valueChanged.connect(     self.__SpinBox_Value_Changed)
    self.gui.PeakDelaySpinBox.valueChanged.connect(   self.__SpinBox_Value_Changed)
    self.gui.PeakMeanSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
    self.gui.PeakHoldoffSpinBox.valueChanged.connect( self.__SpinBox_Value_Changed)
    self.gui.BaseMeanSpinBox.valueChanged.connect(    self.__SpinBox_Value_Changed)
    self.gui.BaseHoldoffSpinBox.valueChanged.connect( self.__SpinBox_Value_Changed)

    self.__SetInitialField(self.gui.InputRange,     self.DPP.inputRange[self.DPP.CH])
    self.__SetInitialField(self.gui.Virtual_1,      self.DPP.boardConfig.WFParams.vp1)
    self.__SetInitialField(self.gui.Virtual_2,      self.DPP.boardConfig.WFParams.vp2)
    self.__SetInitialField(self.gui.Digital_1,      self.DPP.boardConfig.WFParams.dp1)
    self.__SetInitialField(self.gui.InputPolarity,  self.DPP.boardConfig.PulsePolarity[self.DPP.CH])
    
    self.gui.InputRange.currentIndexChanged.connect(   self.__IRC)
    self.gui.InputPolarity.currentIndexChanged.connect(self.__IPP)
    self.gui.Virtual_1.currentIndexChanged.connect(    self.__VP1)
    self.gui.Virtual_2.currentIndexChanged.connect(    self.__VP2)
    self.gui.Digital_1.currentIndexChanged.connect(    self.__DP1)

  def __SpinBox_Value_Changed(self):
    self.DPP.boardConfig.DPPParams.enf[ self.DPP.CH] =            self.gui.FineGainSpinBox.value()
    self.DPP.boardConfig.DCoffset[self.DPP.CH] = int((self.gui.DCoffsetSpinBox.value() + 50.0) * 655.35)
    self.DPP.boardConfig.DPPParams.k[   self.DPP.CH] = int(1000 * self.gui.RiseTimeSpinBox.value())
    self.DPP.boardConfig.DPPParams.M[   self.DPP.CH] = int(1000 * self.gui.DecayTimeSpinBox.value())
    self.DPP.boardConfig.DPPParams.m[   self.DPP.CH] = int(1000 * self.gui.FlatTopSpinBox.value())
    self.DPP.boardConfig.DPPParams.ftd[ self.DPP.CH] = int(1000 * self.gui.PeakDelaySpinBox.value())
    self.DPP.boardConfig.DPPParams.nspk[self.DPP.CH] =            self.gui.PeakMeanSpinBox.value()
    self.DPP.boardConfig.DPPParams.pkho[self.DPP.CH] = int(1000 * self.gui.PeakHoldoffSpinBox.value())
    self.DPP.boardConfig.DPPParams.nsbl[self.DPP.CH] =            self.gui.BaseMeanSpinBox.value()
    self.DPP.boardConfig.DPPParams.blho[self.DPP.CH] = int(1000 * self.gui.BaseHoldoffSpinBox.value())
    self.DPP.SetBoardConfiguration()
    self.__ADC()

  def __SetInitialField(self, A, B): 
    for index in range(A.count()):
      if A.itemData(index) == B: A.setCurrentIndex(index); break

  def __ADC(self): # ADC Configuration
    POL = self.DPP.boardConfig.PulsePolarity[self.DPP.CH] 
    INR = self.DPP.inputRange[          self.DPP.CH]
    DCO = self.DPP.boardConfig.DCoffset[self.DPP.CH]   # in units of LSB 
    if   POL is 0: 
      if DCO < 25000: zero = 16989.5 - 0.273058 * DCO  # positive polarity
      else:           zero = 17035.6 - 0.274045 * DCO  # positive polarity
    elif POL is 1: 
      if DCO < 25000: zero = -606.92 + 0.272018 * DCO  # negative polarity
      else:           zero = -653.33 + 0.274035 * DCO  # negative polarity
    gain = self.DPP.inputRanges[INR]/self._ADC         # i.e. Volts / LSB
    self.gui.QScope.Scale(zero, gain)
    

  def __IRC(self, index): # input range control
    self.DPP.inputRange[self.DPP.CH] = self.gui.InputRange.itemData(index)
    self.DPP.SetInputRange(self.DPP.CH)
    self.__ADC()
    
  def __IPP(self, index): # input pulse polarity
    self.DPP.boardConfig.PulsePolarity[self.DPP.CH] = self.gui.InputPolarity.itemData(index)
    self.DPP.SetBoardConfiguration()
    self.__ADC()
    
  def __VP1(self, index): # virtual probe 1
    self.DPP.boardConfig.WFParams.vp1 = self.gui.Virtual_1.itemData(index)
    self.DPP.SetBoardConfiguration()
    
  def __VP2(self, index): # virtual probe 2
    self.DPP.boardConfig.WFParams.vp2 = self.gui.Virtual_2.itemData(index)
    self.DPP.SetBoardConfiguration()
    
  def __DP1(self, index): # digital probe 1
    self.DPP.boardConfig.WFParams.dp1 = self.gui.Digital_1.itemData(index)
    self.DPP.SetBoardConfiguration()
    
