from matplotlib.pyplot import *
from matplotlib import colors
import numpy as np 
from netCDF4 import Dataset
import pandas as pd
from matplotlib.colors import ListedColormap

def findArgmin(data, value):
    IdxMinflat = np.argmin(abs(data - value))
    idxMin = np.unravel_index(IdxMinflat, data.shape)
    return idxMin

class WRFData:
    def __init__(self, fileDir):
        self.filedir = fileDir
        self.wrfdata = Dataset(fileDir)
        self.xlon = self.getVar('XLONG')#self.wrfdata["XLONG"]
        self.xlat = self.getVar('XLAT')#self.wrfdata["XLAT"]
        self.pdTimes = self.constructLocalTime()
        self.lu_index = self.getVar("LU_INDEX")
    def delSpinUpTime(self, var):
        """remove the spin up (first 24 hours)"""
        var = var[13:]
        return var

    def getVar(self, varName):
        var = np.array(self.wrfdata[varName])
        var = self.delSpinUpTime(var)
        return var

    def UTCtoLocal(self, UTCTimes):
        LocalTimes = UTCTimes + pd.Timedelta(8, 'hour')
        return LocalTimes


    def constructLocalTime(self):
        oriTimes = self.getVar('Times')
        newTimes = []
        for i in range(len(oriTimes)):
            newTimes.append(pd.to_datetime("".join(char.decode("utf-8") for char in oriTimes[i]), format="%Y-%m-%d_%H:%M:%S"))
        newTimes = pd.DatetimeIndex(newTimes)

        LocalTimes = self.UTCtoLocal(newTimes)
        return LocalTimes


if __name__ == "__main__":
    WrfVersion = "v1"
    mode = "NC"
    day = 16

    colorMap = {
    1: "#e21417", # urban
    2: "#ffffff", # dryland
    3: "#ffffff", #irrigated cropland
    4: "#ffffff", # mixed dryland/irrigated
    5: "#ffffff", #cropland/grassland
    6: "#ffffff", #cropland/woodland
    7: "#98fcca", #grassland
    8: "#ffffff", #shrubland
    9: "#ffffff", #mixed shrubland/grassland
    10: "#9ad9b9", #savanna
    11: "#41b3ad", #deciduous broadleaf
    12: "#6bcc9c", #deciduous needleleaf
    13: "#11550f", #evergreen broadleaf
    14: "#63c7be", #evergreen needleleaf
    15: "#077e0d", #mixed forest
    16: "#54aaea", #water bodies
    17: "#ffffff", #herbaceous wetland
    18: "#ffffff", #wooden wetland
    19: "#ffffff", #barren or sparsely vegetated
    20: "#ffffff", #herbaceous tundra
    21: "#ffffff", #wooded tundra
    22: "#ffffff", #mixed tundra
    23: "#ffffff", #bare ground tundra
    24: "#0102f9", #snow or ice
    }
    cmap = ListedColormap([x for x in colorMap.values()])
    # ========== 
    wrf_dir = "/home/twsand/fskao/wrfOUT43{VERSION}/{MODE}202104{DATE}/wrfout_d04_2021-04-{DATE}_12:00:00".format(VERSION=WrfVersion , MODE=mode, DATE=day)
    wrfData = WRFData(fileDir = wrf_dir)
    pcolormesh(wrfData.xlon[0], wrfData.xlat[0], wrfData.lu_index[0], cmap=cmap)
    colorbar()
    savefig('lu_index_Yunlin.jpg', dpi=300)

