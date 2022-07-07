import pandas as pd
from itertools import islice


def get_map_lines(df_flights, df_airports):

    df_map_lines = pd.DataFrame()
    colors = [
        "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99",
        "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"
    ]
    i = 0

    for index, row in islice(df_flights.iterrows(), 10):
        color = colors[i]
        i += 1
        if row.stop_count == 0:
            flight = "{}–{}".format(
                df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                df_airports.loc[row.f1_airport_to, "airport_iata_code"]
            )
            # From 1
            lon = df_airports.loc[row.f1_airport_from, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_from, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_from, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 1
            lon = df_airports.loc[row.f1_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)
        elif row.stop_count == 1:
            flight = "{}–{}–{}".format(
                df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                df_airports.loc[row.f2_airport_to, "airport_iata_code"]
            )
            # From 1
            lon = df_airports.loc[row.f1_airport_from, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_from, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_from, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 1
            lon = df_airports.loc[row.f1_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 2
            lon = df_airports.loc[row.f2_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f2_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f2_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)
        elif row.stop_count == 2:
            flight = "{}–{}–{}–{}".format(
                df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                df_airports.loc[row.f2_airport_to, "airport_iata_code"],
                df_airports.loc[row.f3_airport_to, "airport_iata_code"]
            )
            # From 1
            lon = df_airports.loc[row.f1_airport_from, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_from, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_from, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 1
            lon = df_airports.loc[row.f1_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f1_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f1_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 2
            lon = df_airports.loc[row.f2_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f2_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f2_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)

            # To 3
            lon = df_airports.loc[row.f3_airport_to, "airport_longitude_deg"]
            lat = df_airports.loc[row.f3_airport_to, "airport_latitude_deg"]
            iata = df_airports.loc[row.f3_airport_to, "airport_iata_code"]
            df_map_lines = append_to_df(df_map_lines, flight, lon, lat, iata, color)
        else:
            continue

    return df_map_lines


def get_map_markers(df_map_lines, df_airports):

    iata_codes = df_map_lines["iata"].drop_duplicates().reset_index(drop=True)

    df_map_markers = pd.DataFrame(columns=["iata", "lon", "lat"])
    df_map_markers["iata"] = iata_codes
    df_map_markers = df_map_markers.set_index("iata")

    df_airports = df_airports.set_index("airport_iata_code")
    df_map_markers["lon"] = df_airports.loc[df_map_markers.index, "airport_longitude_deg"]
    df_map_markers["lat"] = df_airports.loc[df_map_markers.index, "airport_latitude_deg"]

    return df_map_markers


def append_to_df(df, flight, lon, lat, iata, color):
    df_dict = {
        "flight": flight,
        "lon": lon,
        "lat": lat,
        "iata": iata,
        "color": color
    }
    return pd.concat([df, pd.DataFrame.from_records([df_dict])], ignore_index=True)
