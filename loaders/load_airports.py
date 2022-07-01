import csv
from db import Session
from models import Airport


def change_to_null(x):
    if x == "":
        return None
    else:
        return x


session = Session()

# Create list of valid airports
airport_baseline = set()
with open("../data/airport_baseline.csv") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header
    for row in reader:
        airport_baseline.add(row[0])


# Import all valid airports
with open("../data/airport_consolidated.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header

    count_insert = 0

    for row in reader:
        if row[1] in airport_baseline:
            airport = Airport(
                airport_ident=change_to_null(row[1]),
                airport_type=change_to_null(row[2]),
                airport_name=change_to_null(row[3]),
                airport_latitude_deg=change_to_null(row[4]),
                airport_longitude_deg=change_to_null(row[5]),
                airport_elevation_ft=change_to_null(row[6]),
                airport_continent=change_to_null(row[7]),
                airport_iso_country=change_to_null(row[8]),
                airport_iso_region=change_to_null(row[9]),
                airport_municipality=change_to_null(row[10]),
                airport_scheduled_service=change_to_null(row[11]),
                airport_gps_code=change_to_null(row[12]),
                airport_iata_code=change_to_null(row[13]),
                airport_local_code=change_to_null(row[14]),
                airport_home_link=change_to_null(row[15]),
                airport_wikipedia_link=change_to_null(row[16]),
                airport_keywords=change_to_null(row[17])
            )
            session.add(airport)
            count_insert += 1

    print("Committing " + str(count_insert) + " records...")
    session.commit()
    print("Done!\n")
