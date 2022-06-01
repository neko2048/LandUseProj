import numpy as np
from matplotlib.pyplot import *
from test import *
from matplotlib.colors import ListedColormap
from matplotlib import colors as c

class DiffSys:
    def __init__(self, data1, data2):
        self.data1 = data1
        self.data2 = data2
        self.urbanIdx1 = self.data1.getUrbanIndex()
        self.urbanIdx2 = self.data2.getUrbanIndex()
        self.data1.isUrban = self.getIsUrban(data1.landUse, self.urbanIdx1)
        self.data2.isUrban = self.getIsUrban(data2.landUse, self.urbanIdx2)

    def getIsUrban(self, landUse, urbanIdx):
        return landUse == urbanIdx

    def minusBoth(self, smallArray, largeArray):
        diff = np.zeros(largeArray.shape)
        for i in range(largeArray.shape[0]):
            for j in range(largeArray.shape[1]):
                xSampledIdx = int(i / largeArray.shape[0] * smallArray.shape[0])
                ySampledIdx = int(j / largeArray.shape[1] * smallArray.shape[1])
                sampleValue = smallArray[xSampledIdx, ySampledIdx]
                if sampleValue and largeArray[i, j]:
                    diff[i, j] = 3
                elif sampleValue and not largeArray[i, j]:
                    diff[i, j] = 2
                elif not sampleValue and largeArray[i, j]:
                    diff[i, j] = 1
        return diff

    def drawYunlinDiff(self, baseSys, compareSys):
        cmap = ListedColormap([x[0] for x in compareSys.colorMap.values()])
        cmapTick = [x[1] for x in compareSys.colorMap.values()]
        #cmap = np.vstack((cmap, np.full_like(shape=np.)))
        fig = subplots(1, 1, figsize=(16, 7))
        pcolormesh(compareSys.lon, compareSys.lat, compareSys.landUse, 
        vmin=np.min(list(compareSys.colorMap.keys()))-0.5, vmax=np.max(list(compareSys.colorMap.keys()))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)

        diff = self.minusBoth(baseSys.isUrban, compareSys.isUrban)
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 1), cmap=c.ListedColormap(['red']))
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 2), cmap=c.ListedColormap(['blue']))
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 3), cmap=c.ListedColormap(['black']))
        title("Difference of Urban | {} Based | {}: (RED) | {} (BLUE) | COMMON (BLACK) ".format(compareSys.landUseName, compareSys.landUseName, baseSys.landUseName))
        savefig('{}_{}YunlinDiff.jpg'.format(compareSys.landUseName, baseSys.landUseName), dpi=300)

    def drawTaiwanDiff(self, baseSys, compareSys):
        cmap = ListedColormap([x[0] for x in compareSys.colorMap.values()])
        cmapTick = [x[1] for x in compareSys.colorMap.values()]
        dlon = taiwanDictBoundary["endLon"] - taiwanDictBoundary["initLon"]
        dlat = taiwanDictBoundary["endLat"] - taiwanDictBoundary["initLat"]
        fig = subplots(1, 1, figsize=(dlon/dlat*20, 20))
        #cmap = np.vstack((cmap, np.full_like(shape=np.)))
        #fig = subplots(1, 1, figsize=(16, 16))
        pcolormesh(compareSys.lon, compareSys.lat, compareSys.landUse, 
        vmin=np.min(list(compareSys.colorMap.keys()))-0.5, vmax=np.max(list(compareSys.colorMap.keys()))+0.5, cmap=cmap)
        #cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        #cb.set_ticklabels(cmapTick)
        #cb.ax.tick_params(labelsize=25)

        diff = self.minusBoth(baseSys.isUrban, compareSys.isUrban)
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 1), cmap=c.ListedColormap(['red']))
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 2), cmap=c.ListedColormap(['blue']))
        pcolormesh(compareSys.lon, compareSys.lat, np.ma.masked_array(diff, diff != 3), cmap=c.ListedColormap(['black']))
        title("Difference of Urban based on {}\n{}: (RED) | {} (BLUE) | COMMON (BLACK) ".\
              format(compareSys.landUseName, compareSys.landUseName, baseSys.landUseName), fontsize=30)
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        savefig('{}_{}TaiwanDiff.jpg'.format(compareSys.landUseName, baseSys.landUseName), dpi=300)

    def drawTaiwanDiffForESRI(self, baseSys, compareSys=esri):
        cmap = ListedColormap([x[0] for x in compareSys.colorMap.values()])
        cmapTick = [x[1] for x in compareSys.colorMap.values()]
        dlon = taiwanDictBoundary["endLon"] - taiwanDictBoundary["initLon"]
        dlat = taiwanDictBoundary["endLat"] - taiwanDictBoundary["initLat"]
        fig = subplots(1, 1, figsize=(dlon/dlat*20, 20))
        pcolormesh(compareSys.sLon, compareSys.sLat, compareSys.southLandUse, 
        vmin=np.min(list(compareSys.colorMap.keys()))-0.5, vmax=np.max(list(compareSys.colorMap.keys()))+0.5, cmap=cmap)
        pcolormesh(compareSys.nLon, compareSys.nLat, compareSys.northLandUse, 
        vmin=np.min(list(compareSys.colorMap.keys()))-0.5, vmax=np.max(list(compareSys.colorMap.keys()))+0.5, cmap=cmap)

        # calculate north part
        baseSys.isNorthUrban = self.getIsUrban(baseSys.northLandUse, baseSys.getUrbanIndex())
        compareSys.isNorthUrban = self.getIsUrban(compareSys.northLandUse, compareSys.getUrbanIndex())
        northDiff = self.minusBoth(baseSys.isNorthUrban, compareSys.isNorthUrban)
        pcolormesh(compareSys.nLon, compareSys.nLat, np.ma.masked_array(northDiff, northDiff != 1), cmap=c.ListedColormap(['red']))
        pcolormesh(compareSys.nLon, compareSys.nLat, np.ma.masked_array(northDiff, northDiff != 2), cmap=c.ListedColormap(['blue']))
        pcolormesh(compareSys.nLon, compareSys.nLat, np.ma.masked_array(northDiff, northDiff != 3), cmap=c.ListedColormap(['black']))

        # calculate south part
        baseSys.isSouthUrban = self.getIsUrban(baseSys.southLandUse, baseSys.getUrbanIndex())
        compareSys.isSouthUrban = self.getIsUrban(compareSys.southLandUse, compareSys.getUrbanIndex())
        southDiff = self.minusBoth(baseSys.isSouthUrban, compareSys.isSouthUrban)
        pcolormesh(compareSys.sLon, compareSys.sLat, np.ma.masked_array(southDiff, southDiff != 1), cmap=c.ListedColormap(['red']))
        pcolormesh(compareSys.sLon, compareSys.sLat, np.ma.masked_array(southDiff, southDiff != 2), cmap=c.ListedColormap(['blue']))
        pcolormesh(compareSys.sLon, compareSys.sLat, np.ma.masked_array(southDiff, southDiff != 3), cmap=c.ListedColormap(['black']))

        title("Difference of Urban based on {}\n{}: (RED) | {} (BLUE) | COMMON (BLACK) ".\
              format(compareSys.landUseName, compareSys.landUseName, baseSys.landUseName), fontsize=30)
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        savefig('{}_{}TaiwanDiff.jpg'.format(compareSys.landUseName, baseSys.landUseName), dpi=300)

if __name__ == "__main__":
    def cutPartEdge(lon, lat, landUse, dictBoundary, type):
        lonLimit = np.logical_and(lon >= dictBoundary['initLon'], lon <= dictBoundary['endLon'])
        if type=="north":
            latLimit = np.logical_and(lat >= 23.5, lat <= dictBoundary['endLat'])
        elif type=="south":
            latLimit = np.logical_and(lat >= dictBoundary['initLat'], lat <= 23.5)
        landUse = landUse[latLimit][:, lonLimit]#[::-1]
        lon = lon[lonLimit]
        lat = lat[latLimit]
        return lon, lat, landUse

    # USGS, Modis
    UMcompare = DiffSys(usgs, modis)
    #UMcompare.drawYunlinDiff(baseSys=usgs, compareSys=modis)
    UMcompare.drawTaiwanDiff(baseSys=usgs, compareSys=modis)

    # USGS, CJCHEN
    UCJcompare = DiffSys(usgs, cjchen)
    #UCJcompare.drawYunlinDiff(baseSys=usgs, compareSys=cjchen)
    UCJcompare.drawTaiwanDiff(baseSys=usgs, compareSys=cjchen)

    # Modis, CJCHEN
    MCJcompare = DiffSys(modis, cjchen)
    #MCJcompare.drawYunlinDiff(baseSys=modis, compareSys=cjchen)
    MCJcompare.drawTaiwanDiff(baseSys=modis, compareSys=cjchen)

    # Modis, ESRI
    MEcompare = DiffSys(modis, esri)
    modis.sLon, modis.sLat, modis.southLandUse = cutPartEdge(modis.lon, modis.lat, modis.landUse,\
                                                             dictBoundary=taiwanDictBoundary, type="south")
    modis.nLon, modis.nLat, modis.northLandUse = cutPartEdge(modis.lon, modis.lat, modis.landUse,\
                                                             dictBoundary=taiwanDictBoundary, type="north")
    #MEcompare.drawYunlinDiff(baseSys=modis, compareSys=esri)
    MEcompare.drawTaiwanDiffForESRI(baseSys=modis, compareSys=esri)

    # CJCHEN, ESRI
    CJEcompare = DiffSys(cjchen, esri)
    cjchen.sLon, cjchen.sLat, cjchen.southLandUse = cutPartEdge(cjchen.lon, cjchen.lat, cjchen.landUse,\
                                                             dictBoundary=taiwanDictBoundary, type="south")
    cjchen.nLon, cjchen.nLat, cjchen.northLandUse = cutPartEdge(cjchen.lon, cjchen.lat, cjchen.landUse,\
                                                             dictBoundary=taiwanDictBoundary, type="north")
    #MEcompare.drawYunlinDiff(baseSys=cjchen, compareSys=esri)
    CJEcompare.drawTaiwanDiffForESRI(baseSys=cjchen, compareSys=esri)
