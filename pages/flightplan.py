import dash
import pytz
import dash_mantine_components as dmc
import pandas as pd

from dash import html, callback, Input, Output
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import aliased
from itertools import islice

from lib.flights import get_flights
from models import Airport, Country, Region
from db import Session


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


# sort by dropdown outside of callback to avoid callback exceptions
sort_select = dmc.Select(
    data=[
        {"value": "dep", "label": "Departure Time"},
        {"value": "arr", "label": "Arrival Time"},
        {"value": "dur", "label": "Duration"},
        {"value": "lay", "label": "Layovers"},
    ],
    radius="sm",
    size="sm",
    label="Sort by",
    value="dur",
    icon=[DashIconify(icon="clarity:sort-by-line", width=25)],
    style={"width": 180},
    id="sort_by"
)

layout = dmc.LoadingOverlay(
    [
        html.Div(id="page-content"),
        # hidden sort by dropdown
        html.Div(children=sort_select, style={"display": "none"})
    ],
)

dash.register_page(
    __name__,
    path="/flightplan/",
    name="Flight Plan",
    title="Flight Plan",
    layout=layout
)


@callback(
    Output("page-content", "children"),
    Output("sort_by", "value"),
    Input("airport_from", "value"),
    Input("airport_to", "value"),
    Input("datepicker", "value"),
    Input("dep_time", "value"),
    Input("max_stops", "value"),
    Input("flight_duration", "value"),
    Input("layover_duration", "value"),
    Input("sort_by", "value"),
    prevent_initial_call=True
)
def get_flightplan(airport_from, airport_to, flight_date, dep_time,
                   max_stops, flight_duration, layover_duration, sort_by):
    print(airport_from)
    print(airport_to)
    print(flight_date)
    print(dep_time)
    print(max_stops)
    print(flight_duration)
    print(layover_duration)
    print(sort_by)

    if (airport_from is None or airport_to is None or flight_date is None or
        flight_duration is None or layover_duration is None or sort_by is None):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # TODO: Validate/pass origin
    origin_value = airport_from.split("#")
    print(origin_value)
    origin = ['EGGW', 'EGKK', 'EGLL', 'EGSS']

    # TODO: Validate/pass destination
    destination = 'LSZH'

    # Convert flight_date to timezone aware
    date_no_tz = datetime.strptime(flight_date, "%Y-%m-%d")
    date_with_tz = pytz.utc.localize(date_no_tz)

    # Add departure time from/to depending on selection
    if dep_time is None:
        delta_from = timedelta(hours=00)
        delta_to = timedelta(hours=23, minutes=59)
    elif "night" in dep_time:
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=5, minutes=59)
    elif "morning" in dep_time:
        delta_from = timedelta(hours=6)
        delta_to = timedelta(hours=11, minutes=59)
    elif "afternoon" in dep_time:
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59)
    elif "evening" in dep_time:
        delta_from = timedelta(hours=18)
        delta_to = timedelta(hours=23, minutes=59)
    elif "anytime" in dep_time:
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=23, minutes=59)
    else:
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59)

    # earliest_time = flight_date + delta_from
    earliest_time = date_with_tz + delta_from

    # latest_time = flight_date + delta_to
    latest_time = date_with_tz + delta_to

    # Validate max stop count
    if max_stops is None:
        stop_cnt = 2
    elif "0" in max_stops:
        stop_cnt = 0
    elif "1" in max_stops:
        stop_cnt = 1
    else:
        stop_cnt = 2

    # get flights
    df_final = get_flights(origin, destination, earliest_time, latest_time, layover_duration, stop_cnt)

    # drop flights that take longer than flight_duration
    flight_duration_s = flight_duration * 3600
    df_final.drop(df_final[df_final.total_duration_s > flight_duration_s].index, inplace=True)

    # sort df_final according to input value
    if sort_by == "dur":
        df_final = df_final.sort_values(["total_duration_s"], ascending=[True])
    elif sort_by == "dep":
        df_final = df_final.sort_values(["f1_time_from", "total_duration_s"], ascending=[True, True])
    elif sort_by == "arr":
        df_final = df_final.sort_values(["arr_time", "total_duration_s"], ascending=[True, True])
    elif sort_by == "lay":
        df_final = df_final.sort_values(["stop_count", "total_duration_s"], ascending=[True, True])
    else:
        df_final = df_final.sort_values(["total_duration_s"], ascending=[True])

    # page content
    content = []

    # create title/subtitle div
    title = dmc.Text("Title", style={"fontSize": 30, "fontWeight": 400})
    subtitle = dmc.Text("Subtitle", color="dimmed", style={"marginBottom": 15})
    title_subtitle = html.Div(
        [
            title,
            subtitle
        ]
    )

    # content header
    content_header = dmc.Group(
        [
            title_subtitle,
            sort_select
        ],
        position="apart",
        align="flex-start"
    )
    content.append(content_header)

    if df_final.empty:
        # no flights found
        subcontent = dmc.Text("No flights found")
    else:
        # create accordion for flights
        accordion_items = []

        # iterate over all flights in df_final
        for index, row in islice(df_final.iterrows(), 10):
            # layout of accordion label depends on stop_count
            if row.stop_count == 1:
                # create accordion label
                accordion_label = [dmc.Grid(
                    [
                        # Airlines
                        dmc.Col(
                            [
                                html.Div(
                                    [
                                        dmc.Text(
                                            (row.f1_airline_code, ", ", row.f2_airline_code),
                                            style={"fontSize": 20, "fontWeight": 400}
                                        ),
                                        dmc.Text(
                                            "Airlines",
                                            color="dimmed", style={"fontSize": 14, "fontWeight": 400})
                                    ],
                                )
                            ],
                            lg=3,
                            md=3,
                            sm=6,
                            xs=6,
                        ),
                        # Time + Departure/Destination Airports
                        dmc.Col(
                            [
                                html.Div(
                                    [
                                        dmc.Text(
                                            (row.f1_time_from_str, " – ", row.f2_time_to_str),
                                            style={"fontSize": 20, "fontWeight": 500}
                                        ),
                                        dmc.Text(
                                            (row.f1_airport_from, " – ", row.f2_airport_to),
                                            color="dimmed", style={"fontSize": 14, "fontWeight": 400}
                                        )
                                    ],
                                )
                            ],
                            lg=3,
                            md=3,
                            sm=6,
                            xs=6
                        ),
                        # Duration
                        dmc.Col(
                            [
                                html.Div(
                                    [
                                        dmc.Text(
                                            row.total_duration,
                                            style={"fontSize": 20, "fontWeight": 400}
                                        ),
                                    ],
                                )
                            ],
                            lg=3,
                            md=3,
                            sm=6,
                            xs=6
                        ),
                        # Stops
                        dmc.Col(
                            [
                                html.Div(
                                    [
                                        dmc.Text(
                                            row.stop_count_str,
                                            style={"fontSize": 20, "fontWeight": 400}
                                        ),
                                        dmc.Text(
                                            (row.layover_duration_1, " in ", row.f1_airport_to),
                                            color="dimmed", style={"fontSize": 14, "fontWeight": 400}
                                        )
                                    ],
                                )
                            ],
                            lg=3,
                            md=3,
                            sm=6,
                            xs=6
                        ),
                    ],

                )]

                # create accordion content
                accordion_content = dmc.Timeline(
                    [
                        dmc.TimelineItem(
                            [
                                dmc.Text("Test 1"),
                                dmc.Text("Test 2")
                            ],
                            lineVariant="dotted", title="Titel",

                        ),
                        dmc.TimelineItem("Test 2", lineVariant="dotted", title="Titel 2"),
                        dmc.TimelineItem("Test 3", lineVariant="dotted", title="Titel 3"),
                    ],
                    active=1,
                    color="green"
                )
            else:
                accordion_label = row.arr_time
                accordion_content = dmc.Timeline(
                    [
                        dmc.TimelineItem(
                            [
                                dmc.Text("Test 1"),
                                dmc.Text("Test 2")
                            ],
                            lineVariant="dotted", title="Titel",

                        ),
                        dmc.TimelineItem("Test 2", lineVariant="dotted", title="Titel 2"),
                        dmc.TimelineItem("Test 3", lineVariant="dotted", title="Titel 3"),
                    ],
                    active=1,
                    color="green"
                )

            # add accordion item
            accordion_item = dmc.AccordionItem(children=accordion_content, label=accordion_label)
            accordion_items.append(accordion_item)

        # add accordion
        subcontent = dmc.Accordion(children=accordion_items, multiple=True, iconPosition="right")

    # add subcontent
    content.append(subcontent)
    return content, sort_by


@callback(
    Output("airport_to", "data"),
    Input("airport_to", "value")
)
def get_airport_to(value):
    session = Session()

    a = aliased(Airport)
    airport_stmt = \
        select(a.airport_iata_code, a.airport_name). \
        where(a.airport_type == "large_airport", a.airport_scheduled_service == "yes")
    airports = pd.read_sql(airport_stmt, session.bind)

    airports["label_value"] = airports["airport_name"] + " (" + airports["airport_iata_code"] + ")"
    airports = airports.drop(["airport_name"], axis=1)
    airports = airports.sort_values(by=["label_value"])
    airports = airports.rename(columns={"label_value": "label"})
    airports = airports.rename(columns={"airport_iata_code": "value"})
    return airports.to_dict("records")


@callback(
    Output("airport_from", "data"),
    Input("airport_from", "value")
)
def get_airport_from(value):
    session = Session()

    a = aliased(Airport)
    b = aliased(Country)
    c = aliased(Region)
    airport_stmt = \
        select(
            a.airport_iata_code,  a.airport_continent, b.country_name,
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

    df_air = pd.DataFrame(columns=["label", "value", "group"])
    df_air["label"] = (airports["airport_name"] + " (" + airports["airport_iata_code"] + ")").drop_duplicates()
    df_air["value"] = ("air#" + airports["airport_iata_code"])
    df_air["group"] = "Airport"
    df_air = df_air.dropna()

    df_from = pd.concat([df_con, df_cou, df_reg, df_mun, df_air])
    df_from = df_from.sort_values(["group", "label"], ascending=[True, True]).reset_index(drop=True)

    return df_from.to_dict("records")


"""
bullet=[
                              dmc.ThemeIcon(
                                  DashIconify(
                                      icon="cil:airplane-mode",
                                      width=22
                                  ),
                                  radius=30,
                                  size=36,
                                  variant="light",
                                  color="indigo"
                              )
                          ]
"""