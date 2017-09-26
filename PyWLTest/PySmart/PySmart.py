import re

from ctypes import *
from . import osinfo
from . import smartHeader
from . import basicSmartInfo

_libPath = osinfo.libdir + '\\SmartSDK_1288_Win32.dll'
_smartLib = windll.LoadLibrary(_libPath)

_smartLib.GetMPVersion.restype = c_char_p
_smartLib.GetFlashType.restype = c_char_p
_smartLib.GetFlashID.restype = c_char_p
_smartLib.GetHWVersion.restype = c_char_p
_smartLib.GetFWVersion.restype = c_char_p
_smartLib.GetRemainingLife.restype = c_float
_smartLib.GetECCUncorrectableCount.restype = c_ushort
_smartLib.GetInitialBadBlockCount.restype = c_ushort
_smartLib.GetMinSpareBlockCount.restype = c_ushort
_smartLib.GetLaterBadBlockCount.restype = c_ushort
_smartLib.GetTotalCECount.restype = c_byte
_smartLib.GetECCCapacity.restype = c_byte
_smartLib.GetEraseCountOffset.restype = c_ushort
_smartLib.GetHeaderVersion.restype = c_byte

_smartLib.GetSmartHeader.restype = smartHeader.SmartHeader
_smartLib.GetDetailEraseCount.restype = c_ubyte

_drive = ''

class SmartInfo:
    def __init__(self):
        global _smartLib
        self.BasicInfo = basicSmartInfo.BasicSmartInfo()
        self.SmartHeader = smartHeader.SmartHeader()
        self._totalVBs = 0
        _smartLib.SetTransactionVersion(2)         
    
    def Read(self, DriveName:str):
        global _smartLib
        strBuf = create_string_buffer(DriveName.encode('utf-8'))
        _smartLib.SetDiskName(strBuf)        
        _smartLib.GetSmartInfo.restype = c_byte
        ret = _smartLib.GetSmartInfo()
        # Update basic smart info data
        self.BasicInfo.reset(_smartLib)
        self.SmartHeader = _smartLib.GetSmartHeader()

        if (self.SmartHeader.VB_GapOffset == 0):
            dieCount = 1
        else:
           dieCount = (self.SmartHeader.TotalVBCountOfFlash / self.SmartHeader.VB_GapOffset) 

        self._totalVBs = self.SmartHeader.TotalVBCountWithHash + ((dieCount  -1) * self.SmartHeader.VB_GapNumber)

        buffLen = self._totalVBs * sizeof(c_uint32)
        arrayType = c_uint32 * self._totalVBs

        retBuffLen = c_ulong()

        self.EraseCountRawData = arrayType()
        _smartLib.GetDetailEraseCount(self.EraseCountRawData, buffLen, byref(retBuffLen))

        #self.EechVBEraseCount = list(self.EraseCountRawData)

        _smartLib.CloseDeviceHandle()

        return ret    

    def GetErrorMessage(self):
        global _smartLib
        _smartLib.GetErrorMessage.restype = c_char_p
        ret = _smartLib.GetErrorMessage()
        return ret.decode('utf-8')
        

    def GetEraseCountRawData():
        global basicInfo
        buffSize = basicInfo.TotalVBCount