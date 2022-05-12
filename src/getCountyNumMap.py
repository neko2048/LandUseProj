import numpy as np
import json
from countyJudge import CountyJudger
from landUse import LandUseDataLoader

if __name__ == "__main__":
    dataDirs = {
    "landUseInfo": "../data/CJCHEN_30s.json", 
    "colorMap": "../data/LU24type.json", 
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
    luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    #luDataLoader.cutEdge(taiwanDictBoundary)
    countyNumMap = np.zeros(shape=luDataLoader.landUse.shape)

    for i in range(len(luDataLoader.lon)):
        for j in range(len(luDataLoader.lat)):
            countyNumIdx = countyJudger.searchCountyNum(x=luDataLoader.lon[i], y=luDataLoader.lat[j])
            if i % 100 == 0 and j % 100 ==0:
                print("{:04d}/{}, {:04d}/{}: {}".format(i, len(luDataLoader.lon), j, len(luDataLoader.lat), countyNumIdx))
            countyNumMap[j, i] = countyNumIdx
    np.save("../data/{}_countyNumMap.npy".format(luDataLoader.landUseName), countyNumMap)

