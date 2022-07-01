import csv
from models import Country
from db import Session


def change_to_null(x):
    if x == "":
        return None
    else:
        return x


session = Session()

# Import all countries
with open("../../data/countries.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header

    count_insert = 0

    for row in reader:
        country = Country(
            country_code=change_to_null(row[1]),
            country_name=change_to_null(row[2]),
            country_continent=change_to_null(row[3]),
            country_wiki=change_to_null(row[4]),
            country_keywords=change_to_null(row[5])
        )
        session.add(country)
        count_insert += 1

    print("Committing " + str(count_insert) + " records...")
    session.commit()
    print("Done!\n")
