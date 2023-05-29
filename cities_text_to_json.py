import json

filename = "cities1000.txt"  # Replace with the actual file name/path

data = []

with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line:
            geonameid, name, asciiname, alternatenames, latitude, longitude, feature_class, feature_code, country_code, cc2, admin1_code, admin2_code, admin3_code, admin4_code, population, elevation, dem, timezone, modification_date = line.split(
                "\t")

            record = {
                "geonameid": int(geonameid),
                "name": name,
                "asciiname": asciiname,
                "alternatenames": [name.encode("unicode_escape").decode("utf-8") for name in alternatenames.split(",")],
                "latitude": float(latitude),
                "longitude": float(longitude),
                "feature_class": feature_class,
                "feature_code": feature_code,
                "country_code": country_code,
                "cc2": cc2.split(","),
                "admin1_code": admin1_code,
                "admin2_code": admin2_code,
                "admin3_code": admin3_code,
                "admin4_code": admin4_code,
                "population": int(population) if population else None,
                "elevation": int(elevation) if elevation else None,
                "dem": dem,
                "timezone": timezone,
                "modification_date": modification_date
            }

            data.append(record)

# Convert the list of dictionaries to JSON
json_data = json.dumps(data, indent=4)

# Print or save the JSON data
print(json_data)
