import numpy as np
from matplotlib.pyplot import *
from countyJudge import CountyJudger
from landUse import LandUseDataLoader
import json
if __name__ == "__main__":
    dataDirs = {
    "landUseInfo": "../data/MODIS_5s.json", 
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

    luDataLoader = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoader.landUse = luDataLoader.loadData()
    luDataLoader.lon, luDataLoader.lat = luDataLoader.getLonLat()
    #luDataLoader.cutEdge(taiwanDictBoundary)


    countyNumMap = np.load("../data/{}_countyNumMap.npy".format(luDataLoader.landUseName))
    fig = subplots(1, 1, figsize=(20, 20))
    pcolormesh(luDataLoader.lon, luDataLoader.lat, countyNumMap, cmap="jet")
    xticks(fontsize=30)
    yticks(fontsize=30)
    title(luDataLoader.landUseName, fontsize=30)
    savefig('../fig/{}_countyNumMap.jpg'.format(luDataLoader.landUseName))




