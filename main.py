import json
from shapely.geometry import Polygon

if __name__ == "__main__":
    inputfilepath = "feinkart_mitte_nutzung.geojson"#

    features = []
    with open(inputfilepath) as inputfile:
        features = json.load(inputfile)["features"]

    areasums = {}
    it = 0

    for feature in features:
        nutzung = feature["properties"]["nutzung"]

        if feature["geometry"]["type"] == "MultiPolygon":
            for poly in feature["geometry"]["coordinates"][0]:
                print(len(poly))
                if(len(poly) <= 2):
                    continue
                geom = Polygon(poly)
                area = geom.area
                # print(area)

                if not nutzung in areasums:
                    areasums[nutzung] = area
                else:
                    areasums[nutzung] = areasums[nutzung] + area

            print("feature",str(it),"of",len(features))
            it += 1

    print(areasums)

    sumsum = 0
    area_percent = {}

    nutzung_ofinterest = ["Parkplatz","Fahrbahn","Ãœberfahrt","Feldweg","Radweg","Geh- und Radweg","FuÃŸgÃ¤ngerzone","Fahrbahn mit Schutzstreifen","Gehweg"]

    for key in areasums:
        if key in nutzung_ofinterest:
            sumsum += areasums[key]
    
    output_path = "out.csv"
    with open(output_path, "w") as outfile:
        for key in areasums:
            outfile.write(str(key))
            outfile.write(",")
            outfile.write(str(areasums[key]))
            if key in nutzung_ofinterest:
                outfile.write(",")
                percent = areasums[key] / sumsum
                outfile.write(str(percent))
            outfile.write("\n")