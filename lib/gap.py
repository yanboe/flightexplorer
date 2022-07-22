from sqlalchemy import select, func, distinct
from sqlalchemy.orm import aliased
import pandas as pd
from db import Session
from models import Flight


def get_gap(origin, start, end):
    a = aliased(Flight)
    session = Session()

    # Get flights
    stmt = \
        select(
            a.origin, func.count(a.origin)
        ).\
        where(
            a.firstseen.between(start, end),
            a.origin.in_(origin)
        ).\
        group_by(
            a.origin
        )
    gap_flights = pd.read_sql(stmt, session.bind).\
        rename(columns={"origin": "f1_airport_from", "count_1": "kpi1"}).\
        set_index("f1_airport_from")

    # Get airlines
    stmt = \
        select(
            a.origin, func.substr(a.callsign, 1, 3), func.count(a.origin)
        ).\
        where(
            a.firstseen.between(start, end),
            a.origin.in_(origin)
        ).\
        group_by(
            a.origin, func.substr(a.callsign, 1, 3)
        )
    gap_air_df = pd.read_sql(stmt, session.bind)
    gap_air_series = gap_air_df["origin"].value_counts()
    gap_airlines = gap_air_series.to_frame().\
        reset_index().\
        rename(columns={"index": "f1_airport_from", "origin": "kpi2"}).\
        set_index("f1_airport_from")

    # Get destinations
    stmt = \
        select(
            a.origin, a.destination, func.count(a.origin)
        ).\
        where(
            a.firstseen.between(start, end),
            a.origin.in_(origin)
        ).\
        group_by(
            a.origin, a.destination
        )
    gap_dest_df = pd.read_sql(stmt, session.bind)
    gap_dest_series = gap_dest_df["origin"].value_counts()
    gap_destinations = gap_dest_series.to_frame().\
        reset_index().\
        rename(columns={"index": "f1_airport_from", "origin": "kpi3"}).\
        set_index("f1_airport_from")

    df_gap = pd.concat([gap_flights, gap_airlines, gap_destinations], axis=1)

    return df_gap
