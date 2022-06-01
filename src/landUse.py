import numpy as np
from matplotlib.pyplot import *
from matplotlib.colors import ListedColormap
import json
import netCDF4

class LandUseDataLoader:
    def __init__(self, anchorLon, anchorlat, dataDirs):
        self.dataDirs = dataDirs
        self.dataInfo = self.getJSON("landUseInfo")
        self.anchorlon = anchorLon
        self.anchorlat = anchorlat
        self.landUseName = self.dataInfo["landUseName"]
        self.dirName = self.dataInfo["folderDir"]
        self.baseLon = self.dataInfo["baseLon"]
        self.baseLat = self.dataInfo["baseLat"]
        self.dx = self.dataInfo["dx"]
        self.dy = self.dataInfo["dy"]
        self.tilex = self.dataInfo["tilex"]
        self.tiley = self.dataInfo["tiley"]
        self.numType = self.dataInfo["numType"]
        self.waterIdx = int(self.dataInfo["waterIdx"])
        self.colorMap = self.getJSON("colorMap")
        if "countyNumMap" in self.dataDirs.keys():
            self.countyNumMap = np.load(self.dataDirs["countyNumMap"])

    def getJSON(self, name):
        with open(self.dataDirs[name]) as jsonFile:
            jsonData = json.load(jsonFile)
        return jsonData

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
        if hasattr(self, "countyNumMap"):
            self.countyNumMap = self.countyNumMap[initLatIdx:endLatIdx, initLonIdx:endLonIdx]

    def getCatIdx(self, catName):
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if catName in info[-1]:
                catIdx = idx
                return catIdx
        return None

    def getCatRatio(self, catName):
        if hasattr(self, "countyNumMap"):
            numTotal = np.sum(1 - np.isnan(self.countyNumMap))
            for idx, info in self.colorMap.items():
                idx = int(idx)
                if info[1] == catName:
                    numTarget = np.sum(self.landUse[~np.isnan(self.countyNumMap)] == idx)
                    return(numTarget / numTotal*100)
        else:
            numTotal = np.sum(self.landUse != self.waterIdx)
            for idx, info in self.colorMap.items():
                idx = int(idx)
                if idx != self.waterIdx and info[1] == catName:
                    numTarget = np.sum(self.landUse == idx)
                    return(numTarget / numTotal*100)
        return None

    def getEveryCatRatio(self):
        if hasattr(self, "countyNumMap"):
            numTotal = np.sum(1 - np.isnan(self.countyNumMap))
        else:
            numTotal = np.sum(self.landUse != self.waterIdx)
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if idx != self.waterIdx:
                numTarget = np.sum(self.landUse[~np.isnan(self.countyNumMap)] == idx)
                print("{:30s}: {:.2f} %".format(info[1], numTarget / numTotal*100))
            elif idx == self.waterIdx and hasattr(self, "countyNumMap"):
                numTarget = np.sum(np.logical_and((1 - np.isnan(self.countyNumMap)), self.landUse == idx))
                print("{:30s}: {:.2f} %".format(info[1], numTarget / numTotal*100))
            else:
                print("{:30s}: {}".format(info[1], "Not be counted"))
        return None

    def getPlaceLandType(self, lon, lat):
        lonIdx = np.argmin(np.abs(self.lon-lon))
        latIdx = np.argmin(np.abs(self.lat-lat))
        luIdx = self.landUse[latIdx, lonIdx]
        return self.colorMap[str(luIdx)][1]

    def drawRegion(self, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        lonLimit = np.logical_and(self.lon >= regionBound['initLon'], self.lon <= regionBound['endLon'])
        latLimit = np.logical_and(self.lat >= regionBound['initLat'], self.lat <= regionBound['endLat'])
        lon = self.lon[lonLimit]
        lat = self.lat[latLimit]
        landUse = self.landUse[latLimit][:, lonLimit]
        #landUse = np.full(fill_value=17, shape=landUse.shape)
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20+4, 20)))
        pcolormesh(lon, lat, landUse, 
        vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], 
                 [labelBound["initLat"], labelBound["initLat"], labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        if hasattr(self, "countyNumMap"):
            countyNumMap = self.countyNumMap
            uniqueCountNum = np.unique(self.countyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(self.lon, self.lat, ~np.isnan(countyNumMap), colors='black')
            for i in uniqueCountNum:
                contour(self.lon, self.lat, countyNumMap==i, colors='black')
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{} LandUse'.format(self.landUseName), fontsize=30)
        savefig("{}_{}.jpg".format(self.landUseName, regionBound["regionName"]), dpi=300)

class GeoDataLoader(LandUseDataLoader):
    def loadData(self):
        data = np.array(netCDF4.Dataset(str(self.dirName+self.dataInfo["fileName"]))["LU_INDEX"])[0]
        return np.array(data)

    def getLonLat(self):
        lon = np.array(netCDF4.Dataset(str(self.dirName+self.dataInfo["fileName"]))["XLONG_M"])[0]
        lat = np.array(netCDF4.Dataset(str(self.dirName+self.dataInfo["fileName"]))["XLAT_M"])[0]
        return lon, lat

    def cutEdge(self, dictBoundary):
        latBound = np.logical_and(self.lat >= dictBoundary['initLat'], self.lat <= dictBoundary['endLat'])
        lonBound = np.logical_and(self.lon >= dictBoundary['initLon'], self.lon <= dictBoundary['endLon'])
        bound = np.logical_and(latBound, lonBound)
        self.landUse = self.landUse * bound
        if hasattr(self, "countyNumMap"):
            self.countyNumMap = np.ma.masked_array(self.countyNumMap, 1 - bound)

    def getEveryCatRatio(self):
        if hasattr(self, "countyNumMap"):
            numTotal = np.sum(1 - np.isnan(self.countyNumMap))
        else:
            numTotal = np.sum(np.logical_and(self.landUse != self.waterIdx, self.landUse != 0))
        for idx, info in self.colorMap.items():
            idx = int(idx)
            if idx != self.waterIdx:
                numTarget = np.sum(self.landUse[~np.isnan(self.countyNumMap)] == idx)
                print("{:30s}: {:.2f} %".format(info[1], numTarget / numTotal*100))
            elif idx == self.waterIdx and hasattr(self, "countyNumMap"):
                numTarget = np.sum(np.logical_and((1 - np.isnan(self.countyNumMap)), self.landUse == idx))
                print("{:30s}: {:.2f} %".format(info[1], numTarget / numTotal*100))
            else:
                print("{:30s}: {}".format(info[1], "Not be counted"))
        return None

    def drawRegion(self, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap([x[0] for x in self.colorMap.values()])
        cmapTick = [x[1] for x in self.colorMap.values()]
        lon = self.lon
        lat = self.lat
        landUse = self.landUse
        #landUse = np.full(fill_value=17, shape=landUse.shape)
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20+4, 20)))
        pcolormesh(lon, lat, landUse, 
        vmin=np.min(list(map(int, self.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.colorMap.keys())))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], 
                 [labelBound["initLat"], labelBound["initLat"], labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        if hasattr(self, "countyNumMap"):
            countyNumMap = self.countyNumMap
            uniqueCountNum = np.unique(self.countyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(lon, lat, ~np.isnan(countyNumMap), colors='black')
            for i in uniqueCountNum:
                contour(lon, lat, countyNumMap==i, colors='black')
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{} LandUse'.format(self.landUseName), fontsize=30)
        savefig("{}_{}.jpg".format(self.landUseName, regionBound["regionName"]), dpi=300)

if __name__ == "__main__":
    dataDirs = {
    #"landUseInfo": "../data/MODIS_5s.json", 
    #"landUseInfo": "../data/MODIS_15s1km.json",
    #"landUseInfo": "../data/MODIS_5s_NLSC2015.json",
    "landUseInfo": "../data/NLSC2015Nearest1km.json",
    #"landUseInfo": "../data/MODIS_15s.json",
    "colorMap": "../data/loachColor/modis20types.json", 
    #"countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
    "countyNumMap": "../data/geo1km.npy",
    }
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
    taipeiDictBoundary = {
    'initLon': 121.0,
    'endLon':  121.8,
    'initLat': 24.8,
    'endLat': 25.3,
    'figratio':36,
    'regionName':"Taipei"
    }
    #luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader = GeoDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    #luDataLoader.cutEdge(taiwanDictBoundary)
    #luDataLoader.cutEdge(yunlinDictBoundary)
    #print(luDataLoader.getCatRatio(catName="urban"))
    #print(luDataLoader.getPlaceLandType(lon=120.8, lat=23.666666))
    #luDataLoader.cutEdge(yunlinDictBoundary)
    #luDataLoader.drawRegion(regionBound=yunlinDictBoundary, figsize=(17, 6))
    #luDataLoader.drawRegion(regionBound=taiwanDictBoundary, labelBound=yunlinDictBoundary, figsize=(20, 20))
    #luDataLoader.drawRegion(regionBound=taiwanDictBoundary, figsize=None)
    luDataLoader.drawRegion(regionBound=taipeiDictBoundary, figsize=None)
    #luDataLoader.getEveryCatRatio()


