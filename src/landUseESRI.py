import numpy as np
from matplotlib.pyplot import *
import re
from matplotlib.colors import ListedColormap
import tifffile as tiff
import twd97
import re
import json
class ESRIDataLoader:
    def __init__(self, dataDirs, hemiType):
        self.dataDirs = dataDirs
        self.hemiType = hemiType
        self.dataInfo = self.getJSON("landUseInfo")
        self.landUseInfo = self.dataDirs["landUseInfo"]
        self.colorMap = self.dataDirs["colorMap"]
        self.landUseName = self.dataInfo["landUseName"]
        self.cutEdgeLat = 23.5
        if "countyNumMap" in self.dataDirs.keys():
            self.countyNumMap = np.load(self.dataDirs["countyNumMap"])

    def getJSON(self, name):
        with open(self.dataDirs[name]) as jsonFile:
            jsonData = json.load(jsonFile)
        return jsonData

    def loadData(self):
        data = tiff.imread(self.dataInfo["{}FileDir".format(self.hemiType)]) # shape: (lat, lon)
        return data[::-1]

    def getLonLat(self):
        dictBoundary = self.dataInfo["{}Bound".format(self.hemiType)]
        initLon = dictBoundary["initLon"]
        endLon  = dictBoundary["endLon"]
        initLat = dictBoundary["initLat"]
        endLat  = dictBoundary["endLat"]
        lon = np.linspace(initLon, endLon, self.landUse.shape[1])
        lat = np.linspace(initLat, endLat, self.landUse.shape[0])
        return lon, lat

    def cutEdge(self, dictBoundary):
        initLonIdx = np.argmin(np.abs(self.lon - dictBoundary['initLon']))
        endLonIdx = np.argmin(np.abs(self.lon - dictBoundary['endLon']))+1
        initLatIdx = np.argmin(np.abs(self.lat - dictBoundary['initLat']))
        endLatIdx = np.argmin(np.abs(self.lat - dictBoundary['endLat']))+1
        # >>>>>> for concat south & north in future >>>>>
        if self.hemiType == "south" and dictBoundary['endLat'] > self.cutEdgeLat:
            endLatIdx = np.argmin(np.abs(self.lat - self.cutEdgeLat))+1
        if self.hemiType == "north" and dictBoundary['initLat'] < self.cutEdgeLat:
            initLatIdx = np.argmin(np.abs(self.lat - self.cutEdgeLat))
        # <<<<< for concat south & north in future <<<<<
        self.landUse = self.landUse[initLatIdx:endLatIdx, initLonIdx:endLonIdx]
        self.lon = self.lon[initLonIdx:endLonIdx]
        self.lat = self.lat[initLatIdx:endLatIdx]

class MergeSys():
    def __init__(self, nEsri, sEsri):
        self.nEsri = nEsri
        self.sEsri = sEsri


    #def getUrbanIndex(self):
    #    urbanIndex = 0
    #    for idx, info in self.colorMap.items():
    #        if "Built" in info[1]:
    #            urbanIndex = idx
    #            break
    #    return urbanIndex

    #def getWaterIndex(self):
    #    waterIndex = 0
    #    for idx, info in self.colorMap.items():
    #        if "ater" in info[1]:
    #            waterIndex = idx
    #            break
    #    return waterIndex

    #def getUrbanRatio(self):
    #    urbanIndex = self.getUrbanIndex()
    #    waterIndex = self.getWaterIndex()
    #    numUrban = np.sum(self.landUse == urbanIndex)
    #    numTotal = np.sum(self.landUse != waterIndex)
    #    return numUrban / numTotal

    #def getTaiwanUrbanRatio(self):
    #    urbanIndex = self.getUrbanIndex()
    #    waterIndex = self.getWaterIndex()
    #    numNorthUrban = np.sum(self.northLandUse == urbanIndex)
    #    numSouthUrban = np.sum(self.southLandUse == urbanIndex)
    #    numNorthNonWater = np.sum(np.logical_and(self.northLandUse != waterIndex, self.northLandUse != 0))
    #    numsouthNonWater = np.sum(np.logical_and(self.southLandUse != waterIndex, self.southLandUse != 0))
    #    numNorthTotal = self.northLandUse.shape[0] * self.northLandUse.shape[1]
    #    numSouthTotal = self.southLandUse.shape[0] * self.southLandUse.shape[1]
    #    totalNorthArea = (np.max(self.nLat) - np.min(self.nLat)) / (np.max(self.nLat) - np.min(self.sLat))
    #    totalSouthArea = (np.max(self.sLat) - np.min(self.sLat)) / (np.max(self.nLat) - np.min(self.sLat))
    #    gridNorthArea, gridSouthArea = totalNorthArea / numNorthTotal, totalSouthArea / numSouthTotal
    #    return (numNorthUrban * gridNorthArea + numSouthUrban * gridSouthArea) / (numNorthNonWater * gridNorthArea + numsouthNonWater * gridSouthArea)

    #def getTaiwanEachCateRatio(self):
    #    waterIndex = self.getWaterIndex()
    #    numNorthTotal = self.northLandUse.shape[0] * self.northLandUse.shape[1]
    #    numSouthTotal = self.southLandUse.shape[0] * self.southLandUse.shape[1]
    #    numNorthNonWater = np.sum(np.logical_and(self.northLandUse != waterIndex, self.northLandUse != 0))
    #    numsouthNonWater = np.sum(np.logical_and(self.southLandUse != waterIndex, self.southLandUse != 0))

    #    for idx, info in self.colorMap.items():
    #        targetIndex = idx
    #        numNorthTarget = np.sum(self.northLandUse == targetIndex)
    #        numSouthTarget = np.sum(self.southLandUse == targetIndex)
    #        totalNorthArea = (np.max(self.nLat) - np.min(self.nLat)) / (np.max(self.nLat) - np.min(self.sLat))
    #        totalSouthArea = (np.max(self.sLat) - np.min(self.sLat)) / (np.max(self.nLat) - np.min(self.sLat))
    #        gridNorthArea, gridSouthArea = totalNorthArea / numNorthTotal, totalSouthArea / numSouthTotal
    #        ratioUp = numNorthTarget * gridNorthArea + numSouthTarget * gridSouthArea
    #        ratioDown = numNorthNonWater * gridNorthArea + numsouthNonWater * gridSouthArea
    #        print(info, ratioUp / ratioDown * 100)


    #def drawYunLin(self):
    #    cmap = ListedColormap([x[0] for x in self.colorMap.values()])
    #    cmapTick = [x[1] for x in self.colorMap.values()]
    #    fig = subplots(1, 1, figsize=(16, 7))
    #    pcolormesh(self.lon, self.lat, self.landUse, 
    #    #vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
    #    vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
    #    cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
    #    cb.set_ticklabels(cmapTick)
    #    xlim(yunlinDictBoundary["initLon"], yunlinDictBoundary["endLon"])
    #    ylim(yunlinDictBoundary["initLat"], yunlinDictBoundary["endLat"])
    #    title('{} LandUse'.format(self.landUseName))
    #    savefig("{}_yunlin.jpg".format(self.landUseName), dpi=300)

    #def drawRegion(self, regionBound, localDictBoundary=None, figsize=None):
    #    dlon = regionBound["endLon"] - regionBound["initLon"]
    #    dlat = regionBound["endLat"] - regionBound["initLat"]
    #    
    #    cmap = ListedColormap([x[0] for x in self.colorMap.values()])
    #    cmapTick = [x[1] for x in self.colorMap.values()]
    #    fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20+4, 20)))
    #    pcolormesh(self.nLon, self.nLat, self.northLandUse, 
    #    #vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
    #    vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
    #    cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
    #    cb.set_ticklabels(cmapTick)
    #    cb.ax.tick_params(labelsize=17)
    #    pcolormesh(self.sLon, self.sLat, self.southLandUse, 
    #    #vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
    #    vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
    #    
    #    if localDictBoundary:
    #        plot([localDictBoundary["initLon"], localDictBoundary["endLon"], localDictBoundary["endLon"], localDictBoundary["initLon"], localDictBoundary["initLon"]], 
    #             [localDictBoundary["initLat"], localDictBoundary["initLat"], localDictBoundary["endLat"], localDictBoundary["endLat"], localDictBoundary["initLat"]], 
    #             color='red', linewidth=10)
    #    title('{} LandUse'.format(self.landUseName), fontsize=30)
    #    xlabel('Longitude', fontsize=30)
    #    ylabel('Latitude', fontsize=30)
    #    xticks(fontsize=30)
    #    yticks(fontsize=30)
    #    savefig("{}_Taiwan.jpg".format(self.landUseName), dpi=600)

if __name__ == "__main__":
    taiwanDictBoundary = {
    'initLon': 120,
    'endLon':  122.282366,  
    'initLat': 21.752632,
    'endLat': 25.459580, 
    'regionName': "Taiwan", 
    }
    northDataDirs = {
    "landUseInfo": "../data/ESRI_10m.json", 
    "colorMap": "../data/LU10types.json", 
    "countyNumMap": "../data/ESRI_10mNorth_countyNumMap.npy",
    }
    southDataDirs = {
    "landUseInfo": "../data/ESRI_10m.json", 
    "colorMap": "../data/LU10types.json", 
    "countyNumMap": "../data/ESRI_10mSouth_countyNumMap.npy",
    }


    nEsri = ESRIDataLoader(dataDirs = northDataDirs, hemiType="north")
    nEsri.landUse = nEsri.loadData()
    nEsri.lon, nEsri.lat = nEsri.getLonLat()
    nEsri.cutEdge(dictBoundary=taiwanDictBoundary)
    print(nEsri.countyNumMap.shape)

    sEsri = ESRIDataLoader(dataDirs = southDataDirs, hemiType="south")
    sEsri.landUse = sEsri.loadData()
    sEsri.lon, sEsri.lat = sEsri.getLonLat()
    sEsri.cutEdge(dictBoundary=taiwanDictBoundary)
    print(sEsri.countyNumMap.shape)
    
    mergeSys = MergeSys(nEsri, nEsri)

    # >>>>> draw Taiwan >>>>>
    #esri.nLon, esri.nLat, esri.northLandUse = esri.getHemiLandUse(type="north")
    #esri.sLon, esri.sLat, esri.southLandUse = esri.getHemiLandUse(type="south")
    #esri.lon, esri.lat, esri.landUse = esri.getHemiLandUse(type="south")
    #esri.drawRegion(regionBound=taiwanDictBoundary, localDictBoundary=None)
    #print(esri.getTaiwanUrbanRatio())
    #esri.getTaiwanEachCateRatio()
    # >>>>> draw YunLin >>>>>
    #esri.lon, esri.lat  = esri.getLonLat(dictBoundary=ESRI_10mInfo["southBound"])
    #esri.cutEdge(yunlinDictBoundary)
    #esri.drawYunLin()
    #print(esri.getUrbanRatio())
    
    
