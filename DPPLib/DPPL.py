from ctypes import cdll, byref, c_char, c_double, c_uint32, c_int32, c_int16, c_ubyte, c_int32 as c_enum
from DPPLib.HEAD import DPP_ErrorCode, DPP_ConnectionParams
from DPPLib.HEAD import DPP_Info, DPP_Traces, DPP_Probes
from DPPLib.HEAD import DPP_DgtzParams, MAX_NUMCHB
from DPPLib.HVPS import HVPS
from DPPLib.DGTZ import DGTZ


class CAEN_DPP(HVPS, DGTZ):
  dpplib         = cdll.LoadLibrary("libCAENDPPLib.so")
  linknum        = 0
  acqMode        = 0 # Waveform = 0, Histogram = 1
  trigger        = 0 # Normal= 0, Auto = 1
  link           = DPP_ConnectionParams()
  link.LinkType  = link.LinkTypes['USB']
  boardConfig    = DPP_DgtzParams()
  inputRange     = [0]*MAX_NUMCHB
  inputRanges    = [float(e.replace(",",".")) for e in DPP_Probes["InputRanges"]]
  boardInfo      = DPP_Info()
  Traces         = DPP_Traces()
  is_board_acq   = c_int32()
  is_chann_acq   = c_enum()

  def RQ(self, s): 
    if not s:                          return True 
    else:     print(DPP_ErrorCode[s]); return False

  def InitLibrary(self):
    self.handle = c_int32(-1)
    return self.RQ(self.dpplib.CAENDPP_InitLibrary(byref(self.handle)))

  def AddBoard(self):           
    self.boardId = c_int32()
    self.link.LinkNum   = c_int32(self.linknum)
    return self.RQ(self.dpplib.CAENDPP_AddBoard(self.handle, self.link, byref(self.boardId)))

  def EndLibrary(self): 
    return self.RQ(self.dpplib.CAENDPP_EndLibrary(self.handle))

  def ResetConfiguration(self): 
    return self.RQ(self.dpplib.CAENDPP_ResetConfiguration(self.handle, self.boardId))

  def GetDPPInfo(self): 
    return self.RQ(self.dpplib.CAENDPP_GetDPPInfo(self.handle, self.boardId, byref(self.boardInfo)))

  def CheckBoardCommunication(self):
    return self.RQ(self.dpplib.CAENDPP_CheckBoardCommunication(self.handle, self.boardId))

  def GetInfoDict(self, attr_number, attr_list):
    R = {}    
    for r in range(getattr(self.boardInfo, attr_number)):
      num = getattr(self.boardInfo, attr_list)[r]
      name = DPP_Probes[attr_list][r]; R[name] = num
    return R
      
  def GetBoardConfiguration(self):
    self.acqcMode = c_enum(self.acqMode)
    return self.RQ(self.dpplib.CAENDPP_GetBoardConfiguration(self.handle, self.boardId, byref(self.acqcMode), byref(self.boardConfig)))

  def SetBoardConfiguration(self):
    self.acqcMode = c_enum(self.acqMode)
    return self.RQ(self.dpplib.CAENDPP_SetBoardConfiguration(self.handle, self.boardId,       self.acqcMode,        self.boardConfig))
      
  def Board_Reconfigure(self, ch):
    status = self.IsChannelAcquiring(ch)
    if status != 0: self.StopAcquisition(ch)
    self.SetBoardConfiguration()
    if status != 0: self.StartAcquisition(ch)



