import pandas as pd

from models import Airport, Country, Region
from db import Session
from sqlalchemy import select
from sqlalchemy.orm import aliased


def get_airports_from(page):
    session = Session()

    a = aliased(Airport)
    b = aliased(Country)
    c = aliased(Region)
    airport_stmt = \
        select(
            a.airport_iata_code, a.airport_continent, b.country_name,
            c.region_name, a.airport_municipality, a.airport_name,
            a.airport_iso_region, a.airport_iso_country
        ).\
        join(b, a.airport_iso_country == b.country_code).\
        join(c, a.airport_iso_region == c.region_code).\
        where(
            a.airport_type.in_(["large_airport", "medium_airport"]),
            a.airport_scheduled_service == "yes"
        )
    airports = pd.read_sql(airport_stmt, session.bind)

    # Continents
    df_con = pd.DataFrame(columns=["label", "value", "group"])
    df_con["label"] = (airports["airport_continent"] + " (All airports)").drop_duplicates()
    df_con["value"] = ("con#" + airports["airport_continent"])
    df_con["group"] = "Continent"

    # Countries
    df_cou = pd.DataFrame(columns=["label", "value", "group"])
    df_cou["label"] = (airports["country_name"] + " (All airports)").drop_duplicates()
    df_cou["value"] = ("cou#" + airports["airport_iso_country"])
    df_cou["group"] = "Country"

    # Regions
    df_reg = pd.DataFrame(columns=["label", "value", "group"])
    df_reg["label"] = (
        airports["region_name"] +
        ", " +
        airports["country_name"] +
        " (All airports)"
    ).drop_duplicates()
    df_reg["value"] = ("reg#" + airports["airport_iso_region"])
    df_reg["group"] = "Region"

    # Municipalities
    df_mun = pd.DataFrame(columns=["label", "value", "group"])
    df_mun["label"] = (
        airports["airport_municipality"] +
        ", " +
        airports["region_name"] +
        ", " +
        airports["airport_iso_country"] +
        " (All airports)"
    ).drop_duplicates()
    df_mun["value"] = (
        "mun#" +
        airports["airport_iso_country"] +
        "#" +
        airports["airport_iso_region"] +
        "#" +
        airports["airport_municipality"]
    )
    df_mun["group"] = "Municipality"
    df_mun = df_mun.dropna()

    if page == "fl":
        df_air = pd.DataFrame(columns=["label", "value", "group"])
        df_air["label"] = (airports["airport_name"] + " (" + airports["airport_iata_code"] + ")").drop_duplicates()
        df_air["value"] = ("air#" + airports["airport_iata_code"])
        df_air["group"] = "Airport"
        df_air = df_air.dropna()
        df_from = pd.concat([df_con, df_cou, df_reg, df_mun, df_air])
    else:
        df_from = pd.concat([df_con, df_cou, df_reg, df_mun])

    df_from = df_from.sort_values(["group", "label"], ascending=[True, True]).reset_index(drop=True)
    return df_from.to_dict("records")


def get_airports_to():
    session = Session()

    a = aliased(Airport)
    airport_stmt = \
        select(a.airport_iata_code, a.airport_name).\
        where(
            a.airport_type.in_(["large_airport", "medium_airport"]),
            a.airport_scheduled_service == "yes"
        )
    airports = pd.read_sql(airport_stmt, session.bind)

    df_air = pd.DataFrame(columns=["label", "value"])
    df_air["label"] = (airports["airport_name"] + " (" + airports["airport_iata_code"] + ")").drop_duplicates()
    df_air["value"] = ("air#" + airports["airport_iata_code"])
    df_air = df_air.dropna()
    df_air = df_air.sort_values(["label"], ascending=[True]).reset_index(drop=True)
    return df_air.to_dict("records")


def get_airports_by_key(selected_value):
    session = Session()
    search_string = selected_value.split("#")
    search_level = search_string[0]
    search_value = search_string[1]

    a = aliased(Airport)

    if search_level == "con":
        stmt = \
            select(a.airport_ident).\
            where(
                a.airport_continent == search_value,
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )
    elif search_level == "cou":
        stmt = \
            select(a.airport_ident).\
            where(
                a.airport_iso_country == search_value,
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )
    elif search_level == "reg":
        stmt = \
            select(a.airport_ident).\
            where(
                a.airport_iso_region == search_value,
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )
    elif search_level == "mun":
        iso_region = search_string[2]
        municipality = search_string[3]
        stmt = \
            select(a.airport_ident).\
            where(
                a.airport_iso_country == search_value,
                a.airport_iso_region == iso_region,
                a.airport_municipality == municipality,
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )
    elif search_level == "air":
        stmt = \
            select(a.airport_ident).\
            where(
                a.airport_iata_code == search_value,
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )
    else:
        # Should never happen, but in the worst case mock an SQL statement
        stmt = \
            select(a.airport_ident). \
            where(
                a.airport_iata_code == "ZRH",
                a.airport_type.in_(["large_airport", "medium_airport"]),
                a.airport_scheduled_service == "yes"
            )

    airports = pd.read_sql(stmt, session.bind)
    airport_list = airports["airport_ident"].values.tolist()
    return airport_list


def get_airport_details_fl(df):
    f1_airport_from = pd.Series(df["f1_airport_from"].dropna().unique())
    f1_airport_to = pd.Series(df["f1_airport_to"].dropna().unique())
    f2_airport_to = pd.Series(df["f2_airport_to"].dropna().unique())
    f3_airport_to = pd.Series(df["f3_airport_to"].dropna().unique())
    airports = pd.concat([f1_airport_from, f1_airport_to, f2_airport_to, f3_airport_to]).tolist()

    session = Session()
    a = aliased(Airport)
    stmt = \
        select(a.airport_ident, a.airport_iata_code, a.airport_name, a.airport_latitude_deg, a.airport_longitude_deg).\
        where(
            a.airport_ident.in_(airports)
        )
    airport_df = pd.read_sql(stmt, session.bind).set_index("airport_ident")

    return airport_df


def get_airport_details_ap(df):
    airports = pd.Series(df["airport"]).tolist()

    session = Session()
    a = aliased(Airport)
    stmt = \
        select(a.airport_ident, a.airport_iata_code, a.airport_name). \
        where(
            a.airport_ident.in_(airports)
        )
    airport_df = pd.read_sql(stmt, session.bind).set_index("airport_ident")

    return airport_df
