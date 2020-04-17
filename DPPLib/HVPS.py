from ctypes import Structure, pointer, create_string_buffer
from ctypes import c_double, c_int32, c_uint16
from DPPLib.HEAD import DPP_HVChannelConfig

class HVPS:                   

  def GetHVChannelConfiguration(self, ch): 
    cfg  = DPP_HVChannelConfig()
    R = self.RQ(self.dpplib.CAENDPP_GetHVChannelConfiguration(self.handle, self.boardId, c_int32(ch), pointer(cfg)))
    if R: return {'VSet':cfg.VSet, 'ISet':cfg.ISet, 'RampUp':cfg.RampUp, 'RampDown':cfg.RampDown , 'VMax':cfg.VMax, 'PowerDownMode':cfg.PWDownMode}
    else: return False
  
  def SetHVChannelConfiguration(self, ch, params): 
    cfg = DPP_HVChannelConfig()
    cfg.VSet       = params['VSet']
    cfg.ISet       = params['ISet']
    cfg.RampUp     = params['RampUp']
    cfg.RampDown   = params['RampDown']
    cfg.VMax       = params['VMax']
    cfg.PWDownMode = params['PWDownMode']
    self.RQ(self.dpplib.CAENDPP_SetHVChannelConfiguration(self.handle, self.boardId, c_int32(ch), cfg ))
  
  def SetHVChannelVMax(self, ch, Vmax):    
    self.RQ(self.dpplib.CAENDPP_SetHVChannelVMax(self.handle, self.boardId, c_int32(ch), c_double(Vmax)))
  
  def GetHVChannelPowerOn(self, ch):
    on = c_int32()
    if self.RQ(self.dpplib.CAENDPP_GetHVChannelPowerOn(self.handle, self.boardId, c_int32(ch), pointer(on))): 
      return on.value
    else: return -1
  
  def SetHVChannelPowerOn(self, ch, on):   
    self.RQ(self.dpplib.CAENDPP_SetHVChannelPowerOn(self.handle, self.boardId, c_int32(ch), c_int32(on)))

  def ReadHVChannelMonitoring(self,ch):
    V, I = c_double(),c_double()
    if self.RQ(self.dpplib.CAENDPP_ReadHVChannelMonitoring(self.handle, self.boardId, c_int32(ch), pointer(V), pointer(I))):
      return (V.value, I.value)
    else: 
      return (False, False)
   
  def ReadHVChannelExternals(self, ch):
    V, I = c_double(),c_double()
    if self.RQ(self.dpplib.CAENDPP_ReadHVChannelExternals(self.handle, self.boardId, c_int32(ch), pointer(V), pointer(I))):
      return (V.value, I.value)
    else: return (0.0, 0.0)

  def GetHVChannelStatus(self, ch):
    status       = c_uint16()
    statusString = create_string_buffer(64)
    R = self.RQ(self.dpplib.CAENDPP_GetHVChannelStatus(self.handle, self.boardId, c_int32(ch), pointer(status)))
    if R:
      R = self.RQ(self.dpplib.CAENDPP_GetHVStatusString(self.handle, self.boardId, status, pointer(statusString)))
      if R:
        return statusString.value.decode()

