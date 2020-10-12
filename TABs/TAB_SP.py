from ctypes import c_int32
import pickle, time, gzip, os, configparser

class TAB_SP:
  __initiated  = False
  HistoSize    = 16384
  PageStep     = HistoSize-1
  HistoType    = c_int32*HistoSize # length of a histogram
  Histogram    = HistoType()
  StopCriteria = [' Manual Stop', ' Stop by live time', ' Stop by real time', ' Stop by counts']
  Integrals    = [[0,  0,  0 ], [0,  0,  0 ]]
  LiveTimes    = [0.0, 0.0]
  ScaleSize    = 512
  configure    = configparser.ConfigParser()
  keV          = 1.0

  def __init__(self):
    if not self.__initiated:
      self.configure.read('environment.cfg')
      self.data_folder = self.configure.get('Paths','data_folder')
      self.Progress  = 0  
      self.ScaleList = [[0 for i in range(self.ScaleSize)] for j in range(3)]
      self.ScalesMax = [0, 0, 0]
      for v in self.StopCriteria:  self.gui.StopCriteriaComboBox.addItem(v, userData = self.StopCriteria.index(v))
      for v in range(9):    self.gui.ZoomComboBox.addItem(' Zoom: {}x '.format(1<<v), userData = v)
      self.gui.HistogramScrollBar.setMinimum(0)
      self.gui.HistogramScrollBar.setMaximum(0)
      self.gui.HistogramScrollBar.setPageStep(self.HistoSize)
      self.gui.ZoomComboBox.currentIndexChanged.connect(self.__Zoom)
      self.gui.HistogramScrollBar.valueChanged.connect(self.__Shift)
      self.gui.StartStopAcqButton.clicked.connect(self.__Acquisition)
      self.gui.ClearAcqButton.clicked.connect(self.__Clear_Acquisition)
      self.gui.SaveAcqButton.clicked.connect( self.__Save_Acquisition)
      self.gui.AcqNumberSpinBox.valueChanged.connect( self.__Stop_Value)
      self.gui.ThresholdASpinBox.valueChanged.connect(self.__Ranges)
      self.gui.ThresholdBSpinBox.valueChanged.connect(self.__Ranges)
      self.gui.ThresholdCSpinBox.valueChanged.connect(self.__Ranges)
      self.gui.UpdateTimeSpinBox.valueChanged.connect(self.__Update_Time)
      self.gui.StopCriteriaComboBox.currentIndexChanged.connect(self.__Stop_Criteria)
      self.gui.SpectrumRadioButton.toggled.connect(self.__Set_View)

      self.gui.GainCheckBox.toggled.connect(self.__Set_keV)
      self.gui.GainSpinBox.valueChanged.connect(self.__Set_keV)

      self.hide = [self.gui.StopCriteriaComboBox, self.gui.AcqNumberSpinBox,  self.gui.UpdateTimeSpinBox,
                   self.gui.ThresholdASpinBox,    self.gui.ThresholdBSpinBox, self.gui.ThresholdCSpinBox, 
                   self.gui.SaveAcqButton, self.gui.GainCheckBox, self.gui.GainSpinBox]
      self.__initiated = True
      self.last_response = self.prev_response = None
    self.Read_Scope_Parameters()
    self.DPP.acqMode = 1 # Waveform = 0, Histogram = 1
    self.Read_Acquisition_Parameters()

  def Init_Acquisition_Parameters(self):
    self.AcqPar = {'StopCriteria':1, 
                   'StopValue': [1, 60, 60, 10000],
                   'StopSuffix':[' mouse click', ' seconds', ' seconds', ' counts'], 
                   'UpdateTime':1.0, 
                   'ThresholdABC':[100, 1000, 10000, self.HistoSize],
                   'Gain': 1.0}

  def Save_Acquisition_Parameters(self):
    with open('acquisition.pickle', 'wb') as fp: pickle.dump(self.AcqPar, fp)
    
  def Read_Acquisition_Parameters(self):
    try:     
      with open('acquisition.pickle', 'rb') as fp: self.AcqPar = pickle.load(fp)
    except FileNotFoundError: self.Init_Acquisition_Parameters()
    i = self.AcqPar['StopCriteria']
    self.__SetInitialField(self.gui.StopCriteriaComboBox, i)
    self.__SetInitialField(self.gui.ZoomComboBox, 0)
    self.gui.ProgressBar.setValue(0)
    self.gui.DeadTimeBar.setValue(0)

    C = self.DPP.GetHVChannelConfiguration(self.DPP.CH)
    self.gui.UBar.setRange(0, int(C['VMax']));  self.gui.UBar.setFormat("%v V")
    self.gui.IBar.setRange(0, int(C['ISet']));  self.gui.IBar.setFormat("%v μA")

    self.__SetValue(self.gui.AcqNumberSpinBox,  self.AcqPar['StopValue'][i], self.AcqPar['StopSuffix'][i], bool(i))
    self.__SetValue(self.gui.UpdateTimeSpinBox, self.AcqPar['UpdateTime'],     ' s', True)
    self.__SetValue(self.gui.GainSpinBox,       self.AcqPar['Gain'],      ' keV/ch', True)
    self.gui.SpectrumRadioButton.setChecked(True)
    self.gui.ACheckBox.setChecked(True)
    self.gui.BCheckBox.setChecked(True)
    self.gui.CCheckBox.setChecked(True)
    self.gui.GainCheckBox.setChecked(False)
    self.Visualize = 'spectrum'
    self.__Set_keV()
    self.gui.AcqWidget.Prepare(self)
    self.gui.AcqWidget.Show_Spectrum()
  
  def __SetValue(self, SB, V, S, E):
    SB.blockSignals(True); SB.setValue(V); SB.setSuffix(S); SB.setEnabled(E); SB.blockSignals(False)  

  def __SetInitialField(self, A, B): 
    for index in range(A.count()):
      if A.itemData(index) == B: A.setCurrentIndex(index); break

  def __Set_keV(self):
    self.AcqPar['Gain'] = self.gui.GainSpinBox.value()
    if self.gui.GainCheckBox.isChecked(): self.keV = self.AcqPar['Gain']
    else:                                 self.keV = 1.0
    self.gui.AcqWidget.Show_Spectrum()
    if self.keV == 1.0:
      self.__SetValue(self.gui.ThresholdASpinBox, self.AcqPar['ThresholdABC'][0], ' ch',  True)
      self.__SetValue(self.gui.ThresholdBSpinBox, self.AcqPar['ThresholdABC'][1], ' ch',  True)
      self.__SetValue(self.gui.ThresholdCSpinBox, self.AcqPar['ThresholdABC'][2], ' ch',  True)
    else:
      self.__SetValue(self.gui.ThresholdASpinBox, self.AcqPar['ThresholdABC'][0]*self.keV, ' keV', True)
      self.__SetValue(self.gui.ThresholdBSpinBox, self.AcqPar['ThresholdABC'][1]*self.keV, ' keV', True)
      self.__SetValue(self.gui.ThresholdCSpinBox, self.AcqPar['ThresholdABC'][2]*self.keV, ' keV', True)
      

  def __Set_View(self, index):
    if index: 
      self.gui.stackedWidget.setCurrentIndex(0)
      self.Visualize = 'spectrum'
      self.gui.AcqWidget.Prepare(self)
      self.gui.AcqWidget.Show_Spectrum()
    else:
      self.gui.stackedWidget.setCurrentIndex(1)
      self.Visualize = 'scaler'
      self.gui.AcqWidget.Prepare(self)
      self.gui.AcqWidget.Show_Counting()
    
  def __Zoom(self,index):
    vl = self.gui.HistogramScrollBar.value() + self.PageStep//2 
    self.PageStep = self.HistoSize//(1<<index)-1
    self.gui.HistogramScrollBar.setMaximum(self.HistoSize-self.PageStep-1)
    self.gui.HistogramScrollBar.setPageStep(self.PageStep)
    self.gui.HistogramScrollBar.setValue(vl - self.PageStep//2)
    self.gui.AcqWidget.Show_Spectrum()
#    print(self.PageStep, self.gui.HistogramScrollBar.value(), self.gui.HistogramScrollBar.value()+self.PageStep)

  def __Shift(self):    
    self.gui.AcqWidget.Show_Spectrum()
    
  def __Acquisition(self):
    button  = self.gui.StartStopAcqButton.text()
    if  'Start' in button: 
      self.start = True
      for el in self.hide: el.setEnabled(False)
      if self.Progress==100: self.__Clear_Histogram()
      self.gui.StartStopAcqButton.setText('Stop')
      self.gui.AcqWidget.Prepare(self)
      tt = int(1000*self.AcqPar['UpdateTime']) # seconds -> milliseconds
      self.Time_Start = time.localtime()
      self.gui.timerB.start(tt); self.gui.timerB.timeout.connect(self.__Acquire)
      for i in [0,1,2]: self.gui.Tabs.setTabEnabled(i, False)
    elif 'Stop' in button: 
      self.__Stop_Action()
      for el in self.hide: el.setEnabled(True)
      for i in [0,1,2]: self.gui.Tabs.setTabEnabled(i, True)

  def __Stop_Action(self):
    self.gui.timerB.timeout.disconnect(self.__Acquire); self.gui.timerB.stop()
    self.DPP.StopAcquisition(   self.DPP.CH)
    self.Time_Stop = time.localtime()
    self.gui.StartStopAcqButton.setText('Start')

  def __Acquire(self):
    if self.gui.tab_SP.isHidden(): self.__Acquisition()
    R = self.DPP.GetCurrentHistogram(self.DPP.CH, self.Histogram)

    if not R['acqStatus']:  # if not aquiring now  
      if self.start:        # if acquisition is just started
        self.DPP.StartAcquisition( self.DPP.CH)
        self.start = False
      elif self.gui.AutoRestartCheckBox.isChecked(): # if acquisition is finished, start new one
        print('auto mode')
        self.__Stop_Action()
        self.__Save_Acquisition()
        self.__Acquisition()
      else: self.__Acquisition() # if acquisition is finished, stop it
    
    V, I = self.DPP.ReadHVChannelMonitoring(self.DPP.CH)
    self.gui.UBar.setValue(V); self.gui.IBar.setValue(I)
    
    if R['real_t']>0:
      if   self.AcqPar['StopCriteria'] == 0: self.Progress = 0
      elif self.AcqPar['StopCriteria'] == 1: self.Progress = 100 * (R['real_t'] - R['dead_t']) // self.AcqPar['StopValue'][1]
      elif self.AcqPar['StopCriteria'] == 2: self.Progress = 100 *  R['real_t']                // self.AcqPar['StopValue'][2]
      elif self.AcqPar['StopCriteria'] == 3: self.Progress = 100 *  R['counts']                // self.AcqPar['StopValue'][3]
      self.gui.ProgressBar.setValue(self.Progress)
      self.gui.DeadTimeBar.setValue(100*R['dead_t'] // R['real_t'])
    
    self.LiveTimes[1] = R['real_t'] - R['dead_t'];  dT = self.LiveTimes[1] - self.LiveTimes[0]; self.LiveTimes[0] = self.LiveTimes[1]
    if dT>0.0:
      for r in [0,1,2]:
        self.Integrals[1][r] = sum(self.Histogram[self.AcqPar['ThresholdABC'][r]: self.AcqPar['ThresholdABC'][r+1]])
        rate = int(float(self.Integrals[1][r] - self.Integrals[0][r])/dT)
        if rate >= 0:
          tmp = self.ScaleList[r][0]
          self.ScaleList[r].pop(0)
          self.ScaleList[r].append(rate)
          if self.ScalesMax[r] == tmp: self.ScalesMax[r] = max(                   self.ScaleList[r]    )
          else:                        self.ScalesMax[r] = max(self.ScalesMax[r], self.ScaleList[r][-1])
        self.Integrals[0][r] = self.Integrals[1][r]
    if 'spectrum' in self.Visualize:  self.gui.AcqWidget.Show_Spectrum()
    else:                             self.gui.AcqWidget.Show_Counting()
    self.last_response = R

  def __Clear_Acquisition(self):      
    if self.gui.SpectrumRadioButton.isChecked():
      self.__Clear_Histogram()
    else:
      self.ScaleList = [[0   for i in range(self.ScaleSize)] for j in range(3)]
      self.ScalesMax = [0, 0, 0]
      self.gui.AcqWidget.Show_Counting()
  
  def __Clear_Histogram(self):
    self.Progress = 0
    self.Time_Start = time.localtime()
    self.gui.ProgressBar.setValue(0)
    self.gui.DeadTimeBar.setValue(0)
    self.DPP.ClearCurrentHistogram(self.DPP.CH)
    self.DPP.GetCurrentHistogram(self.DPP.CH, self.Histogram)
    self.gui.AcqWidget.Prepare(self)
    self.gui.AcqWidget.Show_Spectrum()

  def __Save_Acquisition(self):
    if self.last_response == self.prev_response:
      self.gui.statusBar().showMessage('Nothing was saved')
      return

    self.gui.statusBar().showMessage('Saving new file...')
    folder = '%s/%4d/%04d%02d%02d' % (self.data_folder, self.Time_Stop.tm_year, self.Time_Stop.tm_year, self.Time_Start.tm_mon, self.Time_Start.tm_mday)
    if not os.path.exists(folder): os.makedirs(folder)
    filename = folder + '/%02d%02d%02d.wall.gz' % (self.Time_Stop.tm_hour, self.Time_Stop.tm_min, self.Time_Stop.tm_sec)
    
    with gzip.open(filename, 'wb') as f:
      f.write(b'# Date        %4d%02d%02d\n' %  (self.Time_Start.tm_year, self.Time_Start.tm_mon, self.Time_Start.tm_mday))
      f.write(b'# eDate       %4d%02d%02d\n' %  (self.Time_Stop.tm_year,  self.Time_Stop.tm_mon,  self.Time_Stop.tm_mday))
      f.write(b'# Begin       %d\n'   % (self.Time_Start.tm_hour*3600 + self.Time_Start.tm_min*60 + self.Time_Start.tm_sec))
      f.write(b'# End         %d\n'   % (self.Time_Stop.tm_hour *3600 + self.Time_Stop.tm_min *60 + self.Time_Stop.tm_sec))
      f.write(b'# Treal       %.2f\n' % self.last_response['real_t'])
      f.write(b'# Tlive       %.2f\n' % (self.last_response['real_t'] - self.last_response['dead_t']))
      f.write(b'# ModelMCA    %s\n'   % self.DPP.boardInfo.ModelName)
      f.write(b'# SerialNumer %d\n'   % self.DPP.boardInfo.SerialNumber)
      f.write(b'# HV          %d\n'   % self.DPP.ReadHVChannelMonitoring(self.DPP.CH)[0])
      f.write(b'# LLD         %d\n'   % self.DPP.boardConfig.DPPParams.thr[self.DPP.CH])
      f.write(b'# RangeADC    %d\n'   % self.DPP.inputRange[self.DPP.CH])
      f.write(b'# FineGain    %.5f\n' % self.DPP.boardConfig.DPPParams.enf[ self.DPP.CH])
      f.write(b'# OffsetDC    %d\n'   % self.DPP.boardConfig.DCoffset[self.DPP.CH])
      f.write(b'# RiseTime    %d\n'   % self.DPP.boardConfig.DPPParams.k[   self.DPP.CH])
      f.write(b'# DecayTime   %d\n'   % self.DPP.boardConfig.DPPParams.M[   self.DPP.CH])
      f.write(b'# FlatTop     %d\n'   % self.DPP.boardConfig.DPPParams.m[   self.DPP.CH])
      f.write(b'# PeakDelay   %d\n'   % self.DPP.boardConfig.DPPParams.ftd[ self.DPP.CH])
      f.write(b'# PeakHoldoff %d\n'   % self.DPP.boardConfig.DPPParams.pkho[self.DPP.CH])
      f.write(b'# BaseHoldoff %d\n'   % self.DPP.boardConfig.DPPParams.blho[self.DPP.CH])
      for c in range(self.HistoSize):  f.write(b'%d\n' % self.Histogram[c])

#      print (self.DPP.GetInfoDict("InputRangeNum", "InputRanges"))
    self.gui.statusBar().showMessage('New file %s was saved on %s' % (filename, time.asctime()))
    self.prev_response = self.last_response
#    print(time.asctime(self.Time_Start), time.mktime(self.Time_Start))
#    print(time.asctime(self.Time_Stop ), time.mktime(self.Time_Stop ))

  def __Stop_Criteria(self, index):
    c = self.gui.StopCriteriaComboBox.itemData(index)
    self.AcqPar['StopCriteria'] = c
    if c == 0:
      self.gui.AcqNumberSpinBox.setMinimum( 1); self.gui.AcqNumberSpinBox.setMaximum(1)
    elif c in [1,2]: 
      self.gui.AcqNumberSpinBox.setMinimum(10); self.gui.AcqNumberSpinBox.setMaximum(10000)
    elif c == 3:     
      self.gui.AcqNumberSpinBox.setMinimum(10); self.gui.AcqNumberSpinBox.setMaximum(10000000)
    self.gui.AcqNumberSpinBox.setValue(self.AcqPar['StopValue'][c])
    self.gui.AcqNumberSpinBox.setSuffix(self.AcqPar['StopSuffix'][c])
    self.gui.AcqNumberSpinBox.setEnabled(bool(c))
    self.DPP.SetStopCriteria(self.DPP.CH, c, self.AcqPar['StopValue'][c])
      
  def __Stop_Value(self):    
    self.AcqPar['StopValue'][self.AcqPar['StopCriteria']] = self.gui.AcqNumberSpinBox.value()
    self.DPP.SetStopCriteria(self.DPP.CH, self.AcqPar['StopCriteria'], self.AcqPar['StopValue'][self.AcqPar['StopCriteria']])
#    print(self.DPP.GetStopCriteria(self.DPP.CH))

  def __Update_Time(self):
     self.AcqPar['UpdateTime'] = self.gui.UpdateTimeSpinBox.value()
    
  def __Ranges(self):
    self.AcqPar['ThresholdABC'][0] = int(self.gui.ThresholdASpinBox.value()/self.keV)
    self.AcqPar['ThresholdABC'][1] = int(self.gui.ThresholdBSpinBox.value()/self.keV)
    self.AcqPar['ThresholdABC'][2] = int(self.gui.ThresholdCSpinBox.value()/self.keV)
#    self.gui.ThresholdASpinBox.setMinimum(0)                                
#    self.gui.ThresholdASpinBox.setMaximum( int((self.AcqPar['ThresholdABC'][1]-1)*self.keV) )
#    self.gui.ThresholdBSpinBox.setMinimum(int((self.AcqPar['ThresholdABC'][0]+1)*self.keV))
#    self.gui.ThresholdBSpinBox.setMaximum(int((self.AcqPar['ThresholdABC'][2]-1)*self.keV))
#    self.gui.ThresholdCSpinBox.setMinimum(int((self.AcqPar['ThresholdABC'][1]+1)*self.keV))
#    self.gui.ThresholdCSpinBox.setMaximum(int((self.AcqPar['ThresholdABC'][3]-1)*self.keV))


