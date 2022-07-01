import dash
import pytz
import dash_mantine_components as dmc

from dash import html, callback, Input, Output
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from itertools import islice

from lib.flights import get_flights
from lib.utils import get_airports_from, get_airports_to, get_airports_by_key


# sort by dropdown outside of callback to avoid callback exceptions
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
    Output("dep_time", "value"),
    Output("max_stops", "value"),
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

    if (airport_from is None or airport_to is None or flight_date is None or
        flight_duration is None or layover_duration is None or sort_by is None):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # TODO: Validate/pass origin
    origin = get_airports_by_key(airport_from)

    # TODO: Validate/pass destination
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
    df_final = get_flights(origin, destination, earliest_time, latest_time, layover_duration, stop_cnt)

    if not df_final.empty:
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
        elif sort_by == "stp":
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
                accordion_content = dmc.Container(
                    [
                        # 1st flight
                        dmc.Timeline(
                            [
                                dmc.TimelineItem(
                                    dmc.Text(("Travel time: ", row.f1_duration), color="dimmed"),
                                    lineVariant="dotted",
                                    title=(row.f1_time_from_str, " · ", row.f1_airport_from_long),
                                ),
                                dmc.TimelineItem(
                                    dmc.Text(row.f1_airline_name, color="dimmed"),
                                    lineVariant="dotted",
                                    title=(row.f1_time_to_str, " · ", row.f1_airport_to_long),
                                )
                            ],
                        ),

                        # Layover information
                        dmc.Divider(variant="solid", style={"marginTop": "20px", "marginBottom": "20px"}),
                        dmc.Text((row.layover_duration_1, " layover in ", row.f1_airport_to_long)),
                        dmc.Divider(variant="solid", style={"marginTop": "20px", "marginBottom": "20px"}),

                        # 2nd flight
                        dmc.Timeline(
                            [
                                dmc.TimelineItem(
                                    dmc.Text(("Travel time: ", row.f2_duration), color="dimmed"),
                                    lineVariant="dotted",
                                    title=(row.f2_time_from_str, " · ", row.f2_airport_from_long),
                                ),
                                dmc.TimelineItem(
                                    dmc.Text(row.f2_airline_name, color="dimmed"),
                                    lineVariant="dotted",
                                    title=(row.f2_time_to_str, " · ", row.f2_airport_to_long),
                                )
                            ],
                        )
                    ],
                    px=0,
                    mt=20,
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
    return content, sort_by, dep_time, max_stops


@callback(
    Output("airport_to", "data"),
    Input("airport_to", "value")
)
def get_airport_to(value):
    return get_airports_to()


@callback(
    Output("airport_from", "data"),
    Input("airport_from", "value")
)
def get_airport_from(value):
    return get_airports_from()
