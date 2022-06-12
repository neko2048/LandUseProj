import numpy as np
from matplotlib.pyplot import *
from matplotlib.colors import ListedColormap
import tifffile as tiff
import json
from landUse import LandUseDataLoader


class ESRIDataLoader:
    def __init__(self, dataDirs, hemiType):
        self.dataDirs = dataDirs
        self.hemiType = hemiType
        self.landUseInfo = self.dataDirs["landUseInfo"]
        self.dataInfo = self.getJSON("landUseInfo")
        self.colorMap = self.getJSON("colorMap")
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
        self.nLon, self.nLat = self.nEsri.lon, self.nEsri.lat
        self.sLon, self.sLat = self.sEsri.lon, self.sEsri.lat
        self.nLandUse, self.sLandUse = self.nEsri.landUse, self.sEsri.landUse
        self.colorMap = self.nEsri.colorMap
        self.nCountyNumMap = self.nEsri.countyNumMap
        self.sCountyNumMap = self.sEsri.countyNumMap
        self.landUseName = "ESRI_10m"

    def getEveryCatRatio(self):
        waterIndex = self.nEsri.dataInfo["waterIdx"]
        numNorthTotal = np.sum(~np.isnan(self.nEsri.countyNumMap))
        numSouthTotal = np.sum(~np.isnan(self.sEsri.countyNumMap))

        for idx, info in self.colorMap.items():
            targetIndex = int(idx)
            numNorthTarget = np.sum(self.nLandUse[~np.isnan(self.nEsri.countyNumMap)] == targetIndex)
            numSouthTarget = np.sum(self.sLandUse[~np.isnan(self.sEsri.countyNumMap)] == targetIndex)
            totalNorthArea = (np.max(self.nLat) - np.min(self.nLat)) #/ (np.max(self.nLat) - np.min(self.sLat))
            totalSouthArea = (np.max(self.sLat) - np.min(self.sLat)) #/ (np.max(self.nLat) - np.min(self.sLat))
            gridNorthArea, gridSouthArea = totalNorthArea / numNorthTotal, totalSouthArea / numSouthTotal
            ratioUp = numNorthTarget * gridNorthArea + numSouthTarget * gridSouthArea
            ratioDown = numNorthTotal * gridNorthArea + numSouthTotal * gridSouthArea
            print("{:30s}: {:.2f} %".format(info[1], ratioUp / ratioDown * 100))

    def getDrawCountyNumMap(self, dictBoundary):
        dataDirs = {
        "landUseInfo": "../data/MODIS_5s.json", 
        "colorMap": "../data/loachColor/modis20types.json", 
        "countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
        }
        luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
        luDataLoader.landUse = luDataLoader.loadData()
        luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
        luDataLoader.cutEdge(dictBoundary)
        return luDataLoader.lon, luDataLoader.lat, luDataLoader.countyNumMap

    def drawRegion(self, regionBound, localDictBoundary=None, figsize=None, countyDictBoundary=None):
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20+4, 20)))
        pcolormesh(self.nLon, self.nLat, self.nLandUse, 
        vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)
        pcolormesh(self.sLon, self.sLat, self.sLandUse, 
        vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)

        if localDictBoundary:
            plot([localDictBoundary["initLon"], localDictBoundary["endLon"], localDictBoundary["endLon"], localDictBoundary["initLon"], localDictBoundary["initLon"]], 
                 [localDictBoundary["initLat"], localDictBoundary["initLat"], localDictBoundary["endLat"], localDictBoundary["endLat"], localDictBoundary["initLat"]], 
                 color='red', linewidth=10)
        if countyDictBoundary:
            dLon, dLat, dCountyNumMap = self.getDrawCountyNumMap(countyDictBoundary)
            uniqueCountNum = np.unique(dCountyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(dLon, dLat, ~np.isnan(dCountyNumMap), colors='black')
            for i in uniqueCountNum:
                contour(dLon, dLat, dCountyNumMap==i, colors='black')
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
    northDataDirs = {
    "landUseInfo": "../data/ESRI_10m.json", 
    "colorMap": "../data/LU10type.json", 
    "countyNumMap": "../data/ESRI_10mNorth_countyNumMap.npy",
    }
    southDataDirs = {
    "landUseInfo": "../data/ESRI_10m.json", 
    "colorMap": "../data/LU10type.json", 
    "countyNumMap": "../data/ESRI_10mSouth_countyNumMap.npy",
    }
    countyNumMapInfo = {
    "landUseInfo": "../data/MODIS_5s.json", 
    "countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
    }

    nEsri = ESRIDataLoader(dataDirs = northDataDirs, hemiType="north")
    nEsri.landUse = nEsri.loadData()
    nEsri.lon, nEsri.lat = nEsri.getLonLat()
    nEsri.cutEdge(dictBoundary=taiwanDictBoundary)

    sEsri = ESRIDataLoader(dataDirs = southDataDirs, hemiType="south")
    sEsri.landUse = sEsri.loadData()
    sEsri.lon, sEsri.lat = sEsri.getLonLat()
    sEsri.cutEdge(dictBoundary=taiwanDictBoundary)
    
    mergeSys = MergeSys(nEsri, sEsri)
    mergeSys.drawRegion(regionBound=taiwanDictBoundary, countyDictBoundary=taiwanDictBoundary)
    mergeSys.getEveryCatRatio()
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
    
    
