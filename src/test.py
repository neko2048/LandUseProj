import json

with open("../data/USGS_30s.json") as jsonFile:
    data = json.load(jsonFile)
    print(data)