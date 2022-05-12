import numpy as np
from matplotlib.pyplot import *
from countyJudge import CountyJudger
from landUse import LandUseDataLoader
import json
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
    luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataInfo=targetLandUseInfo)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    luDataLoader.cutEdge(taiwanDictBoundary)


    countyNumMap = np.load("../data/{}_countyNumMap.npy".format(targetLandUseInfo["landUseName"]))
    fig = subplots(1, 1, figsize=(20, 20))
    pcolormesh(luDataLoader.lon, luDataLoader.lat, countyNumMap, cmap="jet")
    xticks(fontsize=30)
    yticks(fontsize=30)
    title(targetLandUseInfo["landUseName"], fontsize=30)
    savefig('../fig/{}_countyNumMap.jpg'.format(targetLandUseInfo["landUseName"]))




