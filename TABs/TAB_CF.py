class TAB_CF:
  def __init__(self):
    for k,v in self.DPP.link.LinkTypes.items():
      self.gui.LinkType.addItem(k,v)
    self.gui.Disconn.setChecked(True)
    self.DPP.Connection = False
    self.Update_Tabs()
    self.gui.Connect.toggled.connect(self.Connections)
    self.gui.Select_CH0.toggled.connect(self.Channel_Select)
    self.gui.Select_CH0.setEnabled(False)
    self.gui.Select_CH1.setEnabled(False)

  def Connections(self):
    T = ['---', '---', '---', '---', '---']
    if self.gui.Connect.isChecked(): 
      self.DPP.link.LinkType = self.gui.LinkType.currentData()
      self.DPP.linknum       = self.gui.LinkNumber.value()
      self.DPP.InitLibrary()
      if self.DPP.AddBoard():
        if self.DPP.GetDPPInfo():
          T[0] = self.DPP.boardInfo.ModelName.decode()
          T[1] = str(self.DPP.boardInfo.SerialNumber)
          T[2] = self.DPP.boardInfo.AMC_FirmwareRel.decode()
          T[3] = self.DPP.boardInfo.ROC_FirmwareRel.decode()
          T[4] = self.DPP.boardInfo.License.decode()
          self.gui.Connect.setText("Connected !")
          self.gui.Disconn.setText("Disconnect")
          self.DPP.Connection = True
          self.DPP.CH = 0
          self.gui.Select_CH0.setEnabled(True)
          self.gui.Select_CH1.setEnabled(True)
          self.gui.Select_CH0.setChecked(True)
      else:
        self.gui.Disconn.setChecked(True)
    elif self.gui.Disconn.isChecked():
      self.Disconnect()
    self.gui.ModelName.setText(   T[0])
    self.gui.SerialNumber.setText(T[1])
    self.gui.AMCFirmware.setText( T[2])
    self.gui.ROCFirmware.setText( T[3])
    self.gui.License.setText(     T[4])
    self.Update_Tabs()

  def Disconnect(self):
    self.DPP.EndLibrary()
    self.DPP.Connection = False
    self.gui.Connect.setText("Connect")
    self.gui.Disconn.setText("Disconnected")
    self.gui.Disconn.setChecked(True)
      
	
  def Channel_Select(self):
    if   self.gui.Select_CH0.isChecked(): self.DPP.CH = 0
    elif self.gui.Select_CH1.isChecked(): self.DPP.CH = 1
      



