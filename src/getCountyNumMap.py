import numpy as np
import json
from countyJudge import CountyJudger
from landUse import LandUseDataLoader, GeoDataLoader
from landUseESRI import ESRIDataLoader
if __name__ == "__main__":
    dataDirs = {
    "landUseInfo": "../data/MODIS_5s_NLSC2015rpurban1km.json",
    #"landUseInfo": "../data/MODIS_5s.json", 
    "colorMap": "../data/LU20type.json", 
    #"countyNumMap": "../data/USGS_30s_countyNumMap.npy",
    }
    taiwanDictBoundary = {
    'initLon': 120,
    'endLon':  122.282366,  
    'initLat': 21.752632,
    'endLat': 25.459580, 
    'regionName': "Taiwan", 
    }

    shpDir = '../data/taiwanCountyShape/TOWN_MOI_1100415.shp'
    countyJudger = CountyJudger(shpDir)
    #luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader = GeoDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    #luDataLoader.cutEdge(taiwanDictBoundary)
    countyNumMap = np.zeros(shape=luDataLoader.landUse.shape)

    if len(luDataLoader.lon.shape) == 1:
        print(luDataLoader.lon.shape)
        for i in range(len(luDataLoader.lon)):
            for j in range(len(luDataLoader.lat)):
                countyNumIdx = countyJudger.searchCountyNum(x=luDataLoader.lon[i], y=luDataLoader.lat[j])
                if i % 100 == 0 and j % 100 ==0:
                    print("{:04d}/{}, {:04d}/{}: {}".format(i, len(luDataLoader.lon), j, len(luDataLoader.lat), countyNumIdx))
                countyNumMap[j, i] = countyNumIdx

    elif len(luDataLoader.lon.shape) == 2:
        print(luDataLoader.lon.shape)
        for i in range(luDataLoader.lon.shape[0]):
            for j in range(luDataLoader.lat.shape[1]):
                countyNumIdx = countyJudger.searchCountyNum(x=luDataLoader.lon[i, j], y=luDataLoader.lat[i, j])
                if i % 100 == 0 and j % 100 ==0:
                    print("{:04d}/{}, {:04d}/{}: {}".format(i, luDataLoader.lon.shape[0], j, luDataLoader.lon.shape[1], countyNumIdx))
                countyNumMap[i, j] = countyNumIdx
    np.save("../data/{}_countyNumMap.npy".format(luDataLoader.landUseName), countyNumMap)

