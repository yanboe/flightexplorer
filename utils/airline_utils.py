import pandas as pd

from models import Airline
from db import Session
from sqlalchemy import select
from sqlalchemy.orm import aliased


def get_airline_details(df):
    f1_airline = pd.Series(df["f1_airline_code"].dropna().unique())
    f2_airline = pd.Series(df["f2_airline_code"].dropna().unique())
    f3_airline = pd.Series(df["f3_airline_code"].dropna().unique())
    airlines = pd.concat([f1_airline, f2_airline, f3_airline]).tolist()

    session = Session()
    a = aliased(Airline)
    stmt = \
        select(a.airline_icao, a.airline_name).\
        where(
            a.airline_icao.in_(airlines)
        )
    airline_df = pd.read_sql(stmt, session.bind).set_index("airline_icao")

    return airline_df
