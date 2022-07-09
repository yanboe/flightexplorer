import dash
import pytz
import dash_mantine_components as dmc

from dash import html, callback, Input, Output
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from itertools import islice

from lib.flight_list import get_flights
from utils.airport_utils import get_airports_from, get_airports_to, get_airports_by_key, get_airport_details
from utils.airline_utils import get_airline_details
from figures.map import map_figure
from lib.appshell import create_form

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
    icon=[DashIconify(icon="clarity:sort-by-line", width=25)],
    style={
        "width": 180
    },
    id="fp_sort_by"
)

page_content = dmc.Container(
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
                                                DashIconify(icon="clarity:map-marker-line", height=20),
                                                size=40,
                                                radius=40,
                                                variant="light"
                                            ),
                                            dmc.ThemeIcon(
                                                DashIconify(icon="clarity:date-line", height=20),
                                                size=40,
                                                radius=40,
                                                variant="light"
                                            ),
                                            dmc.ThemeIcon(
                                                DashIconify(icon="akar-icons:clock", height=20),
                                                size=40,
                                                radius=40,
                                                variant="light"
                                            ),
                                            dmc.ThemeIcon(
                                                DashIconify(icon="ic:round-connecting-airports", height=20),
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
                id="fp_content"
            ),
            # hidden "sort by" dropdown
            html.Div(sort_select, style={"display": "none"})
        ],
        loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
    ),
)

layout = [create_form("fp"), page_content]

dash.register_page(
    __name__,
    path="/flights/",
    name="Explore Flights",
    title="Explore Flights",
    layout=layout
)


@callback(
    Output("fp_content", "children"),
    Output("fp_sort_by", "value"),
    Output("fp_dep_time", "value"),
    Output("fp_max_stops", "value"),
    Input("fp_airport_from", "value"),
    Input("fp_airport_to", "value"),
    Input("fp_date", "value"),
    Input("fp_dep_time", "value"),
    Input("fp_max_stops", "value"),
    Input("fp_flight_duration", "value"),
    Input("fp_layover_duration", "value"),
    Input("fp_sort_by", "value"),
    prevent_initial_call=True
)
def get_flightplan(airport_from, airport_to, flight_date, dep_time,
                   max_stops, flight_duration, layover_duration, sort_by):

    if (airport_from is None or airport_to is None or flight_date is None or
        flight_duration is None or layover_duration is None or sort_by is None):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # Get list of airports based on selected value
    origin = get_airports_by_key(airport_from)
    destination = get_airports_by_key(airport_to)

    # Convert flight_date to timezone aware
    date_no_tz = datetime.strptime(flight_date, "%Y-%m-%d")
    date_with_tz = pytz.utc.localize(date_no_tz)

    # Add departure time from/to depending on selection
    if dep_time == "night":
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=5, minutes=59)
    elif dep_time == "morning":
        delta_from = timedelta(hours=6)
        delta_to = timedelta(hours=11, minutes=59)
    elif dep_time == "afternoon":
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59)
    elif dep_time == "evening":
        delta_from = timedelta(hours=18)
        delta_to = timedelta(hours=23, minutes=59)
    elif dep_time == "anytime":
        delta_from = timedelta(hours=0)
        delta_to = timedelta(hours=23, minutes=59)
    else:
        delta_from = timedelta(hours=12)
        delta_to = timedelta(hours=17, minutes=59)

    # earliest_time = flight_date + delta_from
    earliest_time = date_with_tz + delta_from

    # latest_time = flight_date + delta_to
    latest_time = date_with_tz + delta_to

    # max stop count
    stop_cnt = int(max_stops)

    # get flights
    df_flights = get_flights(origin, destination, earliest_time, latest_time, layover_duration, stop_cnt)

    if not df_flights.empty:
        # drop flights that take longer than flight_duration
        flight_duration_s = flight_duration * 3600
        df_flights.drop(df_flights[df_flights.total_duration_s > flight_duration_s].index, inplace=True)

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

    # Create subcontent
    if df_flights.empty:
        # no flights found
        subcontent = dmc.Text("No flights found")
    else:
        # get airport details (full name and coordinates)
        df_airports = get_airport_details(df_flights)

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
                                    inline=True
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
                                    inline=True
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
                                    inline=True
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

        # add accordion
        subcontent = dmc.Accordion(children=accordion_items, multiple=True, iconPosition="right")

        # create and add map
        fig_map = map_figure(df_flights, df_airports)
        content.append(fig_map)

    # add subcontent
    content.append(subcontent)

    return content, sort_by, dep_time, max_stops


@callback(
    Output("fp_airport_to", "data"),
    Input("fp_airport_to", "value")
)
def get_airport_to(value):
    return get_airports_to()


@callback(
    Output("fp_airport_from", "data"),
    Input("fp_airport_from", "value")
)
def get_airport_from(value):
    return get_airports_from()
