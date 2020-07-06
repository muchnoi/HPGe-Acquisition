from ctypes import Structure, c_int32 as c_enum
from ctypes import c_ubyte, c_char, c_uint8, c_int16, c_uint32, c_int32, c_int64, c_float, c_double

DPP_ErrorCode = {  0 : "Operation completed successfully", 
                -100 : "Unspecified error",
                -101 : "Too many instances",
                -102 : "Process fail",
                -103 : "Read fail",
                -104 : "Write fail",
                -105 : "Invalid response",
                -106 : "Invalid library handle",
                -107 : "Configuration error",
                -108 : "Board Init failed",
                -109 : "Timeout error",
                -110 : "Invalid parameter",
                -111 : "Not in Waveforms Mode",
                -112 : "Not in Histogram Mode",
                -113 : "Not in List Mode",
                -114 : "Not yet implemented",
                -115 : "Board not configured",
                -116 : "Invalid board index",
                -117 : "Invalid channel index",
                -118 : "Invalid board firmware",
                -119 : "No board added",
                -120 : "Acquisition Status is not compliant with the function called",
                -121 : "Out of memory",
                -122 : "Invalid board channel index",
                -123 : "No valid histogram allocated",
                -124 : "Error opening the list dumper",
                -125 : "Error starting acquisition for a board",
                -126 : "The given channel is not enabled",
                -127 : "Invalid command",
                -128 : "Invalid number of bins",
                -129 : "Invalid Histogram Index",
                -130 : "The feature is not supported by the given board/channel",
                -131 : "The given histogram is in invalid state (e.g. 'done' while it shouldn't)",
                -132 : "Cannot switch to ext histo, no more histograms available",
                -133 : "The selected board doesn't support HV Channels",
                -134 : "Invalid HV channel index",
                -135 : "Error Sending Message through Socket",
                -136 : "Error Receiving Message from Socket",
                -137 : "Cannot get Board's acquisition thread",
                -138 : "Cannot decode waveform from buffer", 
                -139 : "Error Opening the digitizer",
                -140 : "Requested a feature incompatible with board's Manufacture",
                -141 : "Autoset Status is not compliant with the requested feature",
                -142 : "Autoset error looking for signal parameters",
                -143 : "Calibration Error",
                -144 : "Event read error"}

DPP_Probes = {"SupportedVirtualProbes1" : ["Input", "RC-CR", "RC-CR²", "Trapezoid", "FastTrap", 
                                           "Trap Baseline", "Energy Out", "Baseline Correction", "None"],
              "SupportedVirtualProbes2" : ["Input", "Threshold", "Trapezoid - Baseline", "Trapezoid BaseLine", "None", 
                                           "RC_CR", "FastTrap", "RC-CR²", "Trapezoid", "Energy Out"],
              "SupportedDigitalProbes1" : ["Trigger Window", "Armed", "Peak Run", "Pileup Flag", "Peaking", 
                                           "Trigger Validation Acceptance Window", "Baseline Holdoff", "Trigger Holdoff", 
                                           "Trigger Value", "Acquisition Veto", "BFMVeto", "External Trigger", "Trigger", 
                                           "None", "Energy Accepted", "Saturation", "Reset", "Baseline Freeze", "Busy", "PrgVeto", "Inhibit"],
              "SupportedDigitalProbes2" : ["Trigger", "None", "Peaking", "Baseline Holdoff", "PURFlag", "EnergyAccepted","Saturation", "Reset"],
              "InputRanges"             : ["9,50", "3,70", "1,40", "0,60", "3,00", "1,00", "0,30", "10,0", "5,00", "2,00", "0,50", 
                                           "2,50", "1,25", "0,10", "0,21", "0,45", "0,83", "1,60", "3,30", "6,60", "13,3"]}
#              "InputRanges"             : ["9.50", "3.70", "1.40", "0.60", "3.00", "1.00", "0.30", "10.0", "5.00", "2.00", "0.50", "2.50",
#                                           "1.25", "0.10", "0.21", "0.45", "0.83", "1.60", "3.30", "6.60", "13.3"]}


class DPP_Traces(Structure):
  RecordLength = 1<<16 # max length of waveform record is 65536 samples
  _fields_ = (("AT1",  c_int16  * RecordLength), 
              ("AT2",  c_int16  * RecordLength),  
              ("DT1",  c_uint8  * RecordLength), 
              ("DT2",  c_uint8  * RecordLength))


class DPP_ConnectionParams(Structure):
  IP_ADDR_LEN = 255
  LinkTypes = {'USB':0, 'OpticalLink':1, 'Ethernet':2, 'Serial':3}
  _fields_ = (("LinkType",       c_enum),
              ("LinkNum",        c_int32),
              ("ConetNode",      c_int32),
              ("VMEBaseAddress", c_uint32),
              ("ETHAddress",     c_char*(IP_ADDR_LEN+1)))

class DPP_ParamInfo(Structure):
  MAX_LIST_VALS = 15 
  Units =     ("NanoSeconds", "Samples", "Adimensional", "MicroAmpere", "Volt", "VoltsPerSecond", "Ohm")
  Types =     ("Range", "List")
  _fields_ = (("type",           c_enum),
              ("minimum",        c_double),
              ("maximum",        c_double),
              ("resolution",     c_double),
              ("values",         c_double*MAX_LIST_VALS),
              ("valuesCount",    c_uint32),
              ("units",          c_enum))

class DPP_HVChannelInfo(Structure):
  _fields_ = (("VSetInfo",       DPP_ParamInfo),
              ("ISetInfo",       DPP_ParamInfo),
              ("RampUpInfo",     DPP_ParamInfo),
              ("RampDownInfo",   DPP_ParamInfo),
              ("VMaxInfo",       DPP_ParamInfo),
              ("VMonInfo",       DPP_ParamInfo),
              ("IMonInfo",       DPP_ParamInfo),
              ("VExtInfo",       DPP_ParamInfo),
              ("RTMPInfo",       DPP_ParamInfo),
              ("HVFamilycode",   c_enum))

class DPP_Info(Structure):
  MAX_BRDNAME_LEN    = 12
  MAX_FWVER_LENGTH   = 20
  MAX_LICENSE_LENGTH = 17
  MAX_INRANGES       = 15
  MAX_PROBES_NUM     = 20
  MAX_HVCHB          = 2
  HV                 = ({},{})
  _fields_ = (("ModelName",               c_char*MAX_BRDNAME_LEN),
              ("Model",                   c_int32),
              ("Channels",                c_uint32),
              ("ROC_FirmwareRel",         c_char*MAX_FWVER_LENGTH),
              ("AMC_FirmwareRel",         c_char*MAX_FWVER_LENGTH),
              ("License",                 c_char*MAX_LICENSE_LENGTH),
              ("SerialNumber",            c_uint32),
              ("Status",                  c_ubyte),
              ("FamilyCode",              c_int32),
              ("HVChannels",              c_uint32),
              ("FormFactor",              c_uint32),
              ("PCB_Revision",            c_uint32),
              ("ADC_NBits",               c_uint32),
              ("Energy_MaxNBits",         c_uint32),
              ("USBOption",               c_uint32),
              ("ETHOption",               c_uint32),
              ("WIFIOption",              c_uint32),
              ("BTOption",                c_uint32),
              ("POEOption",               c_uint32),
              ("GPSOption",               c_uint32),
              ("InputRangeNum",           c_uint32),
              ("InputRanges",             c_enum*MAX_INRANGES),
              ("Tsample",                 c_double),
              ("SupportedVirtualProbes1", c_uint32*MAX_PROBES_NUM),
              ("NumVirtualProbes1",       c_uint32),
              ("SupportedVirtualProbes2", c_uint32*MAX_PROBES_NUM),
              ("NumVirtualProbes2",       c_uint32),
              ("SupportedDigitalProbes1", c_uint32*MAX_PROBES_NUM),
              ("NumDigitalProbes1",       c_uint32),
              ("SupportedDigitalProbes2", c_uint32*MAX_PROBES_NUM),
              ("NumDigitalProbes2",       c_uint32),
              ("DPPCodeMaj",              c_int32),
              ("DPPCodeMin",              c_int32),
              ("HVChannelInfo",           DPP_HVChannelInfo*MAX_HVCHB))

# D P P   H I G H   V O L T A G E   S E C T I O N 

class DPP_HVChannelConfig(Structure):
  (PWDownMode_Ramp, PWDownMode_Kill) = (0, 1)
  _fields_ = (("VSet",                      c_double),
              ("ISet",                      c_double),
              ("RampUp",                    c_double),
              ("RampDown",                  c_double),
              ("VMax",                      c_double),
              ("PWDownMode",                c_int32))

# D P P   P A R A M E T E R S   S E C T I O N

MAX_GW                 = 1000         # Max number of generic write register in the Config File
MAX_NUMCHB             = 16           # Max number of channels per board
MAX_NUMCHB_COINCIDENCE = MAX_NUMCHB+1 # Max number of channels for coincidences (add external channel)
MAX_LISTFILE_LENGTH    = 155          # Max binary file filename length
MAX_LIST_BUFF_NEV      = 8192         # Max size of the list events memory buffer
MAX_GPIO_NUM           = 2
MAX_RUNNAME            = 128


DPP_ParamID = { 'RecordLength' : c_enum(0 ), 'PreTrigger'    : c_enum(1 ), 'Decay'         : c_enum(2 ), 'TrapRise'  : c_enum(3 ),
                'TrapFlat'     : c_enum(4 ), 'TrapFlatDelay' : c_enum(5 ), 'Smoothing'     : c_enum(6 ), 'InputRise' : c_enum(7 ),
                'Threshold'    : c_enum(8 ), 'NSBL'          : c_enum(9 ), 'NSPK'          : c_enum(10), 'PKHO'      : c_enum(11),
                'BLHO'         : c_enum(12), 'TRGHO'         : c_enum(13), 'DGain'         : c_enum(14), 'ENF'       : c_enum(15),
                'Decimation'   : c_enum(16), 'TWWDT'         : c_enum(17), 'TRGWin'        : c_enum(18), 'PulsePol'  : c_enum(19),
                'DCOffset'     : c_enum(20), 'IOLev'         : c_enum(21), 'TRGain'        : c_enum(22) }                

class DPP_TRReset(Structure):
  ResetDetectionMode = ("Internal", "GPIO", "Both")
  _fields_ = (("Enabled",            c_uint32), # Enable TRReset mode (HEXAGON: requires AC coupling)
              ("ResetDetectionMode", c_enum),   # index in ResetDetectionMode: how to detect a reset
              ("thrhold",            c_uint32), # Reset negative threshold (X770 only)
              ("reslenmin",          c_uint32), # Minimum length of the reset spike to trigger the reset inhibit(X770 only)
              ("reslength",          c_uint32)) # Inhibit length

class DPP_CoincParams(Structure):
  Coincidence_Logic  = ("None", "Coincidence", "Anticoincidence")
  Coincidence_Option = ("OR",   "AND",         "MAJ")
  _fields_ = (("CoincChMask",        c_uint32), 
              ("MajLevel",           c_uint32), 
              ("TrgWin",             c_uint32), 
              ("CoincOp",            c_enum),  # index in Coincidence_Option
              ("CoincLogic",         c_enum))  # index in Coincidence_Logic
              
class DPP_ListParams(Structure):
  ListSaveMode = ("Memory",          # Keep the list events in a memory buffer of maximum size = MAX_LIST_BUFF_NEV
                  "FileBinary",      # Save list events in a binary file
                   "FileASCII")      # Save list events in a ASCII file
  _fields_ = (("enabled",            c_uint8),  # 1 = ListMode Enabled, 0 = ListMode Disabled
              ("saveMode",           c_enum),   # index in ListSaveMode
              ("fileName",           c_char*MAX_LISTFILE_LENGTH), # the filename used for binary writing
              ("maxBuffNumEvents",   c_uint32), # max number of events to keep in the buffer if in memory mode
              ("saveMask",           c_uint32)) #The mask of the object to be dumped as defined from 'DUMP_MASK_*' macros
              
class DPP_WaveformParams(Structure):
  _fields_ = (("dualTraceMode",       c_int32), # if true dual trace is enabled
              ("vp1",                 c_enum),  # First Analog Probe
              ("vp2",                 c_enum),  # Second Analog Probe, ignored if dualTraceMode=false
              ("dp1",                 c_enum),  # First Digital probe
              ("dp2",                 c_enum),  # Second Digital probe
              ("recordLength",        c_int32),
              ("preTrigger",          c_int32),
              ("probeTrigger",        c_enum),  # CAENDPP_PHA_ProbeTrigger_t definition was not found in DPP manual
              ("probeSelfTriggerVal", c_int32))
              
class DPP_GPIO(Structure): # GPIO for X770
  GPIOMode = ("OUTSignal", False, "INTrigger", "INReset")
  _fields_ = (("Mode",       c_enum),   
              ("SigOut",     c_enum),   # for this enum see page 56 of DPP manual
              ("DACInvert",  c_uint8),  # 0 -> not inverted; 1 -> Inverted
              ("DACOffset",  c_uint32))

class DPP_GPIOConfig(Structure): # GPIO config for X770
  TriggerControl = ("Internal", "Veto", "GateWin", "VetoWin", "ON", "Coincidence", "OFF")
  GPIOLogic      = ("AND", "OR")
  _fields_ = (("GPIOs",    DPP_GPIO*MAX_GPIO_NUM), 
              ("TRGControl",              c_enum),  
              ("GPIOLogic",               c_enum),  
              ("TimeWindow",              c_uint32),  
              ("TransResetLength",        c_uint32), 
              ("TransResetPeriod",        c_uint32))

class DPP_ExtraParameters(Structure): # Types Definition for X770
  InputImpedance = ("50 Ohm", "1 kOhm") 
  _fields_ = (("trigK",             c_int32),        # trigger fast trapezoid rising time
              ("trigm",             c_int32),        # trigger fast trapezoid flat top
              ("trigMODE",          c_int32),        # 0 - threshold on fast trapeziodal; 1 - for future use
              ("energyFilterMode",  c_int32),        # 0 - trapeziodal; 1 - for future use
              ("InputImpedance",    c_enum),         # input impedance
              ("CRgain",            c_uint32),       # Continuous Reset Analog Gain
              ("TRgain",            c_uint32),       # Pulsed Reset Analog Gain
              ("SaturationHoldoff", c_uint32),       # Saturation detector holdoff
              ("GPIOConfig",        DPP_GPIOConfig)) # GPIO Configuration for X770


class DPP_PHA_Params(Structure):
  _fields_ = (("M",          c_int32             * MAX_NUMCHB), # Signal Decay Time Constant
              ("m",          c_int32             * MAX_NUMCHB), # Trapezoid Flat Top
              ("k",          c_int32             * MAX_NUMCHB), # Trapezoid Rise Time
              ("ftd",        c_int32             * MAX_NUMCHB), # Trapezoid Peaking Delay
              ("a",          c_int32             * MAX_NUMCHB), # Trigger Filter smoothing factor
              ("b",          c_int32             * MAX_NUMCHB), # Input Signal Rise time
              ("thr",        c_int32             * MAX_NUMCHB), # Trigger Threshold
              ("nsbl",       c_int32             * MAX_NUMCHB), # Number of Samples for Baseline Mean
              ("nspk",       c_int32             * MAX_NUMCHB), # Number of Samples for Peak Mean Calculation
              ("pkho",       c_int32             * MAX_NUMCHB), # Peak Hold Off 
              ("blho",       c_int32             * MAX_NUMCHB), # Base Line Hold Off
              ("trgho",      c_int32             * MAX_NUMCHB), # Trigger Hold Off
              ("dgain",      c_int32             * MAX_NUMCHB), # Digital Probe Gain
              ("enf",        c_float             * MAX_NUMCHB), # Energy Normalization Factor
              ("decimation", c_int32             * MAX_NUMCHB), # Decimation (прореживание) of Input Signal
              ("enskim",     c_int32             * MAX_NUMCHB), # Enable energy skimming window [lsb]
              ("enskimlld",  c_int32             * MAX_NUMCHB), # LLD of skimming window [lsb]
              ("enskimuld",  c_int32             * MAX_NUMCHB), # ULD of skimming window [lsb]
              ("brlclip",    c_int32             * MAX_NUMCHB), # Enable baseline restorer clipping (отсечение)
              ("dcomp",      c_int32             * MAX_NUMCHB), # tt_filter compensation
              ("trapbsl",    c_int32             * MAX_NUMCHB), # trapezoid baseline adjuster
              ("pz_dac",     c_uint32            * MAX_NUMCHB), # DAC value used for PoleZero Cancellation
              ("inh_length", c_uint32            * MAX_NUMCHB), # Inhibit length
              ("X770_extra", DPP_ExtraParameters * MAX_NUMCHB)) # for X770 only

class DPP_TempCorrParams(Structure): # Types Definition for Gamma Stream
  _fields_ = (("enabled", c_int32),
              ("LLD",     c_int32),
              ("ULD",     c_int32))

class DPP_RunSpecs(Structure): # Types Definition for Gamma Stream
  _fields_ = (("RunName",         c_char*MAX_RUNNAME),   # run name
              ("RunDurationSec",  c_int32), # duration time (s)
              ("PauseSec",        c_int32), # pause duration (s)
              ("CyclesCount",     c_int32), # number of cycles to do
              ("SaveLists",       c_uint8), # 
              ("GPSEnable",       c_uint8), # 
              ("ClearHistos",     c_uint8)) # duration time (s)

class DPP_SpectrumControl(Structure):
  _fields_ = (("SpectrumMode", c_enum),   # 0 - Energy, 1 - Time distribution 
              ("TimeScale",    c_uint32)) # Scale in time distribution


class DPP_DgtzParams(Structure):
  PulsePolarity = ("Positive", "Negative")
  InputCoupling = ("DC", "AC_5us", "AC_10us", "AC_20us")
  IOLevel       = ("NIM", "TTL")
  _fields_ = (("GWn",                c_int32),               # Board Settings generic write
              ("GWaddr",             c_uint32 * MAX_GW),     # 
              ("GWdata",             c_uint32 * MAX_GW),     # 
              ("GWmask",             c_uint32 * MAX_GW),     # 
              ("ChannelMask",        c_int32),               # Channel Settings
              ("PulsePolarity",      c_enum   * MAX_NUMCHB), # 
              ("DCoffset",           c_int32  * MAX_NUMCHB), # 
              ("TempCorrParameters", DPP_TempCorrParams  * MAX_NUMCHB), # Only for GammaStream
              ("InputCoupling",      c_enum  * MAX_NUMCHB),  # Only for Hexagon
              ("EventAggr",          c_int32),               # 
              ("DPPParams",          DPP_PHA_Params),        # 
              ("IOlev",              c_enum),                # 
              ("WFParams",           DPP_WaveformParams),    # Waveform Mode Settings
              ("ListParams",         DPP_ListParams),        # List Mode Settings
              ("RunSpecifications",  DPP_RunSpecs),          # Run Specifications (only for GammaStream)
              ("CoincParams",        DPP_CoincParams     * MAX_NUMCHB_COINCIDENCE),  # Parameters for coincidence mode
              ("SpectrumControl",    DPP_SpectrumControl * MAX_NUMCHB),  # Spectrum Control setting (Only for X770)
              ("ResetDetector",      DPP_TRReset         * MAX_NUMCHB))  # Transistor Reset Detector settings
              
class DPP_DAQInfo(Structure):
  _fields_ = (("ACQStatus",          c_enum),                # 0 - Stop, 1 - Start, 2 - Pause
              ("RunLoop",            c_int32),
              ("RunState",           c_enum),                # 0 - Stop, 1 - Start, 2 - Pause
              ("RunElapsedTimeSec",  c_int64), 
              ("TotEvtCount",        c_int32),
              ("DeadTimeNs",         c_int64),
              ("GainStatus",         c_enum),                # OFF, Searching, Found, Lost, Following
              ("RunID",              c_int32))
  

