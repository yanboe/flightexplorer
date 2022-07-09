from sqlalchemy import select, func, Interval
from sqlalchemy.sql.functions import concat
from sqlalchemy.orm import aliased
import pandas as pd
from db import Session
from models import Flight
import numpy as np
import warnings
warnings.simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


"""
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
"""


def get_sql(origin, destination, start, end, stop_duration):
    """
    Prepare the SQL statements for the flights based on the input parameters
    """
    a = aliased(Flight)
    b = aliased(Flight)
    c = aliased(Flight)

    stmt0stop = \
        select(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen
        ).\
        where(
          a.firstseen.between(start, end),
          a.destination.in_(destination),
          a.origin.in_(origin)
        ).\
        order_by(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen
        )

    stmt1stop = \
        select(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen,
          b.callsign, b.origin, b.destination, b.firstseen, b.lastseen
        ).\
        join(b, a.destination == b.origin).\
        where(
          a.firstseen.between(start, end),
          b.firstseen.between(
            start,
            start + func.cast(concat(1, ' DAYS'), Interval)
          ),
          b.firstseen.between(
            a.lastseen + func.cast(concat(1, ' HOURS'), Interval),
            a.lastseen + func.cast(concat(stop_duration, ' HOURS'), Interval)
          ),
          b.destination.in_(destination),
          a.origin.in_(origin)
        ).\
        order_by(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen,
          b.callsign, b.origin, b.destination, b.firstseen, b.lastseen
        )

    stmt2stop = \
        select(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen,
          b.callsign, b.origin, b.destination, b.firstseen, b.lastseen,
          c.callsign, c.origin, c.destination, c.firstseen, c.lastseen
        ).\
        join(b, a.destination == b.origin).\
        join(c, b.destination == c.origin).\
        where(
          a.firstseen.between(start, end),
          b.firstseen.between(
            start,
            start + func.cast(concat(1, ' DAYS'), Interval)
          ),
          c.firstseen.between(
            start,
            start + func.cast(concat(2, ' DAYS'), Interval)
          ),
          b.firstseen.between(
            a.lastseen + func.cast(concat(1, ' HOURS'), Interval),
            a.lastseen + func.cast(concat(stop_duration, ' HOURS'), Interval)
          ),
          c.firstseen.between(
            b.lastseen + func.cast(concat(1, ' HOURS'), Interval),
            b.lastseen + func.cast(concat(stop_duration, ' HOURS'), Interval)
          ),
          c.destination.in_(destination),
          a.origin.in_(origin)
        ).\
        order_by(
          a.callsign, a.origin, a.destination, a.firstseen, a.lastseen,
          b.callsign, b.origin, b.destination, b.firstseen, b.lastseen,
          c.callsign, c.origin, c.destination, c.firstseen, c.lastseen
        )

    return stmt0stop, stmt1stop, stmt2stop


def get_timedelta(tsd_from, tsd_to, convert=False):
    """
    Get the timedelta between tsd_to and tsd_from. Convert to "x hr y min" if needed
    """
    duration = (tsd_to - tsd_from).dt.total_seconds()
    if convert:
        duration = convert_duration(duration)
    return duration


def convert_duration(duration):
    """
    Convert duration in seconds to "x hr y min"
    """
    irrelevant_seconds = duration % 60
    duration = duration - irrelevant_seconds
    hrs, mins = divmod(duration / 60, 60)
    hrs = hrs.astype("Int64").astype(str)
    mins = mins.astype("Int64").astype(str)

    dur_formatted = hrs + " hr " + mins + " min"
    dur_formatted = dur_formatted.replace(r"\A0 hr ", "", regex=True)
    dur_formatted = dur_formatted.replace(r"<NA> hr <NA> min", np.nan, regex=True)
    return dur_formatted


def get_airline_code(df, column, none_value):
    """
    Return airline code
    """
    col_exists = check_if_exists(df, column, none_value)
    if col_exists.isnull().values.all():
        return np.nan
    else:
        return col_exists.str[:3]


def get_airline_name(callsign):
    """
    Get the airline name from the callsign
    """
    if callsign.isnull().values.any():
        return np.nan
    else:
        airline_name = callsign + " Airline"
        return airline_name


def check_if_exists(df, column, none_value):
    """
    Check if column exists in df; if yes, return the column as a series, if not, return NaN/NaT
    """
    if column in df.columns:
        if none_value == "NaT":
            return pd.to_datetime(df[column])
        else:
            return df[column]
    else:
        if none_value == "NaT":
            return pd.Series(pd.to_datetime(np.nan))
        else:
            return pd.Series(np.nan)


def convert_time(column):
    """
    Convert datetime to HH:MM format
    """
    if column.isnull().values.all():
        return column
    else:
        column = pd.to_datetime(column).dt.strftime("%H:%M")
        return column


def get_flights(origin, destination, start, end, stop_duration, max_stops):
    # Get the flights and combine them into df_all
    stmt0stop, stmt1stop, stmt2stop = get_sql(origin, destination, start, end, stop_duration)
    session = Session()

    if max_stops == 0:
        df_0stop = pd.read_sql(stmt0stop, session.bind)
        df_all = df_0stop
    elif max_stops == 1:
        df_0stop = pd.read_sql(stmt0stop, session.bind)
        df_1stop = pd.read_sql(stmt1stop, session.bind)
        df_all = pd.concat([df_0stop, df_1stop])
    else:
        df_0stop = pd.read_sql(stmt0stop, session.bind)
        df_1stop = pd.read_sql(stmt1stop, session.bind)
        df_2stop = pd.read_sql(stmt2stop, session.bind)
        df_all = pd.concat([df_0stop, df_1stop, df_2stop])

    df_all = df_all.reset_index(drop=True)

    df_formatted_columns = [
        "f1_airline_code", "f1_airline_name", "f1_airport_from", "f1_airport_to",
        "f1_airport_from_long", "f1_airport_to_long",
        "f1_time_from", "f1_time_from_str", "f1_time_to", "f1_time_to_str",
        "f1_duration", "f1_duration_s",

        "f2_airline_code", "f2_airline_name", "f2_airport_from", "f2_airport_to",
        "f2_airport_from_long", "f2_airport_to_long",
        "f2_time_from", "f2_time_from_str", "f2_time_to", "f2_time_to_str",
        "f2_duration", "f2_duration_s",

        "f3_airline_code", "f3_airline_name", "f3_airport_from", "f3_airport_to",
        "f3_airport_from_long", "f3_airport_to_long",
        "f3_time_from", "f3_time_from_str", "f3_time_to", "f3_time_to_str",
        "f3_duration", "f3_duration_s",

        "total_duration", "total_duration_s", "stop_count", "stop_count_str", "arr_time",
        "layover_duration_1", "layover_duration_1_s", "layover_duration_2", "layover_duration_2_s"
    ]

    df_formatted = pd.DataFrame(columns=df_formatted_columns)

    # 1st flight
    if df_all.empty:
        df_final = df_all
        return df_final
    else:
        df_formatted["f1_airline_code"] = df_all["callsign"].str[:3]
        df_formatted["f1_airline_name"] = get_airline_name(df_all["callsign"].str[:3])
        df_formatted["f1_airport_from"] = df_all["origin"]
        df_formatted["f1_airport_to"] = df_all["destination"]
        df_formatted["f1_airport_from_long"] = df_all["origin"]
        df_formatted["f1_airport_to_long"] = df_all["destination"]
        df_formatted["f1_time_from"] = df_all["firstseen"]
        df_formatted["f1_time_from_str"] = convert_time(df_formatted["f1_time_from"])
        df_formatted["f1_time_to"] = df_all["lastseen"]
        df_formatted["f1_time_to_str"] = convert_time(df_formatted["f1_time_to"])
        df_formatted["f1_duration"] = get_timedelta(df_all["firstseen"], df_all["lastseen"], convert=True)
        df_formatted["f1_duration_s"] = get_timedelta(df_all["firstseen"], df_all["lastseen"], convert=False)

    # 2nd flight
    df_formatted["f2_airline_code"] = get_airline_code(df_all, "callsign_1", "NaN")
    df_formatted["f2_airline_name"] = get_airline_name(df_formatted["f2_airline_code"])
    df_formatted["f2_airport_from"] = check_if_exists(df_all, "origin_1", "NaN")
    df_formatted["f2_airport_to"] = check_if_exists(df_all, "destination_1", "NaN")
    df_formatted["f2_airport_from_long"] = check_if_exists(df_all, "origin_1", "NaN")
    df_formatted["f2_airport_to_long"] = check_if_exists(df_all, "destination_1", "NaN")
    df_formatted["f2_time_from"] = check_if_exists(df_all, "firstseen_1", "NaT")
    df_formatted["f2_time_from_str"] = convert_time(df_formatted["f2_time_from"])
    df_formatted["f2_time_to"] = check_if_exists(df_all, "lastseen_1", "NaT")
    df_formatted["f2_time_to_str"] = convert_time(df_formatted["f2_time_to"])
    df_formatted["f2_duration"] = get_timedelta(
      check_if_exists(df_all, "firstseen_1", "NaT"),
      check_if_exists(df_all, "lastseen_1", "NaT"),
      convert=True
    )
    df_formatted["f2_duration_s"] = get_timedelta(
      check_if_exists(df_all, "firstseen_1", "NaT"),
      check_if_exists(df_all, "lastseen_1", "NaT"),
      convert=False
    )

    # 3rd flight
    df_formatted["f3_airline_code"] = get_airline_code(df_all, "callsign_2", "NaN")
    df_formatted["f3_airline_name"] = get_airline_name(df_formatted["f3_airline_code"])
    df_formatted["f3_airport_from"] = check_if_exists(df_all, "origin_2", "NaN")
    df_formatted["f3_airport_to"] = check_if_exists(df_all, "destination_2", "NaN")
    df_formatted["f3_airport_from_long"] = check_if_exists(df_all, "origin_2", "NaN")
    df_formatted["f3_airport_to_long"] = check_if_exists(df_all, "destination_2", "NaN")
    df_formatted["f3_time_from"] = check_if_exists(df_all, "firstseen_2", "NaT")
    df_formatted["f3_time_from_str"] = convert_time(df_formatted["f3_time_from"])
    df_formatted["f3_time_to"] = check_if_exists(df_all, "lastseen_2", "NaT")
    df_formatted["f3_time_to_str"] = convert_time(df_formatted["f3_time_to"])
    df_formatted["f3_duration"] = get_timedelta(
      check_if_exists(df_all, "firstseen_2", "NaT"),
      check_if_exists(df_all, "lastseen_2", "NaT"),
      convert=True
    )
    df_formatted["f3_duration_s"] = get_timedelta(
      check_if_exists(df_all, "firstseen_2", "NaT"),
      check_if_exists(df_all, "lastseen_2", "NaT"),
      convert=False
    )

    # Duration if flight is nonstop
    td_0stop = get_timedelta(
        df_formatted["f1_time_from"],
        df_formatted["f1_time_to"],
        convert=False
    ).reset_index(drop=True)

    # Duration if flight has 1 stop
    if df_formatted["f2_time_to"].isnull().values.all():
        td_1stop = np.nan
    else:
        td_1stop = get_timedelta(
            df_formatted["f1_time_from"],
            df_formatted["f2_time_to"],
            convert=False
        ).reset_index(drop=True)

    # Duration if flight has 2 stops
    if df_formatted["f3_time_to"].isnull().values.all():
        td_2stop = np.nan
    else:
        td_2stop = get_timedelta(
            df_formatted["f1_time_from"],
            df_formatted["f3_time_to"],
            convert=False
        ).reset_index(drop=True)

    # Move values to dataframe to find max value
    df_td = pd.DataFrame()
    df_td["0stop"] = td_0stop
    df_td["1stop"] = td_1stop
    df_td["2stop"] = td_2stop

    # Set max value to df_formatted
    df_formatted["total_duration_s"] = df_td.max(axis=1)
    df_formatted["total_duration"] = convert_duration(df_formatted["total_duration_s"])

    # Layover Duration 1
    if df_formatted["f2_time_from"].isnull().values.all():
        ld_1stop = np.nan
    else:
        ld_1stop = get_timedelta(
            df_formatted["f1_time_to"],
            df_formatted["f2_time_from"],
            convert=False
        ).reset_index(drop=True)

    # Layover Duration 2
    if df_formatted["f2_time_to"].isnull().values.all():
        ld_2stop = np.nan
    elif df_formatted["f3_time_from"].isnull().values.all():
        ld_2stop = np.nan
    else:
        ld_2stop = get_timedelta(
            df_formatted["f2_time_to"],
            df_formatted["f3_time_from"],
            convert=False
        ).reset_index(drop=True)

    # Add Layover Duration to df_formatted
    df_formatted["layover_duration_1_s"] = ld_1stop
    df_formatted["layover_duration_1"] = convert_duration(df_formatted["layover_duration_1_s"])
    df_formatted["layover_duration_2_s"] = ld_2stop
    df_formatted["layover_duration_2"] = convert_duration(df_formatted["layover_duration_2_s"])

    # Add Stop Count to df_formatted
    cond = [df_formatted["layover_duration_1_s"].isnull(), df_formatted["layover_duration_2_s"].isnull()]
    out = ["Nonstop", "1 stop"]
    stop_count_str = np.select(cond, out, "2 stops")
    df_formatted["stop_count_str"] = stop_count_str

    cond = [df_formatted["layover_duration_1_s"].isnull(), df_formatted["layover_duration_2_s"].isnull()]
    out = [0, 1]
    stop_count = np.select(cond, out, 2)
    df_formatted["stop_count"] = stop_count

    # Add arrival time
    cond = [df_formatted["stop_count"] == 2,
            df_formatted["stop_count"] == 1,
            df_formatted["stop_count"] == 0]
    out = [df_formatted["f3_time_to"], df_formatted["f2_time_to"], df_formatted["f1_time_to"]]
    arr_time = np.select(cond, out)
    df_formatted["arr_time"] = arr_time

    df_sorted = df_formatted.sort_values(
        ["f1_airport_from", "f2_airport_from", "f3_airport_from", "f3_airport_to", "total_duration_s"],
        ascending=[True, True, True, True, True]
    )

    df_final = df_sorted.drop_duplicates(
        subset=["f1_airport_from", "f2_airport_from", "f3_airport_from", "f3_airport_to"],
        keep="first"
    )

    return df_final
