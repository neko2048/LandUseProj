import numpy as np
from matplotlib.pyplot import *
from matplotlib.colors import ListedColormap
import json
import netCDF4
import cartopy.crs as ccrs
from landUse import LandUseDataLoader


#/data/loach/Data/GEOG.TWlusdtm/modis_landuse_20class_5s/modis15s.regrid.79201-86400.79201-86400
if __name__ == "__main__":
    dataDirs = {
    "landUseInfo": "../data/MODIS_5s.json", 
    "colorMap": "../data/loachColor/modis20types.json", 
    "countyNumMap": "../data/MODIS_5s_countyNumMap.npy",
    }


    luDataLoaderLeft = LandUseDataLoader(anchorLon = 115 , anchorlat=23.5, dataDirs=dataDirs)
    luDataLoaderLeft.landUse = luDataLoaderLeft.loadData()
    luDataLoaderLeft.lon, luDataLoaderLeft.lat = luDataLoaderLeft.getLonLat()
    luDataLoaderRight = LandUseDataLoader(anchorLon = 121, anchorlat=23.5, dataDirs=dataDirs)
    luDataLoaderRight.landUse = luDataLoaderRight.loadData()
    luDataLoaderRight.lon, luDataLoaderRight.lat = luDataLoaderRight.getLonLat()
    cmap = ListedColormap([x[0] for x in luDataLoaderRight.colorMap.values()])
    fig, ax = subplots(figsize=(16, 10), subplot_kw={"projection": ccrs.PlateCarree()})
    ax.set_extent([107.5, 132.5, 17.5, 32.5])

    ax.pcolormesh(luDataLoaderLeft.lon, luDataLoaderLeft.lat, luDataLoaderLeft.landUse, 
                  vmin=np.min(list(map(int, luDataLoaderLeft.colorMap.keys())))-0.5, 
                  vmax=np.max(list(map(int, luDataLoaderLeft.colorMap.keys())))+0.5, 
                  cmap=cmap)
    LU = ax.pcolormesh(luDataLoaderRight.lon, luDataLoaderRight.lat, luDataLoaderRight.landUse, 
                  vmin=np.min(list(map(int, luDataLoaderLeft.colorMap.keys())))-0.5, 
                  vmax=np.max(list(map(int, luDataLoaderLeft.colorMap.keys())))+0.5, 
                  cmap=cmap)
    cmapTick = [x[1] for x in luDataLoaderRight.colorMap.values()]
    cb = colorbar(LU)
    cb.set_ticklabels(cmapTick)
    cb.ax.tick_params(labelsize=17)

    plot([110, 130, 130, 110, 110], [20, 20, 30, 30, 20], color="red", linewidth=5)
    ax.gridlines(draw_labels=False, alpha=0.75, 
                 xlocs=[110, 115, 120, 125, 130], 
                 ylocs=[20, 25, 30], color="grey")
    ax.set_xticks([110, 115, 120, 125, 130])
    ax.set_yticks([20, 25, 30])
    ax.set_xticklabels(["110°E", "115°E", "120°E", "125°E", "130°E"])
    ax.set_yticklabels(["20°N", "25°N", "30°N"])
    ax.coastlines(resolution="10m")
    ax.set_title(luDataLoaderLeft.landUseName,fontsize=17)
    savefig("landUseLargeReg.jpg", dpi=250)

