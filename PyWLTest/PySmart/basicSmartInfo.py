import re
from ctypes import *

class BasicSmartInfo:
    def __init__(self):
        self.MPVersionStr = ''
        self.FlashTypeStr = ''
        self.FlashIDStr = ''
        self.TotalCECount = 0
        self.ECCCapacity = 0
        self.HWVersionStr = ''
        self.FWVersionStr = ''
        self.AbnormalShutdownCount = 0
        self.ECCUncCount = 0
        self.PowerCycleCount = 0
        self.FactoryBadBlocks = 0
        self.MininumSpareBlocks = 0
        self.LaterBadBlocks = 0
        self.TotalEraseCount = 0
        self.AverageEraseCount = 0
        self.MaximumEraseCount = 0 
        self.MinimumEraseCount = 0
        self.LifeIndicator = 0.0
        self.TotalVBCount = 0
        self.VBMultiplier = 0
        self.HeaderVersion = 0
        self.EraseCountOffset = 0
    
    def reset(self, smartLib):
        self.MPVersionStr = smartLib.GetMPVersion().decode('utf-8')
        self.FlashTypeStr = smartLib.GetFlashType().decode('utf-8')
        self.FlashIDStr = smartLib.GetFlashID().decode('utf-8')
        self.TotalCECount = int(smartLib.GetTotalCECount())
        self.ECCCapacity = int(smartLib.GetECCCapacity())
        self.HWVersionStr = smartLib.GetHWVersion().decode('utf-8')
        self.FWVersionStr = smartLib.GetFWVersion().decode('utf-8')
        self.AbnormalShutdownCount = int(smartLib.GetAbnormalShutdownCount())
        self.ECCUncCount = int(smartLib.GetECCUncorrectableCount())
        self.PowerCycleCount = smartLib.GetPowerCycleCount()
        self.FactoryBadBlocks = int(smartLib.GetInitialBadBlockCount())
        self.MininumSpareBlocks = int(smartLib.GetMinSpareBlockCount())
        self.LaterBadBlocks = int(smartLib.GetLaterBadBlockCount())
        self.TotalEraseCount = smartLib.GetTotalEraseCount()
        self.AverageEraseCount = smartLib.GetAverageEraseCount()
        self.MaximumEraseCount = smartLib.GetMaxEraseCount()
        self.MinimumEraseCount = smartLib.GetMinEraseCount()
        self.LifeIndicator = smartLib.GetRemainingLife()
        self.TotalVBCount = smartLib.GetTotalVBCountOfFlash()
        self.VBMultiplier = smartLib.GetVBMultiplier()
        self.HeaderVersion = int(smartLib.GetHeaderVersion())
        self.EraseCountOffset = int(smartLib.GetEraseCountOffset())        

    def __str__(self):
        txt = ''
        #members = dir(self)
        for key in self.__dict__:
            if not key.startswith('__') and not key.endswith('__'):                
                value = self.__dict__[key]
                
                if not re.match('<function.*?>', str(value)):
                    #field = 'self.{}'.format(key)     
                    if (key is 'LifeIndicator'):   
                        val_str = str(value)
                        point_at = val_str.find('.')
                        end_pos = min(len(val_str), point_at+3)
                        txt += '{: <22}: {} %\n'.format(key, val_str[:end_pos])
                    else:
                        txt += '{: <22}: {}\n'.format(key, str(value))
        return txt
