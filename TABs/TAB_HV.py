class TAB_HV:
  def __init__(self):
    model  = self.DPP.boardInfo.ModelName.decode()
    if   model[-1] == 'M': self.sign =  1 - 2*self.DPP.HVCH
    elif model[-1] == 'P': self.sign =  1
    elif model[-1] == 'N': self.sign = -1

    vmax  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].VMaxInfo.maximum
    vmin  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].VMaxInfo.minimum
    imax  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].ISetInfo.maximum
    imin  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].ISetInfo.minimum
    umax  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].RampUpInfo.maximum
    umin  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].RampUpInfo.minimum
    dmax  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].RampDownInfo.maximum
    dmin  = self.DPP.boardInfo.HVChannelInfo[self.DPP.HVCH].RampDownInfo.minimum
    self.gui.Title_0.setText("{} s/n {}, CH {}".format(model, self.DPP.boardInfo.SerialNumber, self.DPP.HVCH))
    self.gui.Title_1.setText("Vₘₐₓ= {} V, Iₘₐₓ= {} μA".format(int(vmax*self.sign), int(imax)))
    self.gui.VMax.setMaximum(    vmax);  self.gui.VMax.setMinimum(    vmin)
    self.gui.IMax.setMaximum(    imax);  self.gui.IMax.setMinimum(    imin)
    self.gui.RampUp.setMaximum(  umax);  self.gui.RampUp.setMinimum(  umin)
    self.gui.RampDown.setMaximum(dmax);  self.gui.RampDown.setMinimum(dmin)

    S = self.DPP.GetHVChannelPowerOn(self.DPP.HVCH)
    self.gui.V_ON.setChecked(S)
    self.gui.V_OFF.setChecked(not S)
    C = self.DPP.GetHVChannelConfiguration(self.DPP.HVCH)
    self.gui.VSet.setMaximum(          int(C['VMax']))
    self.__SetValue(self.gui.VSet,     int(C['VSet']))
    self.__SetValue(self.gui.VMax,     int(C['VMax']))
    self.__SetValue(self.gui.IMax,     int(C['ISet']))
    self.__SetValue(self.gui.RampUp,   int(C['RampUp']))
    self.__SetValue(self.gui.RampDown, int(C['RampDown']))

    self.gui.V_ON.toggled.connect(      self.__Switch_HV)
    self.gui.VSet.valueChanged.connect(    self.__Set_HV)
    self.gui.VMax.valueChanged.connect(    self.__Set_HV)
    self.gui.IMax.valueChanged.connect(    self.__Set_HV)
    self.gui.RampUp.valueChanged.connect(  self.__Set_HV)
    self.gui.RampDown.valueChanged.connect(self.__Set_HV)
    self.gui.timerA.timeout.connect(    self.__Update_HV)

  def __SetValue(self, SB, V):
    SB.blockSignals(True); SB.setValue(V); SB.blockSignals(False)  

  def __Update_HV(self):
    if self.gui.tab_HV.isVisible(): 
      V, I = self.DPP.ReadHVChannelMonitoring(self.DPP.HVCH)
      if V is False:
        self.Disconnect()
      else:
        self.gui.VAct.display(self.sign*V); self.gui.IAct.display(I)
        if self.DPP.GetHVChannelStatus(0) == 'Disabled': 
          self.gui.V_OFF.setChecked(True)
          self.gui.V_ON.setText("INH")
        
  def __Switch_HV(self):
    if   self.gui.V_OFF.isChecked(): self.DPP.SetHVChannelPowerOn(self.DPP.HVCH, 0)
    elif self.gui.V_ON.isChecked():  self.DPP.SetHVChannelPowerOn(self.DPP.HVCH, 1)
    
  def __Set_HV(self):
    P = {}
    P['VSet']       = float(self.gui.VSet.value())
    P['VMax']       = float(self.gui.VMax.value())
    P['ISet']       = float(self.gui.IMax.value())
    P['RampUp']     = float(self.gui.RampUp.value())
    P['RampDown']   = float(self.gui.RampDown.value())
    P['PWDownMode'] = int(0)
    self.DPP.SetHVChannelConfiguration(self.DPP.HVCH, P)
    self.DPP.SetHVChannelVMax(self.DPP.HVCH, P['VMax'])
    self.gui.VSet.setMaximum(P['VMax'])
#    print('set', self.DPP.HVCH)
    

