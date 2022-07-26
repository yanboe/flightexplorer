import dash
import pytz
import dash_mantine_components as dmc

from dash import html, callback, Input, Output
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from itertools import islice

from figures.map import create_map
from layout.appshell import create_form
from lib.flights import get_flights
from utils.airport_utils import get_airports_from, get_airports_to, get_airports_by_key, get_airport_details_fl
from utils.airline_utils import get_airline_details


# "sort by" dropdown outside of callback to avoid callback exceptions
sort_select = dmc.Select(
    data=[
        {"value": "dep", "label": "Departure Time"},
        {"value": "arr", "label": "Arrival Time"},
        {"value": "dur", "label": "Duration"},
        {"value": "stp", "label": "Stops"},
    ],
    radius="sm",
    size="sm",
    label="Sort by",
    value="dur",
    icon=[DashIconify(icon="ic:round-sort", width=25)],
    style={
        "width": 180
    },
    id="fl_sort_by"
)

page_content = dmc.Container(
    [
        dmc.LoadingOverlay(
            [
                html.Div(
                    [
                        # Initial content of the page
                        dmc.Paper(
                            [
                                dmc.Group(
                                    [
                                        # Icons
                                        dmc.Group(
                                            [
                                                dmc.ThemeIcon(
                                                    DashIconify(icon="ic:outline-place", height=20),
                                                    size=40,
                                                    radius=40,
                                                    variant="light"
                                                ),
                                                dmc.ThemeIcon(
                                                    DashIconify(icon="ic:outline-calendar-month", height=20),
                                                    size=40,
                                                    radius=40,
                                                    variant="light"
                                                ),
                                                dmc.ThemeIcon(
                                                    DashIconify(icon="ic:outline-watch-later", height=20),
                                                    size=40,
                                                    radius=40,
                                                    variant="light"
                                                ),
                                                dmc.ThemeIcon(
                                                    DashIconify(icon="ic:round-airline-stops", height=20),
                                                    size=40,
                                                    radius=40,
                                                    variant="light"
                                                ),
                                            ],
                                            direction="row",
                                            position="center"
                                        ),

                                        # Title
                                        dmc.Text(
                                            "Select an origin and a destination to see some flights",
                                            align="center",
                                            size="lg",
                                            style={
                                                "marginTop": 20,
                                                "marginBottom": 10
                                            }
                                        ),

                                        # Subtitle
                                        dmc.Text(
                                            "You can further customize your search by providing a range for the "
                                            "departure time, the maximum number of layovers, the maximum travel "
                                            "duration and the maximum layover duration.",
                                            color="dimmed",
                                            align="center",
                                            size="sm",
                                            style={
                                                "marginBottom": 10,
                                            }
                                        )
                                    ],
                                    direction="column",
                                    align="center",
                                    spacing=0,
                                )
                            ],
                            p="lg",
                        )
                    ],
                    id="fl_content"
                ),
                html.Div(id="fl_404")
            ],
            loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
        ),
        # hidden "sort by" dropdown
        html.Div(sort_select, style={"display": "none"})
    ],
    pl=0,
    pr=0
)

layout = [create_form("fl"), page_content]

dash.register_page(
    __name__,
    path="/flights/",
    title="Explore Flights | Airport Explorer",
    description="Explore flights from an airport or a region to your destination.",
    layout=layout
)

print(dash.page_registry)

@callback(
    Output("fl_content", "children"),
    Output("fl_sort_by", "value"),
    Output("fl_dep_time", "value"),
    Output("fl_max_stops", "value"),
    Output("fl_404", "children"),
    Input("fl_airport_from", "value"),
    Input("fl_airport_to", "value"),
    Input("fl_date", "value"),
    Input("fl_dep_time", "value"),
    Input("fl_max_stops", "value"),
    Input("fl_flight_duration", "value"),
    Input("fl_layover_duration", "value"),
    Input("fl_sort_by", "value"),
    prevent_initial_call=True
)
def get_flightplan(ap_from, ap_to, flight_date, dep_time,
                   max_stops, flight_duration, layover_duration, sort_by):

    if not all([ap_from, ap_to, flight_date, dep_time, max_stops, flight_duration, layover_duration, sort_by]):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # Get list of airports based on selected value
    origin = get_airports_by_key(ap_from)
    destination = get_airports_by_key(ap_to)

    # datetime from/to
    date_no_tz = datetime.strptime(flight_date, "%Y-%m-%d")
    date_with_tz = pytz.utc.localize(date_no_tz)

    if dep_time == "night":
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=5, minutes=59, seconds=59)
    elif dep_time == "morning":
        delta_from = timedelta(hours=6)
        delta_to = timedelta(hours=11, minutes=59, seconds=59)
    elif dep_time == "afternoon":
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59, seconds=59)
    elif dep_time == "evening":
        delta_from = timedelta(hours=18)
        delta_to = timedelta(hours=23, minutes=59, seconds=59)
    elif dep_time == "anytime":
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=23, minutes=59, seconds=59)
    else:
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59, seconds=59)

    datetime_from = date_with_tz + delta_from
    datetime_to = date_with_tz + delta_to

    # max stop count
    stop_cnt = int(max_stops)

    # get flights
    df_flights = get_flights(origin, destination, datetime_from, datetime_to, layover_duration, stop_cnt, "unique")

    if not df_flights.empty:
        # drop flights that take longer than flight_duration
        flight_duration_s = flight_duration * 3600
        df_flights = df_flights.drop(df_flights[df_flights.total_duration_s > flight_duration_s].index)

    if not df_flights.empty:
        # sort df_flights according to input value
        if sort_by == "dur":
            df_flights = df_flights.sort_values(["total_duration_s"], ascending=[True])
        elif sort_by == "dep":
            df_flights = df_flights.sort_values(["f1_time_from", "total_duration_s"], ascending=[True, True])
        elif sort_by == "arr":
            df_flights = df_flights.sort_values(["arr_time", "total_duration_s"], ascending=[True, True])
        elif sort_by == "stp":
            df_flights = df_flights.sort_values(["stop_count", "total_duration_s"], ascending=[True, True])
        else:
            df_flights = df_flights.sort_values(["total_duration_s"], ascending=[True])
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, \
               dmc.Center(
                   [
                       dmc.Alert(
                           "Try changing some of the settings above - maybe the flight duration is a bit tight?",
                           title="No flights found",
                           color="yellow"
                       )
                   ]
               )

    # page content
    content = []

    # content header
    content_header = dmc.Group(
        [
            # Title/Subtitle
            html.Div(
                [
                    dmc.Text("Best flights", weight=500, style={"fontSize": 30}),
                    dmc.Text("Only the first 10 flights are shown.", color="dimmed", )
                ]
            ),
            # "Sort by" dropdown
            sort_select
        ],
        position="apart",
        align="flex-start",
        style={"marginBottom": 15}
    )
    content.append(content_header)

    # get airport details (full name and coordinates)
    df_airports = get_airport_details_fl(df_flights)

    # get airline details (full name)
    df_airlines = get_airline_details(df_flights)

    # create accordion for flights
    accordion_items = []

    # iterate over all flights in df_flights
    for index, row in islice(df_flights.iterrows(), 10):

        # Flight with 0 stops
        if row.stop_count == 0:
            # create accordion label
            accordion_label = [dmc.Grid(
                [
                    # Airlines
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Text(
                                        row.f1_airline_code,
                                        style={"fontSize": 20, "fontWeight": 400}
                                    ),
                                    dmc.Text(
                                        "Airline",
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400})
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
                                        (row.f1_time_from_str, " – ", row.f1_time_to_str),
                                        style={"fontSize": 20, "fontWeight": 500}
                                    ),
                                    dmc.Text(
                                        (
                                            df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                            " – ",
                                            df_airports.loc[row.f1_airport_to, "airport_iata_code"]
                                        ),
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
                                    dmc.Text(
                                        "Total travel time",
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
            accordion_content = dmc.Container(
                [
                    # 1st flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f1_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f1_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    ),
                ],
                px=0,
                mt=20,
            )

        # Flight with 1 stop
        elif row.stop_count == 1:
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
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400})
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
                                        (
                                            df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                            " – ",
                                            df_airports.loc[row.f2_airport_to, "airport_iata_code"]
                                        ),
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
                                    dmc.Text(
                                        "Total travel time",
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
                                        (
                                            row.layover_duration_1,
                                            " in ",
                                            df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                                        ),
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
            accordion_content = dmc.Container(
                [
                    # 1st flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f1_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f1_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    ),

                    # Layover information
                    dmc.Group(
                        [
                            dmc.Text(
                                (
                                    row.layover_duration_1,
                                    " layover in ",
                                    df_airports.loc[row.f1_airport_to, "airport_name"]
                                ),
                                inline=True,
                                style={"lineHeight": 1.6}
                            )
                        ],
                        class_name="group-layover"
                    ),

                    # 2nd flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f2_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f2_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f2_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f2_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f2_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f2_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f2_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f2_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    )
                ],
                px=0,
                mt=20,
            )

        # Flight with 2 stops
        elif row.stop_count == 2:
            # create accordion label
            accordion_label = [dmc.Grid(
                [
                    # Airlines
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Text(
                                        (row.f1_airline_code, ", ", row.f2_airline_code, ", ", row.f3_airline_code),
                                        style={"fontSize": 20, "fontWeight": 400}
                                    ),
                                    dmc.Text(
                                        "Airlines",
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400})
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
                                        (row.f1_time_from_str, " – ", row.f3_time_to_str),
                                        style={"fontSize": 20, "fontWeight": 500}
                                    ),
                                    dmc.Text(
                                        (
                                            df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                            " – ",
                                            df_airports.loc[row.f3_airport_to, "airport_iata_code"]
                                        ),
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
                                    dmc.Text(
                                        "Total travel time",
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
                                        (
                                            row.layover_duration_1,
                                            " in ",
                                            df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                                            ", ",
                                            row.layover_duration_2,
                                            " in ",
                                            df_airports.loc[row.f2_airport_to, "airport_iata_code"],
                                        ),
                                        color="dimmed",
                                        style={"fontSize": 14, "fontWeight": 400}
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
            accordion_content = dmc.Container(
                [
                    # 1st flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f1_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f1_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f1_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f1_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f1_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    ),

                    # 1st layover information
                    dmc.Group(
                        [
                            dmc.Text(
                                (
                                    row.layover_duration_1,
                                    " layover in ",
                                    df_airports.loc[row.f1_airport_to, "airport_name"]
                                ),
                                inline=True,
                                style={"lineHeight": 1.6}
                            ),
                        ],
                        class_name="group-layover"
                    ),

                    # 2nd flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f2_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f2_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f2_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f2_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f2_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f2_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f2_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f2_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    ),

                    # 2nd layover information
                    dmc.Group(
                        [
                            dmc.Text(
                                (
                                    row.layover_duration_2,
                                    " layover in ",
                                    df_airports.loc[row.f2_airport_to, "airport_name"]
                                ),
                                inline=True,
                                style={"lineHeight": 1.6}
                            )
                        ],
                        class_name="group-layover"
                    ),

                    # 3rd flight
                    dmc.Timeline(
                        [
                            dmc.TimelineItem(
                                dmc.Text(("Flight duration: ", row.f3_duration), color="dimmed"),
                                lineVariant="dotted",
                                title=(
                                    row.f3_time_from_str,
                                    " · ",
                                    df_airports.loc[row.f3_airport_from, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f3_airport_from, "airport_iata_code"],
                                    ")"
                                ),
                            ),
                            dmc.TimelineItem(
                                dmc.Text(
                                    df_airlines.loc[row.f3_airline_code, "airline_name"],
                                    color="dimmed"
                                ),
                                lineVariant="dotted",
                                title=(
                                    row.f3_time_to_str,
                                    " · ",
                                    df_airports.loc[row.f3_airport_to, "airport_name"],
                                    " (",
                                    df_airports.loc[row.f3_airport_to, "airport_iata_code"],
                                    ")"
                                ),
                            )
                        ],
                        bulletSize=22,
                        lineWidth=3,
                        active=1
                    ),
                ],
                px=0,
                mt=20,
            )

        else:
            continue

        # add accordion item
        accordion_item = dmc.AccordionItem(children=accordion_content, label=accordion_label)
        accordion_items.append(accordion_item)

    # create and add map
    fig_map = create_map(df_flights, df_airports)
    content.append(fig_map)

    # add accordion
    subcontent = dmc.Accordion(children=accordion_items, multiple=True, iconPosition="right")

    # add subcontent
    content.append(subcontent)

    return content, sort_by, dep_time, max_stops, []


@callback(
    Output("fl_airport_to", "data"),
    Input("fl_airport_to", "value")
)
def get_airport_to(value):
    return get_airports_to()


@callback(
    Output("fl_airport_from", "data"),
    Input("fl_airport_from", "value")
)
def get_airport_from(value):
    return get_airports_from("fl")
