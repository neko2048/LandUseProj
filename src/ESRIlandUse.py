import numpy as np
from matplotlib.pyplot import *
import re
from matplotlib.colors import ListedColormap
import tifffile as tiff
import twd97
import re
import json
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
    with open("../data/ESRI_10m.json") as jsonFile:
        ESRI_10mInfo = json.load(jsonFile) # not test yet
    # landUse type: https://www.arcgis.com/home/item.html?id=d6642f8a4f6d4685a24ae2dc0c73d4ac


    

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
    
    