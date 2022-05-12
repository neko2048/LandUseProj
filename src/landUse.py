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


class ESRI:
    def __init__(self, dataInfo):
        self.dataInfo = dataInfo
        self.landUseName = self.dataInfo["landUseName"]
        self.colorMap = self.dataInfo["colorMap"]
        self.landUse = tiff.imread(self.dataInfo["southFileDir"]) # shape:(lat, lon)

    def getLonLat(self, dictBoundary):
        initLon = dictBoundary["initLon"]
        endLon  = dictBoundary["endLon"]
        initLat = dictBoundary["initLat"]
        endLat  = dictBoundary["endLat"]
        lon = np.linspace(initLon, endLon, self.landUse.shape[1])
        lat = np.linspace(initLat, endLat, self.landUse.shape[0])
        return lon, lat

    def getPartLonLat(self, landUseShape, dictBoundary):
        initLon = dictBoundary["initLon"]
        endLon  = dictBoundary["endLon"]
        initLat = dictBoundary["initLat"]
        endLat  = dictBoundary["endLat"]
        lon = np.linspace(initLon, endLon, landUseShape[1])
        lat = np.linspace(initLat, endLat, landUseShape[0])
        return lon, lat

    def getPartLandUse(self, type):
        landUse = tiff.imread(self.dataInfo[type+"FileDir"])
        lon, lat = self.getPartLonLat(landUseShape=landUse.shape, dictBoundary=self.dataInfo[type+"Bound"])
        lon, lat, landUse = self.cutPartEdge(lon, lat, landUse, dictBoundary=taiwanDictBoundary, type=type)
        return lon, lat, landUse

    def cutPartEdge(self, lon, lat, landUse, dictBoundary, type):
        lonLimit = np.logical_and(lon >= dictBoundary['initLon'], lon <= dictBoundary['endLon'])
        if type=="north":
            latLimit = np.logical_and(lat >= 23.5, lat <= dictBoundary['endLat'])
        elif type=="south":
            latLimit = np.logical_and(lat >= dictBoundary['initLat'], lat <= 23.5)
        landUse = landUse[latLimit[::-1]][:, lonLimit][::-1]
        lon = lon[lonLimit]
        lat = lat[latLimit]
        return lon, lat, landUse

    def cutEdge(self, dictBoundary):
        initLonIdx = np.argmin(np.abs(self.lon - dictBoundary['initLon']))
        endLonIdx = np.argmin(np.abs(self.lon - dictBoundary['endLon']))+1
        initLatIdx = np.argmin(np.abs(self.lat - dictBoundary['initLat']))
        endLatIdx = np.argmin(np.abs(self.lat - dictBoundary['endLat']))+1
        self.landUse = self.landUse[-endLatIdx:-initLatIdx, initLonIdx:endLonIdx][::-1]
        self.lon = self.lon[initLonIdx:endLonIdx]
        self.lat = self.lat[initLatIdx:endLatIdx]

    def getUrbanIndex(self):
        urbanIndex = 0
        for idx, info in self.colorMap.items():
            if "Built" in info[1]:
                urbanIndex = idx
                break
        return urbanIndex

    def getWaterIndex(self):
        waterIndex = 0
        for idx, info in self.colorMap.items():
            if "ater" in info[1]:
                waterIndex = idx
                break
        return waterIndex

    def getUrbanRatio(self):
        urbanIndex = self.getUrbanIndex()
        waterIndex = self.getWaterIndex()
        numUrban = np.sum(self.landUse == urbanIndex)
        numTotal = np.sum(self.landUse != waterIndex)
        return numUrban / numTotal

    def getTaiwanUrbanRatio(self):
        urbanIndex = self.getUrbanIndex()
        waterIndex = self.getWaterIndex()
        numNorthUrban = np.sum(self.northLandUse == urbanIndex)
        numSouthUrban = np.sum(self.southLandUse == urbanIndex)
        numNorthNonWater = np.sum(np.logical_and(self.northLandUse != waterIndex, self.northLandUse != 0))
        numsouthNonWater = np.sum(np.logical_and(self.southLandUse != waterIndex, self.southLandUse != 0))
        numNorthTotal = self.northLandUse.shape[0] * self.northLandUse.shape[1]
        numSouthTotal = self.southLandUse.shape[0] * self.southLandUse.shape[1]
        totalNorthArea = (np.max(self.nLat) - np.min(self.nLat)) / (np.max(self.nLat) - np.min(self.sLat))
        totalSouthArea = (np.max(self.sLat) - np.min(self.sLat)) / (np.max(self.nLat) - np.min(self.sLat))
        gridNorthArea, gridSouthArea = totalNorthArea / numNorthTotal, totalSouthArea / numSouthTotal
        return (numNorthUrban * gridNorthArea + numSouthUrban * gridSouthArea) / (numNorthNonWater * gridNorthArea + numsouthNonWater * gridSouthArea)

    def getTaiwanEachCateRatio(self):
        waterIndex = self.getWaterIndex()
        numNorthTotal = self.northLandUse.shape[0] * self.northLandUse.shape[1]
        numSouthTotal = self.southLandUse.shape[0] * self.southLandUse.shape[1]
        numNorthNonWater = np.sum(np.logical_and(self.northLandUse != waterIndex, self.northLandUse != 0))
        numsouthNonWater = np.sum(np.logical_and(self.southLandUse != waterIndex, self.southLandUse != 0))

        for idx, info in self.colorMap.items():
            targetIndex = idx
            numNorthTarget = np.sum(self.northLandUse == targetIndex)
            numSouthTarget = np.sum(self.southLandUse == targetIndex)
            totalNorthArea = (np.max(self.nLat) - np.min(self.nLat)) / (np.max(self.nLat) - np.min(self.sLat))
            totalSouthArea = (np.max(self.sLat) - np.min(self.sLat)) / (np.max(self.nLat) - np.min(self.sLat))
            gridNorthArea, gridSouthArea = totalNorthArea / numNorthTotal, totalSouthArea / numSouthTotal
            ratioUp = numNorthTarget * gridNorthArea + numSouthTarget * gridSouthArea
            ratioDown = numNorthNonWater * gridNorthArea + numsouthNonWater * gridSouthArea
            print(info, ratioUp / ratioDown * 100)


    def drawYunLin(self):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        fig = subplots(1, 1, figsize=(16, 7))
        pcolormesh(self.lon, self.lat, self.landUse, 
        vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        xlim(yunInitLon, yunEndLon)
        ylim(yunInitLat, yunEndLat)
        title('{} LandUse'.format(self.landUseName))
        savefig("{}_yunlin.jpg".format(self.landUseName), dpi=300)

    def drawTaiwan(self, localDictBoundary=None):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        fig = subplots(1, 1, figsize=(16, 16))
        pcolormesh(self.nLon, self.nLat, self.northLandUse, 
        vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)
        pcolormesh(self.sLon, self.sLat, self.southLandUse, 
        vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
        if localDictBoundary:
            plot([localDictBoundary["initLon"], localDictBoundary["endLon"], localDictBoundary["endLon"], localDictBoundary["initLon"], localDictBoundary["initLon"]], 
                 [localDictBoundary["initLat"], localDictBoundary["initLat"], localDictBoundary["endLat"], localDictBoundary["endLat"], localDictBoundary["initLat"]], 
                 color='red', linewidth=10)
        title('{} LandUse'.format(self.landUseName), fontsize=30)
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        savefig("{}_Taiwan.jpg".format(self.landUseName), dpi=600)
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
    with open("../data/ESRI_10m.json") as jsonFile:
        ESRI_10mInfo = json.load(jsonFile) # not test yet
    # landUse type: https://www.arcgis.com/home/item.html?id=d6642f8a4f6d4685a24ae2dc0c73d4ac

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
    print(luDataLoader.getCatRatio(catName="urban", excludeIdx=16))
    luDataLoader.cutEdge(yunlinDictBoundary)
    luDataLoader.drawRegion(regionBound=yunlinDictBoundary, figsize=(17, 6))
    luDataLoader.drawRegion(regionBound=taiwanDictBoundary, labelBound=yunlinDictBoundary, figsize=(20, 20))
    luDataLoader.getEveryCatRatio(excludeIdx=16)
    
    #esri = ESRI(dataInfo = ESRI_10mInfo)
    # >>>>> draw Taiwan >>>>>
    #esri.nLon, esri.nLat, esri.northLandUse = esri.getPartLandUse(type="north")
    #esri.sLon, esri.sLat, esri.southLandUse = esri.getPartLandUse(type="south")
    #esri.lon, esri.lat, esri.landUse = esri.getPartLandUse(type="south")
    #esri.drawTaiwan(localDictBoundary=None)
    #print(esri.getTaiwanUrbanRatio())
    #esri.getTaiwanEachCateRatio()
    
    # >>>>> draw YunLin >>>>>
    #esri.lon, esri.lat  = esri.getLonLat(dictBoundary=ESRI_10mInfo["southBound"])
    #esri.cutEdge(yunlinDictBoundary)
    #esri.drawYunLin()
    #print(esri.getUrbanRatio())
    
    