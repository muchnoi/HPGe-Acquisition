from ctypes import byref, c_uint8, c_int16, c_int32, c_uint32, c_double
from ctypes import c_int32 as c_enum
from ctypes import memset, sizeof
from DPPLib.HEAD import MAX_GW, DPP_DgtzParams
import pickle

class DGTZ:

  def Read_DGTZ_Parameters(self):
    try:     
      with open('dgtz.pickle', 'rb') as fp: 
        self.inputRange, self.boardConfig = pickle.load(fp)
    except FileNotFoundError:        
      self.Init_DGTZ_Parameters()

  def Save_DGTZ_Parameters(self):
#    self.GetBoardConfiguration()
    with open('dgtz.pickle', 'wb') as fp: 
      pickle.dump([self.inputRange, self.boardConfig], fp)

  def Init_DGTZ_Parameters(self):
    DP = self.boardConfig
    # listMode default parameters
    DP.ListParams.enabled            = False
    DP.ListParams.saveMode           = 0 # CAENDPP_ListSaveMode_FileBinary
    DP.ListParams.fileName           = b"UNNAMED"
    DP.ListParams.maxBuffNumEvents   = 0
    DP.ListParams.saveMask           = 0xF
    # default board parameters
    DP.ChannelMask                   = 0x1 # it will be filled later
    DP.EventAggr                     = 0
    DP.IOlev                         = 0 # CAENDPP_IOLevel_NIM
    # Generic Writes to Registers
    DP.GWn                           = 0         # Number of Generic Writes
    memset(DP.GWaddr, 0, MAX_GW*sizeof(c_int32)) # List of addresses (length = 'GWn')
    memset(DP.GWdata, 0, MAX_GW*sizeof(c_int32)) # List of datas (length = 'GWn')
    memset(DP.GWmask, 0, MAX_GW*sizeof(c_int32)) # List of masks (length = 'GWn')
    # Waveform parameters default settings
    DP.WFParams.dualTraceMode        = 1
    DP.WFParams.vp1                  = 0         # CAENDPP_PHA_VIRTUALPROBE1_Input
    DP.WFParams.vp2                  = 2         # CAENDPP_PHA_VIRTUALPROBE2_TrapBLCorr
    DP.WFParams.dp1                  = 4         # CAENDPP_PHA_DigitalProbe1_Peaking
    DP.WFParams.dp2                  = 0         # CAENDPP_PHA_DigitalProbe2_Trigger
    DP.WFParams.recordLength         = c_int32(8192)
    DP.WFParams.preTrigger           = c_int32(1000)
    DP.WFParams.probeTrigger         = 0         # CAENDPP_PHA_PROBETRIGGER_MainTrig
    DP.WFParams.probeSelfTriggerVal  = c_int32(150)
    # Channel parameters
    for ch in [0,1]:
      DP.DCoffset[ch]                = 32767
      DP.PulsePolarity[ch]           = 0         # CAENDPP_PulsePolarityPositive
      # Coicidence parameters between channels
      DP.CoincParams[ch].CoincChMask = 0x0
      DP.CoincParams[ch].CoincLogic  = 0         # CAENDPP_CoincLogic_None
      DP.CoincParams[ch].CoincOp     = 0         # CAENDPP_CoincOp_OR
      DP.CoincParams[ch].MajLevel    = 0
      DP.CoincParams[ch].TrgWin      = 0
      # DPP Parameters
      DP.DPPParams.M[ch]             = 50000     # Signal Decay Time Constant [ns]
      DP.DPPParams.m[ch]             = 1000      # Trapezoid Flat Top  [ns]
      DP.DPPParams.k[ch]             = 3000      # Trapezoid Rise Time  [ns]
      DP.DPPParams.ftd[ch]           = 800       # Flat Top Delay  [ns]
      DP.DPPParams.a[ch]             = 4         # Trigger Filter smoothing factor
      DP.DPPParams.b[ch]             = 200       # Input Signal Rise time  [ns]
      DP.DPPParams.thr[ch]           = 50        # Trigger Threshold
      DP.DPPParams.nsbl[ch]          = 3         # Number of Samples for Baseline Mean
      DP.DPPParams.nspk[ch]          = 0         # Number of Samples for Peak Mean Calculation
      DP.DPPParams.pkho[ch]          = 0         # Peak Hold Off
      DP.DPPParams.blho[ch]          = 1000      # Base Line Hold Off
      DP.DPPParams.dgain[ch]         = 0         # Digital Probe Gain
      DP.DPPParams.enf[ch]           = 1.0       # Energy Nomralization Factor
      DP.DPPParams.decimation[ch]    = 0         # Decimation of Input Signal   
      DP.DPPParams.trgho[ch]         = 1300      # Trigger Hold Off
      # Reset Detector
      DP.ResetDetector[ch].Enabled   = 0
      DP.ResetDetector[ch].ResetDetectionMode = 0 # CAENDPP_ResetDetectionMode_Internal
      DP.ResetDetector[ch].thrhold   = 100
      DP.ResetDetector[ch].reslenmin = 2
      DP.ResetDetector[ch].reslength = 2000
      # Parameters for X770
      DP.DPPParams.X770_extra[ch].CRgain            = 0
      DP.DPPParams.X770_extra[ch].InputImpedance    = 0 # CAENDPP_InputImpedance_1K;
      DP.DPPParams.X770_extra[ch].TRgain            = 0
      DP.DPPParams.X770_extra[ch].SaturationHoldoff = 300
      DP.DPPParams.X770_extra[ch].energyFilterMode  = 0
      DP.DPPParams.X770_extra[ch].trigK             = 30
      DP.DPPParams.X770_extra[ch].trigm             = 10
      DP.DPPParams.X770_extra[ch].trigMODE          = 0
      DP.SpectrumControl[ch].SpectrumMode           = 0 # CAENDPP_SpectrumMode_Energy
      DP.SpectrumControl[ch].TimeScale              = 1
#    return DP
#    print(self.boardConfig.DPPParams.M[0], self.boardConfig.DPPParams.M[1])
#    self.boardConfig = DP
#    print(self.boardConfig.DPPParams.M[0], self.boardConfig.DPPParams.M[1])
#    self.Save_DGTZ_Parameters()

  def GetInputRange(self, ch):
    ir = c_enum()
    if self.RQ(self.dpplib.CAENDPP_GetInputRange(self.handle, c_int32(ch), byref(ir))):
      self.inputRange[ch] = ir.value
    else: return False

  def SetInputRange(self, ch):
    ir = c_enum(self.inputRange[ch])
    return self.RQ(self.dpplib.CAENDPP_SetInputRange(self.handle, c_int32(ch),   ir))

  def StartAcquisition(self, ch):
    return self.RQ(self.dpplib.CAENDPP_StartAcquisition(self.handle, c_int32(ch)))

  def StopAcquisition(self, ch):
    return self.RQ(self.dpplib.CAENDPP_StopAcquisition(self.handle, c_int32(ch)))

  def IsBoardAcquiring(self):
    R = self.RQ(self.dpplib.CAENDPP_IsBoardAcquiring(self.handle, self.boardId, byref(self.is_board_acq)))
    if R: return self.is_board_acq.value
    else: return False
    
  def IsChannelAcquiring(self, ch):
    AcqStatus = c_enum()
    R = self.RQ(self.dpplib.CAENDPP_IsChannelAcquiring(self.handle, c_int32(ch), byref(self.is_chann_acq)))
    if R: return self.is_chann_acq.value
    else: return False
    
  def GetWaveformLength(self, ch): 
    length  = c_uint32()
    R = self.RQ(self.dpplib.CAENDPP_GetWaveformLength(self.handle, c_int32(ch), byref(length)))
    if R: return length.value
    else: return False

  def GetWaveform(self, ch):
    ns = c_uint32()
    ts = c_double()
    R = self.RQ(self.dpplib.CAENDPP_GetWaveform(self.handle, c_int32(ch), 
                                                c_int16(self.trigger),  # 1 - Auto Trig
                                                byref(self.Traces.AT1),
                                                byref(self.Traces.AT2),
                                                byref(self.Traces.DT1),
                                                byref(self.Traces.DT2),
                                                byref(ns),   # number of samples read
                                                byref(ts)))  # one sample time
    if R: return [ns.value, ts.value]
    else: return [False,    False   ]

  def GetDAQInfo(self, ch): # Not Supported!
    R = self.RQ(self.dpplib.CAENDPP_GetDAQInfo(self.handle, c_int32(ch), byref(self.DAQ_Info)))
    print("DAQ Info: ****************")
    print("ACQStatus:",   self.DAQ_Info.ACQStatus) 
    print("RunState:",    self.DAQ_Info.RunState) 
    print("ElapsedTime:", self.DAQ_Info.RunElapsedTimeSec)
    
