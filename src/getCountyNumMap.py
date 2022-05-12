import numpy as np
import json
from countyJudge import CountyJudger
from landUse import LandUseDataLoader

if __name__ == "__main__":
    taiwanDictBoundary = {
    'initLon': 120,
    'endLon':  122.282366,  
    'initLat': 21.752632,
    'endLat': 25.459580, 
    'regionName': "Taiwan", 
    }
    # >>>>> preload >>>>>
    with open("../data/USGS_30s.json") as jsonFile:
        USGS_30Info = json.load(jsonFile)
    with open("../data/MODIS_15s.json") as jsonFile:
        MODIS_15Info = json.load(jsonFile)
    with open("../data/MODIS_5s.json") as jsonFile:
        MODIS_5Info = json.load(jsonFile)
    with open("../data/CJCHEN_30s.json") as jsonFile:
        CJCHEN_30Info = json.load(jsonFile)
    # <<<<< preload <<<<<

    targetLandUseInfo = MODIS_5Info
    shpDir = '../data/taiwanCountyShape/TOWN_MOI_1100415.shp'
    countyJudger = CountyJudger(shpDir)
    luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataInfo=targetLandUseInfo)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    luDataLoader.cutEdge(taiwanDictBoundary)
    countyNumMap = np.zeros(shape=luDataLoader.landUse.shape)

    for i in range(len(luDataLoader.lon)):
        for j in range(len(luDataLoader.lat)):
            countyNumIdx = countyJudger.searchCountyNum(x=luDataLoader.lon[i], y=luDataLoader.lat[j])
            if i % 100 == 0 and j % 100 ==0:
                print("{:04d}/{}, {:04d}/{}: {}".format(i, len(luDataLoader.lon), j, len(luDataLoader.lat), countyNumIdx))
            countyNumMap[j, i] = countyNumIdx
    np.save("../data/{}_countyNumMap.npy".format(targetLandUseInfo["landUseName"]), countyNumMap)

