import json
from shapely.geometry import Polygon


def sum_up_areas(feature, areasums):
    nutzung = feature["properties"]["nutzung"]

    if feature["geometry"]["type"] == "MultiPolygon":
        try:
            for poly in feature["geometry"]["coordinates"][0]:
                print(len(poly))
                if (len(poly) <= 2):
                    continue
                geom = Polygon(poly)
                area = geom.area
                # print(area)

                if not nutzung in areasums:
                    areasums[nutzung] = area
                else:
                    areasums[nutzung] = areasums[nutzung] + area
        except:
            print(feature)

        return areasums

# TODO add Mischfläche as dead space?

car_lane_features = []
car_parking_features = []
bike_lane_features = []
pedestrian_lane_features = []
pedestrian_area_features = []
bike_cars_shared_features = []
bike_pedestrians_shared_features = []
dead_space_features = []

feature_collections_per_type = {
    "car_lanes": car_lane_features,
    "car_parking": car_parking_features,
    "bike_infrastructure": bike_lane_features,
    "pedestrian_lane": pedestrian_lane_features,
    "pedestrian_area": pedestrian_area_features,
    "bike_cars": bike_cars_shared_features,
    "bike_pedestrians": bike_pedestrians_shared_features,
    "dead_space": dead_space_features
}


def get_color_for_land_use(land_use):
    land_use_colors = {
        "Parkplatz": "#8A0808",
        "Fahrbahn": "#FF0040",
        "Überfahrt": "#B40431",
        "Feldweg": "#2A0A12",
        "Radweg": "#00FFFF",
        "Geh- und Radweg": "#00BFFF",
        "Fußgängerzone": "#0B0B3B",
        "Fahrbahn mit Schutzstreifen": "#D7DF01",
        "Gehweg": "#0101DF",
        "Mischfläche": "#848484"
    }

    return land_use_colors[land_use]


def export_to_specific_feature_collection(feat):
    land_use = feat["properties"]["nutzung"]
    infrastructure_type = get_infrastructure_type(land_use)

    if infrastructure_type is not None:
        # set color property for visualization
        feat["properties"]["color"] = get_color_for_land_use(land_use)

        # append feature to type specific feature collection
        feature_collections_per_type[infrastructure_type].append(feat)


def save_geojson_per_infrastructure_type():
    for feature_coll in feature_collections_per_type:
        geojson = {
            "type": "FeatureCollection",
            "name": feature_coll,
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": feature_collections_per_type[feature_coll]
        }

        print("saving " + feature_coll + " to file")
        with open(feature_coll + ".geojson", "w") as f:
            json.dump(geojson, f)


def get_infrastructure_type(use):
    infrastructure_types = {
        "car_lanes": ["Fahrbahn", "Überfahrt", "Feldweg"],
        "car_parking": ["Parkplatz"],
        "dead_space": ["Mischfläche"],
        "bike_infrastructure": ["Radweg"],
        "pedestrian_lane": ["Gehweg"],
        "pedestrian_area": ["Fußgängerzone"],
        "bike_cars": ["Fahrbahn mit Schutzstreifen"],
        "bike_pedestrians": ["Geh- und Radweg"]
    }

    for i_type in infrastructure_types:
        if use in infrastructure_types[i_type]:
            return i_type

    return None


if __name__ == "__main__":
    inputfilepath = "feinkartierung_mitte.geojson"  #

    land_uses = []

    features = []
    with open(inputfilepath) as inputfile:
        features = json.load(inputfile)["features"]

    areasums = {}
    areasums_by_type = {}
    it = 0

    for feature in features:
        # export to feature specific json
        export_to_specific_feature_collection(feature)

        # sum up areas
        areasums = sum_up_areas(feature, areasums)

        print("feature", str(it), "of", len(features))
        it += 1

    print(land_uses)
    print(areasums)
    save_geojson_per_infrastructure_type()

    sumsum = 0

    nutzung_ofinterest = ["Parkplatz", "Fahrbahn", "Überfahrt", "Feldweg", "Radweg", "Geh- und Radweg", "Fußgängerzone",
                          "Fahrbahn mit Schutzstreifen", "Gehweg", "Mischfläche"]

    for key in areasums:
        if get_infrastructure_type(key) is not None:
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
