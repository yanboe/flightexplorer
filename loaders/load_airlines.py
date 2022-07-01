import csv
from models import Airline
from db import Session


def change_to_null(x):
    if x == "":
        return None
    else:
        return x


session = Session()

with open("../../data/airline_baseline.csv", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header

    count_insert = 0

    for row in reader:
        airline = Airline(
            airline_name=change_to_null(row[1]),
            airline_iata=change_to_null(row[2]),
            airline_icao=change_to_null(row[3]),
            airline_callsign=change_to_null(row[4]),
            airline_country=change_to_null(row[5]),
            airline_comments=change_to_null(row[6])
        )
        session.add(airline)
        count_insert += 1

    print("Committing " + str(count_insert) + " records...")
    session.commit()
    print("Done!\n")
