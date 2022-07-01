import csv
from models import Flight
from db import Session
import os


airport_fix = {"KS67", "LSMF", "LTFG", "SCTJ", "YADY", "YPEC", "YSCH"}


def change_to_null(x):
    if x == "":
        return None
    else:
        return x


def check_airport(airport):
    if airport in airport_fix:
        if airport == "KS67":
            return "KMAN"
        elif airport == "LSMF":
            return "LSZM"
        elif airport == "LTFG":
            return "LTGP"
        elif airport == "SCTJ":
            return "SBAE"
        elif airport == "YADY":
            return "YADI"
        elif airport == "YPEC":
            return "YLMQ"
        elif airport == "YSCH":
            return "YCFS"
        else:
            return airport
    else:
        return airport


# Create list of valid airports
airport_baseline = set()
with open("../../data/airport_baseline.csv") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header
    for row in reader:
        airport_baseline.add(row[0])


# Create list of valid airlines
airline_baseline = set()
with open("../../data/airline_baseline.csv") as file:
    reader = csv.reader(file, delimiter=",")
    next(reader)  # skip header
    for row in reader:
        airline_baseline.add(row[3])

# Set directory and initialize statistics
directory = "../../data/flights/"
count_insert_total = 0
count_skip_total = 0

# Iterate over all files and import relevant flights into table
session = Session()
for filename in os.listdir(directory):
    print("------------------------------\nProcessing file:", filename)

    with open(os.path.join(directory, filename)) as file:
        reader = csv.reader(file, delimiter=",")
        next(reader)  # skip header

        count_insert = 0
        count_skip = 0

        for row in reader:

            # Some flights have the wrong airports assigned (mainly due to renaming of airports), so
            # we have to change this first before validating against the already cleaned list of airports
            row[5] = check_airport(row[5])
            row[6] = check_airport(row[6])

            # Check if airline, origin and destination are valid
            if row[0][0:3] in airline_baseline and row[5] in airport_baseline and row[6] in airport_baseline:
                flight = Flight(
                    callsign=row[0],
                    number=row[1],
                    icao24=row[2],
                    registration=row[3],
                    typecode=row[4],
                    origin=row[5],
                    destination=row[6],
                    firstseen=row[7],
                    lastseen=row[8],
                    day=row[9],
                    latitude_1=change_to_null(row[10]),
                    longitude_1=change_to_null(row[11]),
                    altitude_1=change_to_null(row[12]),
                    latitude_2=change_to_null(row[13]),
                    longitude_2=change_to_null(row[14]),
                    altitude_2=change_to_null(row[15])
                )
                session.add(flight)
                count_insert += 1
                if count_insert % 100000 == 0:
                    print(count_insert)
            else:
                count_skip += 1

    print("Committing " + str(count_insert) + " records...")
    session.commit()
    print("Done!\n")
    count_insert_total = count_insert_total + count_insert
    count_skip_total = count_skip_total + count_skip

print("\nSummary\n------------------------------")
print("Rows inserted:\t", count_insert_total)
print("Rows skipped:\t", count_skip_total)
