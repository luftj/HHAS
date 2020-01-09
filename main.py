import json
from shapely.geometry import Polygon

if __name__ == "__main__":
    district = "eims"

    inputfilepath = "feinkart_"+district+"_nutzung.geojson"#

    features = []
    with open(inputfilepath) as inputfile:
        features = json.load(inputfile)["features"]

    areasums = {}
    it = 0

    for feature in features:
        nutzung = feature["properties"]["nutzung"]

        if feature["geometry"]["type"] == "MultiPolygon":
            if len(feature["geometry"]["coordinates"]) == 0:
                continue
            for poly in feature["geometry"]["coordinates"][0]:
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

    interest_sum = 0
    total_sum = 0
    area_percent = {}

    nutzung_ofinterest = ["Parkplatz","Fahrbahn","Ãœberfahrt","Feldweg","Radweg","Geh- und Radweg","FuÃŸgÃ¤ngerzone","Fahrbahn mit Schutzstreifen","Gehweg","Radfahrstreifen","Bussonderstreifen"]

    for key in areasums:
        if key in nutzung_ofinterest:
            interest_sum += areasums[key]
        total_sum += areasums[key]
    
    output_path = "out_"+district+".csv"
    with open(output_path, "w") as outfile:
        for key in areasums:
            outfile.write(str(key))
            outfile.write(",")
            outfile.write(str(areasums[key]))
            if key in nutzung_ofinterest:
                outfile.write(",")
                percent = areasums[key] / interest_sum
                outfile.write(str(percent))
            outfile.write("\n")
        outfile.write("verkehr,")
        outfile.write(str(interest_sum))
        outfile.write("\n")
        outfile.write("gesamt,")
        outfile.write(str(total_sum))
        outfile.write("\n")