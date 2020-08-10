from ctypes import c_int32
import pickle

class TAB_SP:
  initiated    = False
  HistoSize    = 16384
  HistoType    = c_int32*HistoSize # length of a histogram
  Histogram    = HistoType()
  StopCriteria = ['Manual Stop', 'Stop by live time', 'Stop by real time', 'Stop by counts']

  def __init__(self):
    if not self.initiated:  
      for v in self.StopCriteria:  self.gui.StopCriteriaComboBox.addItem(v, userData = self.StopCriteria.index(v))
      self.gui.StartStopAcqButton.clicked.connect(self.__Acquisition)
      self.gui.ClearAcqButton.clicked.connect(self.__Clear_Acquisition)
      self.gui.SaveAcqButton.clicked.connect( self.__Save_Acquisition)
      self.gui.AcqNumberSpinBox.valueChanged.connect( self.__Stop_Value)
      self.gui.ThresholdASpinBox.valueChanged.connect(self.__Ranges)
      self.gui.ThresholdBSpinBox.valueChanged.connect(self.__Ranges)
      self.gui.ThresholdCSpinBox.valueChanged.connect(self.__Ranges)
      self.gui.UpdateTimeSpinBox.valueChanged.connect(self.__Update_Time)
      self.gui.StopCriteriaComboBox.currentIndexChanged.connect(self.__Stop_Criteria)
      self.hide = [self.gui.StopCriteriaComboBox, self.gui.AcqNumberSpinBox,  self.gui.UpdateTimeSpinBox,
                   self.gui.ThresholdASpinBox,    self.gui.ThresholdBSpinBox, self.gui.ThresholdCSpinBox]
      self.initiated = True
    self.Read_Scope_Parameters()
    self.Read_Acquisition_Parameters()
    self.DPP.acqMode = 1 # Waveform = 0, Histogram = 1

  def Init_Acquisition_Parameters(self):
    self.AcqPar = {'StopCriteria':1, 
                   'StopValue': [1, 10, 100, 1000],
                   'StopSuffix':[' mouse click', ' seconds', ' seconds', ' counts'], 
                   'UpdateTime':1.0, 
                   'ThresholdABC':[100, 1000, 10000, self.HistoSize]}

  def Save_Acquisition_Parameters(self):
    with open('acquisition.pickle', 'wb') as fp: pickle.dump(self.AcqPar, fp)
    
  def Read_Acquisition_Parameters(self):
    try:     
      with open('acquisition.pickle', 'rb') as fp: self.AcqPar = pickle.load(fp)
    except FileNotFoundError: self.Init_Acquisition_Parameters()
    i = self.AcqPar['StopCriteria']
    self.__SetInitialField(self.gui.StopCriteriaComboBox, i)
    self.__SetValue(self.gui.AcqNumberSpinBox, self.AcqPar['StopValue'][i], self.AcqPar['StopSuffix'][i], bool(i))
    self.__SetValue(self.gui.ThresholdASpinBox, self.AcqPar['ThresholdABC'][0], ' ', True)
    self.__SetValue(self.gui.ThresholdBSpinBox, self.AcqPar['ThresholdABC'][1], ' ', True)
    self.__SetValue(self.gui.ThresholdCSpinBox, self.AcqPar['ThresholdABC'][2], ' ', True)
    self.__SetValue(self.gui.UpdateTimeSpinBox, self.AcqPar['UpdateTime'],     ' s', True)

  def __SetValue(self, SB, V, S, E):
    SB.blockSignals(True); SB.setValue(V); SB.setSuffix(S); SB.setEnabled(E); SB.blockSignals(False)  

  def __SetInitialField(self, A, B): 
    for index in range(A.count()):
      if A.itemData(index) == B: A.setCurrentIndex(index); break

  def __Acquisition(self):
    button  = self.gui.StartStopAcqButton.text()
    if  'Start' in button: 
      self.start = True
      for el in self.hide: el.setEnabled(False)
      self.gui.StartStopAcqButton.setText('Stop')
      tt = int(1000*self.AcqPar['UpdateTime']) # seconds -> milliseconds
      self.gui.timerB.start(tt)
      self.gui.timerB.timeout.connect(self.__Acquire)
    elif 'Stop' in button: 
      self.gui.timerB.timeout.disconnect(self.__Acquire)
      self.gui.timerB.stop()
      self.DPP.StopAcquisition(   self.DPP.CH)
      self.gui.StartStopAcqButton.setText('Start')
      for el in self.hide: el.setEnabled(True)

  def __Acquire(self):
    if self.gui.tab_SP.isHidden(): self.__Acquisition()
    R = self.DPP.GetCurrentHistogram(self.DPP.CH, self.Histogram)
    
    if not R['acqStatus']:  # not aquiring now  
      if self.start:
        self.DPP.StartAcquisition( self.DPP.CH)
        self.start = False
      else: self.__Acquisition() 
    
    R1 = sum(self.Histogram[self.AcqPar['ThresholdABC'][0]: self.AcqPar['ThresholdABC'][1]])
    R2 = sum(self.Histogram[self.AcqPar['ThresholdABC'][1]: self.AcqPar['ThresholdABC'][2]]) 
    R3 = sum(self.Histogram[self.AcqPar['ThresholdABC'][2]: self.AcqPar['ThresholdABC'][3]])
    print(R)
    print(R1, R2, R3)

  def __Clear_Acquisition(self):      
    self.DPP.ClearCurrentHistogram(self.DPP.CH)

  def __Save_Acquisition(self):      pass

  def __Stop_Criteria(self, index):
    c = self.gui.StopCriteriaComboBox.itemData(index)
    self.AcqPar['StopCriteria'] = c
    if c is 0:
      self.gui.AcqNumberSpinBox.setMinimum( 1); self.gui.AcqNumberSpinBox.setMaximum(1)
    elif c in [1,2]: 
      self.gui.AcqNumberSpinBox.setMinimum(10); self.gui.AcqNumberSpinBox.setMaximum(10000)
    elif c is 3:     
      self.gui.AcqNumberSpinBox.setMinimum(10); self.gui.AcqNumberSpinBox.setMaximum(10000000)
    self.gui.AcqNumberSpinBox.setValue(self.AcqPar['StopValue'][c])
    self.gui.AcqNumberSpinBox.setSuffix(self.AcqPar['StopSuffix'][c])
    self.gui.AcqNumberSpinBox.setEnabled(bool(c))
    self.DPP.SetStopCriteria(self.DPP.CH, c, self.AcqPar['StopValue'][c])
      
  def __Stop_Value(self):    
    self.AcqPar['StopValue'][self.AcqPar['StopCriteria']] = self.gui.AcqNumberSpinBox.value()
    self.DPP.SetStopCriteria(self.DPP.CH, self.AcqPar['StopCriteria'], self.AcqPar['StopValue'][self.AcqPar['StopCriteria']])
    print(self.DPP.GetStopCriteria(self.DPP.CH))

  def __Update_Time(self):
     self.AcqPar['UpdateTime'] = self.gui.UpdateTimeSpinBox.value()
    
  def __Ranges(self):
    self.AcqPar['ThresholdABC'][0] = self.gui.ThresholdASpinBox.value()
    self.AcqPar['ThresholdABC'][1] = self.gui.ThresholdBSpinBox.value()
    self.AcqPar['ThresholdABC'][2] = self.gui.ThresholdCSpinBox.value()
    self.gui.ThresholdASpinBox.setMinimum(0);                                self.gui.ThresholdASpinBox.setMaximum(self.AcqPar['ThresholdABC'][1]-1)
    self.gui.ThresholdBSpinBox.setMinimum(self.AcqPar['ThresholdABC'][0]+1); self.gui.ThresholdBSpinBox.setMaximum(self.AcqPar['ThresholdABC'][2]-1)
    self.gui.ThresholdCSpinBox.setMinimum(self.AcqPar['ThresholdABC'][1]+1); self.gui.ThresholdCSpinBox.setMaximum(self.AcqPar['ThresholdABC'][3]-1)

#    print('N=', self.DPP.GetTotalNumberOfHistograms(self.DPP.CH))
#    print('I=', self.DPP.GetCurrentHistogramIndex(self.DPP.CH))
#    print('S=', self.DPP.GetHistogramSize(self.DPP.CH, 0))
    """
    print(self.DPP.GetStopCriteria(self.DPP.CH))
    status = self.DPP.IsChannelAcquiring(self.DPP.CH)
    if status is 0: 
      self.DPP.StartAcquisition(self.DPP.CH)
      for i in range(10):
        R = self.DPP.GetCurrentHistogram(self.DPP.CH, self.Histogram)
        print(R)
        sleep(1)
    self.DPP.StopAcquisition(self.DPP.CH)
    R = self.DPP.GetCurrentHistogram(self.DPP.CH, self.Histogram)
    print(R)
    """

