import fiona
from rtree import index
from shapely.geometry import shape, Point, Polygon
import matplotlib.pyplot as plt
import geopandas as gpd


class CountyJudger(object):
    """
    docstring for CountyJudger
    ref: https://op8867555.github.io/posts/2017-09-16-python-getting-town-from-gps-coord.html
    """
    def __init__(self, shpDir):
        self.shpDir = shpDir
        self.taiwanCountryShape = fiona.open(self.shpDir)
        self.shapes = {}
        self.properties = {}
        self.collectData()

    def collectData(self):
        for f in self.taiwanCountryShape:
            town_id = int(f['properties']['TOWNCODE'])
            self.shapes[town_id] = shape(f['geometry'])
            self.properties[town_id] = f['properties']
        self.idx = index.Index()
        for town_id, town_shape in self.shapes.items():
            self.idx.insert(town_id, town_shape.bounds)

    def searchTownIdx(self, x, y):
        return next((town_id
                     for town_id in self.idx.intersection((x, y))
                     if self.shapes[town_id].contains(Point(x, y))), None)

    def searchCountyIdx(self, x, y):
        townIdx = self.searchTownIdx(x, y)
        if townIdx != None:
            return self.properties[townIdx]["COUNTYID"]
        return None

    def searchCountyNum(self, x, y):
        countyNumDict = {
            "A": 1, 
            "B": 2, 
            "C": 3, 
            "D": 4, 
            "E": 5, 
            "F": 6, 
            "G": 7, 
            "H": 8, 
            "I": 9, 
            "J": 10, 
            "K": 11, 
            "M": 12, 
            "N": 13, 
            "O": 14, 
            "P": 15, 
            "Q": 16, 
            "T": 17, 
            "U": 18, 
            "V": 19, 
            "W": 20, 
            "X": 21, 
            "Z": 22,
        }
        townIdx = self.searchTownIdx(x, y)
        if townIdx != None:
            return countyNumDict[self.properties[townIdx]["COUNTYID"]]
        return None

    def searchCountyName(self, x, y):
        countyMap = {
            "A": "Taipei City", 
            "B": "Taichung City", 
            "C": "Keelung City", 
            "D": "Tainan City", 
            "E": "Kaohsiung City", 
            "F": "New Taipei City", 
            "G": "Yilan County", 
            "H": "Taoyuan City", 
            "I": "Chiayi City", 
            "J": "Hsinchu County", 
            "K": "Miaoli County", 
            "M": "Nantou County", 
            "N": "Changhua County", 
            "O": "Hsinchu City", 
            "P": "Yunlin County", 
            "Q": "Chiayi County", 
            "T": "Pingtung County", 
            "U": "Hualien County", 
            "V": "Taitung County", 
            "W": "Kinmen County", 
            "X": "Penghu County", 
            "Z": "Lienchiang County"}
        countyIdx = self.searchCountyIdx(x, y)
        if countyIdx != None:
            return countyNumDict[self.properties[townIdx]["COUNTYID"]]
        return None

if __name__ == "__main__":

    shpDir = '../taiwanCountyShape/TOWN_MOI_1100415.shp'
    countyJudger = CountyJudger(shpDir)
    countyName = countyJudger.searchCountyNum(y=25.0263075,x=121.543846)
    print(countyName)













