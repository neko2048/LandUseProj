import numpy as np
from matplotlib.pyplot import *
import re
from matplotlib.colors import ListedColormap
import tifffile as tiff
import twd97
import re 

class LandUseData:
    def __init__(self, anchorLon, anchorlat, dataInfo):
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
        self.colorMap = dataInfo["colorMap"]

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

    def getUrbanIndex(self):
        for idx, info in self.colorMap.items():
            if "urban" in info[-1] or "Urban" in info[-1]:
                urbanIndex = idx
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

    def getEachCatRatio(self):
        waterIndex = self.getWaterIndex()
        numTotal = np.sum(self.landUse != waterIndex)
        for idx, info in self.colorMap.items():
            numTarget = np.sum(self.landUse == idx)
            print(info, numTarget / numTotal*100)

    def drawYunLin(self):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        fig = subplots(1, 1, figsize=(16, 7))
        pcolormesh(self.lon, self.lat, self.landUse, 
        vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        xlim(initLon, endLon)
        ylim(initLat, endLat)
        title('{} LandUse'.format(self.landUseName))
        savefig("{}_yunlin.jpg".format(self.landUseName), dpi=300)

    def drawTaiwan(self, localDictBoundary=None):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        fig = subplots(1, 1, figsize=(20, 20))
        pcolormesh(self.lon, self.lat, self.landUse, 
        vmin=np.min(list(self.colorMap.keys()))-0.5, vmax=np.max(list(self.colorMap.keys()))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)

        if localDictBoundary:
            plot([localDictBoundary["initLon"], localDictBoundary["endLon"], localDictBoundary["endLon"], localDictBoundary["initLon"], localDictBoundary["initLon"]], 
                 [localDictBoundary["initLat"], localDictBoundary["initLat"], localDictBoundary["endLat"], localDictBoundary["endLat"], localDictBoundary["initLat"]], 
                 color='red', linewidth=10)
        xlim(taiwanDictBoundary["initLon"], taiwanDictBoundary["endLon"])
        ylim(taiwanDictBoundary["initLat"], taiwanDictBoundary["endLat"])
        title('{} LandUse'.format(self.landUseName), fontsize=30)
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        savefig("{}_Taiwan.jpg".format(self.landUseName), dpi=300)





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

# >>>>> user defined >>>>>
taiwanInitLon, taiwanEndLon = 120, 122.282366
yunInitLon, yunEndLon = 120.01, 121.00
taiwanInitLat, taiwanEndLat = 21.752632, 25.459580
yunInitLat, yunEndLat = 23.4853847, 23.9194608
# <<<<< user defined <<<<<
taiwanDictBoundary = {
'initLon': taiwanInitLon,
'endLon':  taiwanEndLon,  
'initLat': taiwanInitLat,
'endLat': taiwanEndLat
}
yunlinDictBoundary = {
'initLon': yunInitLon,
'endLon':  yunEndLon,  
'initLat': yunInitLat,
'endLat': yunEndLat
}
# >>>>> data name >>>>>
USGS_30Info = {
"landUseName": "USGS_30s", 
"folderDir": "/data/loach/Data/GEOG/landuse_30s/",
"baseLon": -179.99583,  # degree
"baseLon": -179.99583, # degree
"baseLat": -89.99583, # degree
"dx": 0.00833333, # degree
"dy": 0.00833333, # degree
"tilex": 1200,
"tiley": 1200,
"colorMap": { # USGS
     1: ["#e21417", "urban"], 
     2: ["#ecb400", "dryland"], 
     3: ["#ecb400", "irrigated cropland"], 
     4: ["#ecb400", "mixed dryland/irrigated"], 
     5: ["#ecb400", "cropland/grassland"], 
     6: ["#ecb400", "cropland/woodland"], 
     7: ["#69b076", "grassland"], 
     8: ["#69b076", "shrubland"], 
     9: ["#69b076", "mixed shrubland/grassland"], 
    10: ["#69b076", "savanna"], 
    11: ["#007b43", "deciduous broadleaf"], 
    12: ["#00552e", "deciduous needleleaf"], 
    13: ["#007b43", "evergreen broadleaf"], 
    14: ["#00552e", "evergreen needleleaf"], 
    15: ["#006e54", "mixed forest"], 
    16: ["#54aaea", "water bodies"], 
    17: ["#946243", "herbaceous wetland"], 
    18: ["#946243", "wooden wetland"], 
    19: ["#c89932", "barren or sparsely vegetated"], 
    20: ["#69821b", "herbaceous tundra"], 
    21: ["#69821b", "wooded tundra"], 
    22: ["#69821b", "mixed tundra"], 
    23: ["#69821b", "bare ground tundra"], 
    24: ["#ffffff", "snow or ice"], 
    }
}
MODIS_15Info = {
"landUseName": "MODIS_15s", 
"folderDir": "/data/loach/Data/GEOG/modis_landuse_20class_15s/",
"baseLon": -179.9979167, # degree
"baseLat": -89.9979167, # degree
"dx": 0.00416667, # degree
"dy": 0.00416667, # degree
"tilex": 2400,
"tiley": 2400,
"colorMap": {
    1:  ["#00552e", "Evergreen Needleleaf"], 
    2:  ["#007b43", "Evergreen Broadleaf"], 
    3:  ["#00552e", "Deciuous Needleleaf"], 
    4:  ["#007b43", "Deciuous Broadleaf"], 
    5:  ["#006e54", "Mixed Forests"], 
    6:  ["#69b076", "Closed Shrublands"], 
    7:  ["#69b076", "Open Shrublands"], 
    8:  ["#69b076", "Woody Savannas"], 
    9:  ["#69b076", "Savannas"], 
    10: ["#69b076", "Grasslands"], 
    11: ["#946243", "Permanent Wetlands"], 
    12: ["#ecb400", "Cropland"], 
    13: ["#e21417", "Urban and Built-up"], 
    14: ["#ecb400", "Cropland/Natural Vegetation"], 
    15: ["#ffffff", "Snow and Ice"], 
    16: ["#c89932", "Barren or sparsely Vegetated"], 
    17: ["#54aaea", "Water"], 
    18: ["#69821b", "Wooded Tundra"], 
    19: ["#69821b", "Mixed Tundra"], 
    20: ["#69821b", "Barren Tundra"], 
    }
}
CJCHEN_30Info = {
"landUseName": "CJCHEN_30s", 
"folderDir": "/data/loach/Data/GEOG.CJChen/landuse_30s/",
"baseLon": -179.99583,  # degree
"baseLon": -179.99583, # degree
"baseLat": -89.99583, # degree
"dx": 0.00833333, # degree
"dy": 0.00833333, # degree
"tilex": 1200,
"tiley": 1200,
"colorMap": {
     1: ["#e21417", "urban"], 
     2: ["#ecb400", "dryland"], 
     3: ["#ecb400", "irrigated cropland"], 
     4: ["#ecb400", "mixed dryland/irrigated"], 
     5: ["#ecb400", "cropland/grassland"], 
     6: ["#ecb400", "cropland/woodland"], 
     7: ["#69b076", "grassland"], 
     8: ["#69b076", "shrubland"], 
     9: ["#69b076", "mixed shrubland/grassland"], 
    10: ["#69b076", "savanna"], 
    11: ["#007b43", "deciduous broadleaf"], 
    12: ["#00552e", "deciduous needleleaf"], 
    13: ["#007b43", "evergreen broadleaf"], 
    14: ["#00552e", "evergreen needleleaf"], 
    15: ["#006e54", "mixed forest"], 
    16: ["#54aaea", "water bodies"], 
    17: ["#006e54", "herbaceous wetland"], 
    18: ["#006e54", "wooden wetland"], 
    19: ["#006e54", "barren or sparsely vegetated"], 
    }
}

ESRI_10mInfo = {
"landUseName": "ESRI_10m", 
"southFileDir": "./ESRI/51Q100_lonlat.tif",
"southBound": {
    "initLon": 119.185517,
    "endLon" : 124.36715,
    "initLat": 15.234567,
    "endLat" : 24.435789,
    },
"northFileDir": "./ESRI/51R100_lonlat.tif",
"northBound": {
    "initLon": 118.598375,
    "endLon" : 127.363256,
    "initLat": 23.300906,
    "endLat" : 32.572875,
    },
"colorMap": { # https://www.arcgis.com/home/item.html?id=d6642f8a4f6d4685a24ae2dc0c73d4ac
     1: ["#429bde", "Water"], 
     2: ["#3a7d47", "Trees"], 
     3: ["#88af52", "Grass"], 
     4: ["#748bc2", "Flooded vegetation"], 
     5: ["#e3c765", "Crops"], 
     6: ["#d7be9f", "Scrub/shrub"], 
     7: ["#d5203f", "Built Area"], 
     8: ["#a59b8f", "Bare ground"], 
     9: ["#ffffff", "Snow/Ice"], 
    10: ["#000000", "Clouds"], 

    }
}
# <<<<< data name <<<<<

usgs = LandUseData(anchorLon = 121, anchorlat=23.5, dataInfo=USGS_30Info)
usgs.landUse = usgs.loadData()
usgs.lon, usgs.lat = usgs.getLonLat()
usgs.cutEdge(taiwanDictBoundary)
usgs.drawTaiwan(localDictBoundary=None)
#usgs.cutEdge(yunlinDictBoundary)
#usgs.drawYunLin()
#print(usgs.getUrbanRatio())
#usgs.getEachCatRatio()

modis = LandUseData(anchorLon = 121, anchorlat=23.5, dataInfo=MODIS_15Info)
modis.landUse = modis.loadData()
modis.lon, modis.lat = modis.getLonLat()
modis.cutEdge(taiwanDictBoundary)
modis.drawTaiwan(localDictBoundary=None)
#modis.drawTaiwan(yunlinDictBoundary)
#modis.cutEdge(yunlinDictBoundary)
#modis.drawYunLin()
#print(modis.getUrbanRatio())
#modis.getEachCatRatio()

cjchen = LandUseData(anchorLon = 121, anchorlat=23.5, dataInfo=CJCHEN_30Info)
cjchen.landUse = cjchen.loadData() 
cjchen.lon, cjchen.lat = cjchen.getLonLat()
cjchen.cutEdge(taiwanDictBoundary)
#cjchen.drawTaiwan(localDictBoundary=None)
#cjchen.cutEdge(yunlinDictBoundary)
#cjchen.drawYunLin()
#print(cjchen.getUrbanRatio())
#cjchen.getEachCatRatio()

esri = ESRI(dataInfo = ESRI_10mInfo)
# >>>>> draw Taiwan >>>>>
esri.nLon, esri.nLat, esri.northLandUse = esri.getPartLandUse(type="north")
esri.sLon, esri.sLat, esri.southLandUse = esri.getPartLandUse(type="south")
esri.lon, esri.lat, esri.landUse = esri.getPartLandUse(type="south")
#esri.drawTaiwan(localDictBoundary=None)
#print(esri.getTaiwanUrbanRatio())
#esri.getTaiwanEachCateRatio()

# >>>>> draw YunLin >>>>>
#esri.lon, esri.lat  = esri.getLonLat(dictBoundary=ESRI_10mInfo["southBound"])
#esri.cutEdge(yunlinDictBoundary)
#esri.drawYunLin()
#print(esri.getUrbanRatio())

