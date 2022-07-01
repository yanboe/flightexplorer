import csv
from models import Region
from db import Session


def change_to_null(x):
    if x == "":
        return None
    else:
        return x


session = Session()

# Import all regions
with open("../../data/regions.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header

    count_insert = 0

    for row in reader:
        region = Region(
            region_code=change_to_null(row[1]),
            region_local_code=change_to_null(row[2]),
            region_name=change_to_null(row[3]),
            region_continent=change_to_null(row[4]),
            region_iso_country=change_to_null(row[5]),
            region_wiki=change_to_null(row[6]),
            region_keywords=change_to_null(row[7])
        )
        session.add(region)
        count_insert += 1

    print("Committing " + str(count_insert) + " records...")
    session.commit()
    print("Done!\n")
