import numpy as np
from matplotlib.pyplot import *
import re
from matplotlib.colors import ListedColormap
import tifffile as tiff
import twd97
import re
import json
class LandUseDataLoader:
    def __init__(self, anchorLon, anchorlat, dataInfo, colorMap):
        self.anchorlon = anchorLon
        self.anchorlat = anchorlat
        self.landUseName = dataInfo["landUseName"]
        self.dirName = dataInfo["folderDir"]
        self.baseLon = dataInfo["baseLon"]
        self.baseLat = dataInfo["baseLat"]
        self.dx = dataInfo["dx"]
        self.dy = dataInfo["dy"]
        self.tilex = dataInfo["tilex"]
        self.tiley = dataInfo["tiley"]
        self.colorMap = colorMap

    def getFileName(self):
        gridLon, gridLat = (self.anchorlon - self.baseLon)/self.dx, (self.anchorlat - self.baseLat)/self.dy
        fileName = "{xInit:05d}-{xEnd:05d}.{yInit:05d}-{yEnd:05d}"\
                   .format(xInit = int(gridLon // self.tilex * self.tilex + 1), 
                           xEnd  = int(gridLon // self.tilex * self.tilex + self.tilex), 
                           yInit = int(gridLat // self.tiley * self.tiley + 1), 
                           yEnd  = int(gridLat // self.tiley * self.tiley + self.tiley))
        return fileName

    def getLonLat(self):
        fileName = self.getFileName().replace(".", "-")
        initLon, endLon, initLat, endLat = fileName.split("-")

        initLon = self.dx * int(initLon) + self.baseLon
        endLon = self.dx * int(endLon) + self.baseLon
        initLat = self.dy * int(initLat) + self.baseLat
        endLat = self.dy * int(endLat) + self.baseLat
        lon = np.linspace(initLon, endLon, self.tilex)
        lat = np.linspace(initLat, endLat, self.tiley)
        return lon, lat

    def loadData(self):
        self.fileName = self.getFileName()
        data = np.fromfile(self.dirName+self.fileName, dtype="i1")
        data = np.reshape(data, (self.tiley, self.tilex))
        return data

    def cutEdge(self, dictBoundary):
        initLonIdx = np.argmin(np.abs(self.lon - dictBoundary['initLon']))
        endLonIdx = np.argmin(np.abs(self.lon - dictBoundary['endLon']))+1
        initLatIdx = np.argmin(np.abs(self.lat - dictBoundary['initLat']))
        endLatIdx = np.argmin(np.abs(self.lat - dictBoundary['endLat']))+1
        self.landUse = self.landUse[initLatIdx:endLatIdx, initLonIdx:endLonIdx]
        self.lon = self.lon[initLonIdx:endLonIdx]
        self.lat = self.lat[initLatIdx:endLatIdx]

    def getCatIdx(self, catName):
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if catName in info[-1]:
                catIdx = idx
                return catIdx
        return None

    def getCatRatio(self, catName, excludeIdx):
        numTotal = np.sum(self.landUse != excludeIdx)
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if idx != excludeIdx and info[1] == catName:
                numTarget = np.sum(self.landUse == idx)
                return(numTarget / numTotal*100)
        return None

    def getEveryCatRatio(self, excludeIdx):
        numTotal = np.sum(self.landUse != excludeIdx)
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if idx != excludeIdx:
                numTarget = np.sum(self.landUse == idx)
                print("{:30s}: {} %".format(info[1], numTarget / numTotal*100))
            else:
                print("{:30s}: {}".format(info[1], "Not be counted"))
        return None

    def drawRegion(self, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        lonLimit = np.logical_and(self.lon >= regionBound['initLon'], self.lon <= regionBound['endLon'])
        latLimit = np.logical_and(self.lat >= regionBound['initLat'], self.lat <= regionBound['endLat'])
        lon = self.lon[lonLimit]
        lat = self.lat[latLimit]
        landUse = self.landUse[latLimit][:, lonLimit]
        #landUse = np.full(fill_value=17, shape=landUse.shape)
        fig = subplots(1, 1, figsize=(figsize or None))
        pcolormesh(lon, lat, landUse, 
        vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], 
                 [labelBound["initLat"], labelBound["initLat"], labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{} LandUse'.format(self.landUseName), fontsize=30)
        savefig("{}_{}.jpg".format(self.landUseName, regionBound["regionName"]), dpi=300)



if __name__ == "__main__":
    taiwanDictBoundary = {
    'initLon': 120,
    'endLon':  122.282366,  
    'initLat': 21.752632,
    'endLat': 25.459580, 
    'regionName': "Taiwan", 
    }
    yunlinDictBoundary = {
    'initLon': 120.01,
    'endLon':  121.00,  
    'initLat': 23.4853847,
    'endLat': 23.9194608, 
    'regionName': "YunLin", 
    }
    # >>>>> data name >>>>>
    with open("../data/USGS_30s.json") as jsonFile:
        USGS_30Info = json.load(jsonFile)
    with open("../data/MODIS_15s.json") as jsonFile:
        MODIS_15Info = json.load(jsonFile)
    with open("../data/MODIS_5s.json") as jsonFile:
        MODIS_5Info = json.load(jsonFile)
    with open("../data/CJCHEN_30s.json") as jsonFile:
        CJCHEN_30Info = json.load(jsonFile)

    with open("../data/LU20type.json") as jsonFile:
        LU20type = json.load(jsonFile)
    with open("../data/LU24type.json") as jsonFile:
        LU24type = json.load(jsonFile)

    # <<<<< data name <<<<<
    targetLandUseInfo = USGS_30Info
    colorMap = LU24type
    luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataInfo=targetLandUseInfo, colorMap=colorMap)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    luDataLoader.cutEdge(taiwanDictBoundary)
    #print(luDataLoader.getCatRatio(catName="urban", excludeIdx=16))
    #luDataLoader.cutEdge(yunlinDictBoundary)
    #luDataLoader.drawRegion(regionBound=yunlinDictBoundary, figsize=(17, 6))
    #luDataLoader.drawRegion(regionBound=taiwanDictBoundary, labelBound=yunlinDictBoundary, figsize=(20, 20))
    #luDataLoader.getEveryCatRatio(excludeIdx=16)
    

