import numpy as np
from matplotlib.pyplot import *
from landUse import *
from matplotlib.colors import ListedColormap
from matplotlib import colors as c

class DiffSys():
    def __init__(self, dataLoader1, dataLoader2):
        self.dataLoader1 = dataLoader1
        self.dataLoader2 = dataLoader2

    def getTotalDiff(self):
        if self.dataLoader2.landUse.shape[0] * self.dataLoader2.landUse.shape[1] >= \
           self.dataLoader1.landUse.shape[0] * self.dataLoader1.landUse.shape[1]:
           largeArray = self.dataLoader2.landUse
           smallArray = self.dataLoader1.landUse
        else:
           largeArray = self.dataLoader1.landUse
           smallArray = self.dataLoader2.landUse

        diff = np.zeros(largeArray.shape)

        #for i in range(largeArray.shape[0]):
        #    for j in range(largeArray.shape[1]):
        #        xSampledIdx = int(i / largeArray.shape[0] * smallArray.shape[0])
        #        ySampledIdx = int(j / largeArray.shape[1] * smallArray.shape[1])
        #        sampleValue = smallArray[xSampledIdx, ySampledIdx]
        #        if sampleValue != largeArray[i, j]:
        #            diff[i, j] = sampleValue
        for i in range(largeArray.shape[0]):
            for j in range(largeArray.shape[1]):
                if smallArray[i, j] != largeArray[i, j]:
                    diff[i, j] = smallArray[i, j]
        return diff

    def getDiff(self, diffIdx):
        array1 = self.dataLoader1.landUse
        array2 = self.dataLoader2.landUse

        diff = np.zeros(self.dataLoader1.landUse.shape)
        urban1 = array1 == diffIdx
        urban2 = array2 == diffIdx
        diff[urban1] = 1
        diff[urban2] = 2
        diff[np.logical_and(urban1, urban2)] = 3
        # 3: common, 2: dataLoader2, 1: dataLoader1
        return diff


    def drawDiffrence(self, diff, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap([x[0] for x in self.dataLoader1.colorMap.values()])
        cmapTick = [x[1] for x in self.dataLoader1.colorMap.values()]
        baseLon = self.dataLoader1.lon
        baseLat = self.dataLoader1.lat
        baseLandUse = self.dataLoader1.landUse
        #landUse = np.full(fill_value=17, shape=landUse.shape)
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20+4, 20)))
        #pcolormesh(baseLon, baseLat, baseLandUse, 
        #vmin=np.min(list(map(int, self.dataLoader1.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.dataLoader1.colorMap.keys())))+0.5, cmap=cmap)
        #cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        #cb.set_ticklabels(cmapTick)
        #cb.ax.tick_params(labelsize=17)

        pcolormesh(baseLon, baseLat, np.ma.masked_array(diff, diff == 0), color="white", edgecolor=None, 
                   vmin=np.min(list(map(int, self.dataLoader1.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.dataLoader1.colorMap.keys())))+0.5, cmap=cmap)
        cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        cb.set_ticklabels(cmapTick)
        cb.ax.tick_params(labelsize=17)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], 
                 [labelBound["initLat"], labelBound["initLat"], labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        if hasattr(self.dataLoader1, "countyNumMap"):
            countyNumMap = self.dataLoader1.countyNumMap
            uniqueCountNum = np.unique(self.dataLoader1.countyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(baseLon, baseLat, ~np.isnan(countyNumMap), colors='black')
            for i in uniqueCountNum:
                contour(baseLon, baseLat, countyNumMap==i, colors='black')
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{d1} versus {d2} \n {d1}'.format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName), fontsize=30)
        savefig("Diff_{d1}_{d2}_{d1}_{rg}.jpg".format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName, rg=regionBound["regionName"]), dpi=300)

    def drawUrbanDiffrence(self, diff, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap(["red", "blue", "green"])
        cmapTick = [self.dataLoader1.landUseName, self.dataLoader2.landUseName, "Common"]
        baseLon = self.dataLoader1.lon
        baseLat = self.dataLoader1.lat
        baseLandUse = self.dataLoader1.landUse
        #landUse = np.full(fill_value=17, shape=landUse.shape)
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20, 20)))
        #pcolormesh(baseLon, baseLat, baseLandUse, 
        #vmin=np.min(list(map(int, self.dataLoader1.colorMap.keys())))-0.5, vmax=np.max(list(map(int, self.dataLoader1.colorMap.keys())))+0.5, cmap=cmap)
        #cb = colorbar(ticks=[x for x in range(1, len(cmapTick)+1)])
        #cb.set_ticklabels(cmapTick)
        #cb.ax.tick_params(labelsize=17)
        pcolormesh(baseLon, baseLat, np.ma.masked_array(diff, diff == 0), 
                   cmap=cmap, edgecolor=None, vmin=0.5, vmax=3.5)
        #cb = colorbar(ticks=[1, 2, 3])
        #cb.set_ticklabels(cmapTick)
        #cb.ax.tick_params(labelsize=17)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], 
                 [labelBound["initLat"], labelBound["initLat"], labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        if hasattr(self.dataLoader1, "countyNumMap"):
            countyNumMap = self.dataLoader1.countyNumMap
            uniqueCountNum = np.unique(self.dataLoader1.countyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(baseLon, baseLat, ~np.isnan(countyNumMap), colors='black')
            for i in uniqueCountNum:
                contour(baseLon, baseLat, countyNumMap==i, colors='black')
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{d1} (Red) versus \n{d2} (Blue)\nCommon (Green)'.format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName), fontsize=30)
        savefig("urbanDiff_{d1}_{d2}_{d1}_{rg}.jpg".format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName, rg=regionBound["regionName"]), dpi=300)


    def drawInnerWaterDiffrence(self, diff, regionBound, labelBound=None, figsize=None):
        cmap = ListedColormap(["white", "red", "blue", "green"])
        cmapTick = [self.dataLoader1.landUseName, self.dataLoader2.landUseName, "Common"]
        baseLon = self.dataLoader1.lon
        baseLat = self.dataLoader1.lat
        baseLandUse = self.dataLoader1.landUse
        dlon = regionBound["endLon"] - regionBound["initLon"]
        dlat = regionBound["endLat"] - regionBound["initLat"]
        fig = subplots(1, 1, figsize=(figsize or (dlon/dlat*20, 20)))
        if hasattr(self.dataLoader1, "countyNumMap"):
            diff[np.isnan(self.dataLoader1.countyNumMap)] = 0
            countyNumMap = self.dataLoader1.countyNumMap
            uniqueCountNum = np.unique(self.dataLoader1.countyNumMap)
            uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
            contour(baseLon, baseLat, ~np.isnan(countyNumMap), colors='grey')
            for i in uniqueCountNum:
                contour(baseLon, baseLat, countyNumMap==i, colors='grey')
        pcolormesh(baseLon, baseLat, np.ma.masked_array(diff, diff == 0), \
                   cmap=cmap, edgecolor=None, vmin=-0.5, vmax=3.5, zorder=4)

        if labelBound:
            plot([labelBound["initLon"], labelBound["endLon"], \
			     labelBound["endLon"], labelBound["initLon"], labelBound["initLon"]], \
                 [labelBound["initLat"], labelBound["initLat"], \
				 labelBound["endLat"], labelBound["endLat"], labelBound["initLat"]], 
                 color='red', linewidth=10)
        #if hasattr(self.dataLoader1, "countyNumMap"):
        #    countyNumMap = self.dataLoader1.countyNumMap
        #    uniqueCountNum = np.unique(self.dataLoader1.countyNumMap)
        #    uniqueCountNum = uniqueCountNum[~np.isnan(uniqueCountNum)]
        #    contour(baseLon, baseLat, ~np.isnan(countyNumMap), colors='grey')
        #    for i in uniqueCountNum:
        #        contour(baseLon, baseLat, countyNumMap==i, colors='grey')
        xlabel('Longitude', fontsize=30)
        ylabel('Latitude', fontsize=30)
        xticks(fontsize=30)
        yticks(fontsize=30)
        xlim(regionBound['initLon'], regionBound['endLon'])
        ylim(regionBound['initLat'], regionBound['endLat'])
        title('{d1} (Red) versus \n{d2} (Blue)\nCommon (Green)' \
			  .format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName), \
			  fontsize=30)
        savefig("waterDiff_{d1}_{d2}_{d1}_{rg}.jpg" \
		.format(d1=self.dataLoader1.landUseName, d2=self.dataLoader2.landUseName, rg=regionBound["regionName"]), \
		dpi=300)


if __name__ == "__main__":
    dataDirs2 = {
    #"landUseInfo": "../data/MODIS_5s1km.json", 
    "landUseInfo": "../data/MODIS_5s.json", 
    "colorMap": "../data/loachColor/modis20types.json", 
    #"countyNumMap": "../data/geo1km.npy",
    "countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
    }

    dataDirs1 = {
    #"landUseInfo": "../data/MODIS_5s_NLSC2015_1km.json", 
    "landUseInfo": "../data/MODIS_5s_NLSC2015.json", 
    "colorMap": "../data/loachColor/modis20types.json", 
    "countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
    #"countyNumMap": "../data/geo1km.npy",
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
    luDataLoader1 = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs1)
    #luDataLoader1 = GeoDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs1)
    luDataLoader1.landUse = luDataLoader1.loadData()
    luDataLoader1.lon, luDataLoader1.lat = luDataLoader1.getLonLat()
    luDataLoader1.cutEdge(taiwanDictBoundary)

    luDataLoader2 = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs2)
    #luDataLoader2 = GeoDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs2)
    luDataLoader2.landUse = luDataLoader2.loadData()
    luDataLoader2.lon, luDataLoader2.lat = luDataLoader2.getLonLat()
    luDataLoader2.cutEdge(taiwanDictBoundary)

    diffSys = DiffSys(luDataLoader1, luDataLoader2)
    #diff = diffSys.getDiff()
    #diffSys.drawDiffrence(diff, regionBound=yunlinDictBoundary, figsize=None)

	#urbanDiff = diffSys.getDiff(diffIdx=13)
    #diffSys.drawUrbanDiffrence(urbanDiff, regionBound=taiwanDictBoundary, figsize=None)

    waterDiff = diffSys.getDiff(diffIdx=17)
    diffSys.drawInnerWaterDiffrence(waterDiff, regionBound=taiwanDictBoundary, figsize=None)


