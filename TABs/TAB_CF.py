class TAB_CF:
  def __init__(self):
    for k,v in self.DPP.link.LinkTypes.items(): self.gui.LinkType.addItem(k,v)
    self.gui.Disconn.setChecked(True)
    self.DPP.Connection = False
    self.DPP.CH = None
    self.DPP.HVCH = None
    self.gui.Connect.toggled.connect(self.Connections)
    self.gui.InputComboBox.currentIndexChanged.connect(self.__Input_Channel_Select)
    self.gui.HVComboBox.currentIndexChanged.connect(   self.__HV_Channel_Select)


  def Connections(self):
    T = ['---' for i in range(8)]
    if self.gui.Connect.isChecked(): 
      self.DPP.link.LinkType = self.gui.LinkType.currentData()
      self.DPP.linknum       = self.gui.LinkNumber.value()
      self.DPP.InitLibrary()
      if self.DPP.AddBoard():
        if self.DPP.GetDPPInfo():
          T[0] = self.DPP.boardInfo.ModelName.decode()
          T[1] = str(self.DPP.boardInfo.FamilyCode)
          T[2] = str(self.DPP.boardInfo.SerialNumber)
          T[3] = self.DPP.boardInfo.AMC_FirmwareRel.decode()
          T[4] = self.DPP.boardInfo.ROC_FirmwareRel.decode()
          T[5] = self.DPP.boardInfo.License.decode()
          T[6] = str(self.DPP.boardInfo.Channels)
          T[7] = str(self.DPP.boardInfo.HVChannels)
          self.gui.Connect.setText("Connected !")
          self.gui.Disconn.setText("Disconnect")
          self.DPP.Connection = True
          if self.DPP.boardInfo.Channels>0:
            for c in range(self.DPP.boardInfo.Channels):   self.gui.InputComboBox.addItem('Input channel: %d' % c, c)
            self.gui.Tabs.setTabEnabled(2, True)
            self.gui.Tabs.setTabEnabled(3, True)
          if self.DPP.boardInfo.HVChannels>2:
            for c in range(self.DPP.boardInfo.HVChannels): self.gui.HVComboBox.addItem('HV channel: %d' % c, c)
            self.gui.Tabs.setTabEnabled(1, True)
      else:
        self.gui.Disconn.setChecked(True)
    elif self.gui.Disconn.isChecked():
      self.gui.InputComboBox.clear()
      self.gui.HVComboBox.clear()
      self.Disconnect()
    self.gui.ModelName.setText(   'Model Name: '        + T[0])
    self.gui.FamilyCode.setText(  'Family Code: '       + T[1])
    self.gui.SerialNumber.setText('Serial Number: '     + T[2])
    self.gui.AMCFirmware.setText( 'AMC: '               + T[3])
    self.gui.ROCFirmware.setText( 'ROC: '               + T[4])
    self.gui.License.setText(     'License: '           + T[5])
    self.gui.Channels.setText(    'Number of channels: '+ T[6])
    self.gui.HVChannels.setText(  'Num of HV channels: '+ T[7])

  def Disconnect(self):
    for i in [1,2,3]: self.gui.Tabs.setTabEnabled(i, False)
    self.DPP.EndLibrary()
    self.DPP.Connection = False
    self.gui.Connect.setText("Connect")
    self.gui.Disconn.setText("Disconnected")
    self.gui.Disconn.setChecked(True)

  def __Input_Channel_Select(self, index): self.DPP.CH = index
	
  def __HV_Channel_Select(self, index):    self.DPP.HVCH = index

	
