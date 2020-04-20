from TABs.TAB_CF  import TAB_CF as CF
from TABs.TAB_HV  import TAB_HV as HV
from TABs.TAB_OS  import TAB_OS as OS
from TABs.TAB_SP  import TAB_SP as SP
import DPPLib

class TABs(CF, HV, OS, SP):
  
  def __init__(self, gui):
    self.gui = gui
    self.DPP = DPPLib.CAEN_DPP()
    CF.__init__(self)
    self.gui.Tabs.setCurrentWidget(self.gui.tab_CF)
#    self.gui.Tabs.currentChanged.connect(self.Select_Tab)
    self.gui.timerA.start(999)
    self.gui.timerA.timeout.connect(self.Update_Tabs)
    self.already_connected = False   
#  def Select_Tab(self):
#    if   self.gui.tab_HV.isVisible(): HV.__init__(self)
#    elif self.gui.tab_OS.isVisible(): OS.__init__(self)
#    elif self.gui.tab_SP.isVisible(): SP.__init__(self)
    
  def Update_Tabs(self):
    if self.gui.Connect.isChecked(): #self.DPP.Connection:
      if self.DPP.CheckBoardCommunication(): 
        if not self.already_connected:
          self.already_connected = True
          HV.__init__(self)
          OS.__init__(self)
        self.TABs123(True)
      else: 
        self.Disconnect()
        self.already_connected = False
    else: self.TABs123(False)
        
  def TABs123(self, v):     
    for i in [1,2,3]: self.gui.Tabs.setTabEnabled(i, v)

  def __del__(self):
    if self.DPP.Connection:  print("Close connection: ", self.DPP.EndLibrary())


