from TABs.TAB_CF  import TAB_CF as CF
from TABs.TAB_HV  import TAB_HV as HV
from TABs.TAB_OS  import TAB_OS as OS
from TABs.TAB_SP  import TAB_SP as SP
import DPPLib

class TABs(CF, HV, OS, SP):
  
  def __init__(self, gui):
    self.gui = gui
    self.DPP = DPPLib.CAEN_DPP()
    self.gui.Tabs.setCurrentWidget(self.gui.tab_CF)
    CF.__init__(self)
    for i in [1,2,3]: self.gui.Tabs.setTabEnabled(i, False)
    self.gui.Tabs.currentChanged.connect(self.Tab_Changed)
    self.gui.menuWaveform_Settings.setDisabled(True)
    self.gui.Save_WF_Settings.triggered.connect(self.DPP.Save_DGTZ_Parameters)
    self.gui.Back_to_Saved_WF_Settings.triggered.connect(self.Read_Scope_Parameters)
    self.gui.Back_to_Default_WF_Settings.triggered.connect(self.Init_Scope_Parameters)

    self.gui.menuAcquisition_Settings.setDisabled(True)
    self.gui.Save_ACQ_Settings.triggered.connect(self.Save_Acquisition_Parameters)
    self.gui.Back_to_Saved_ACQ_Settings.triggered.connect(self.Read_Acquisition_Parameters)
    self.gui.Back_to_Default_ACQ_Settings.triggered.connect(self.Init_Acquisition_Parameters)

  def Tab_Changed(self,index):
    if   index==1: HV.__init__(self);  self.gui.timerA.start(1000)
    elif index==2: OS.__init__(self);  self.gui.timerA.stop()
    elif index==3: SP.__init__(self);  self.gui.timerA.stop()
    self.gui.menuWaveform_Settings.setDisabled(   index!=2)
    self.gui.menuAcquisition_Settings.setDisabled(index!=3)


