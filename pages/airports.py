import dash
import pytz
import dash_mantine_components as dmc
import pandas as pd

from dash import html, callback, Input, Output, dcc, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from itertools import islice

from figures.apd_bar import create_apd_bar
from figures.corr import create_corr_heatmap
from figures.heatmap import create_heatmap
from figures.viz_bar import create_viz_bar
from layout.appshell import create_form
from layout.utils import create_kpi, create_display_diff
from lib.flights import get_flights
from lib.gap import get_gap
from lib.kpi import get_unweighted_kpi, get_weighted_kpi
from utils.airport_utils import get_airports_from, get_airports_to, get_airports_by_key, get_airport_details_ap


# "preference" dropdown outside of callback to avoid callback exceptions
pref_select = dmc.Select(
    data=[
        {"label": "No preference", "value": "NA"},
        {"label": "KPI1", "value": "kpi1"},
        {"label": "KPI2", "value": "kpi2"},
        {"label": "KPI3", "value": "kpi3"},
        {"label": "KPI4", "value": "kpi4"},
        {"label": "KPI5", "value": "kpi5"},
        {"label": "KPI6", "value": "kpi6"},
        {"label": "KPI7", "value": "kpi7"},
        {"label": "KPI8", "value": "kpi8"},
    ],
    radius="sm",
    size="sm",
    label="Preference",
    value="NA",
    icon=[DashIconify(icon="ic:outline-scale", width=25)],
    style={
        "width": 180
    },
    id="ap_weight"
)


page_content = dmc.Container(
    [
        dmc.LoadingOverlay(
            [
                html.Div(id="ap_404"),
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
                                            "Select an origin and a destination to compare airports",
                                            align="center",
                                            size="lg",
                                            style={
                                                "marginTop": 20,
                                                "marginBottom": 10
                                            }
                                        ),

                                        # Subtitle
                                        dmc.Text(
                                            "You can further customize your search by changing the range of the "
                                            "departure date, the maximum number of layovers, the maximum travel "
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
                    id="ap_content"
                ),
                dcc.Store(id="df_unweighted_kpi"),
                dcc.Store(id="df_unweighted_kpi_prev"),
                dcc.Store(id="df_weighted_kpi"),
                dcc.Store(id="df_weighted_kpi_prev"),
            ],
            loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
        ),
        # hidden "preference" dropdown
        html.Div(pref_select, style={"display": "none"}),
        dcc.Store(id="ap_preference"),
        dcc.Store(id="ap_active_tab")
    ],
    pl=0,
    pr=0
)
layout = [create_form("ap"), page_content]

dash.register_page(
    __name__,
    path="/airports/",
    name="Compare Airports",
    title="Compare Airports",
    layout=layout
)


@callback(
    Output("df_unweighted_kpi", "data"),
    Output("df_unweighted_kpi_prev", "data"),
    Output("ap_404", "children"),
    Input("ap_airport_from", "value"),
    Input("ap_airport_to", "value"),
    Input("ap_date", "value"),
    Input("ap_period", "value"),
    Input("ap_max_stops", "value"),
    Input("ap_flight_duration", "value"),
    Input("ap_layover_duration", "value"),
    prevent_initial_call=True
)
def get_unweighted_data(ap_from, ap_to, flight_date, period,
                        max_stops, flight_duration, layover_duration):

    if not all([ap_from, ap_to, flight_date, period, max_stops, flight_duration, layover_duration]):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # Get list of airports based on selected value
    origin = get_airports_by_key(ap_from)
    destination = get_airports_by_key(ap_to)

    # datetime from/to
    date_from_no_tz = datetime.strptime(flight_date[0], "%Y-%m-%d")
    date_from_with_tz = pytz.utc.localize(date_from_no_tz)
    date_to_no_tz = datetime.strptime(flight_date[1], "%Y-%m-%d")
    date_to_with_tz = pytz.utc.localize(date_to_no_tz)
    delta_from = timedelta(hours=0)
    delta_to = timedelta(hours=23, minutes=59, seconds=59)
    datetime_from = date_from_with_tz + delta_from
    datetime_to = date_to_with_tz + delta_to

    # max stop count
    stop_cnt = int(max_stops)

    # get flights + kpi for selected period
    df_flights = get_flights(origin, destination, datetime_from, datetime_to, layover_duration, stop_cnt, "all")
    df_gap = get_gap(origin, datetime_from, datetime_to)

    # get flights + kpi for previous period
    period_int = int(period)
    delta = timedelta(days=period_int)
    datetime_from = datetime_from - delta
    datetime_to = datetime_to - delta
    df_flights_prev = get_flights(origin, destination, datetime_from, datetime_to, layover_duration, stop_cnt, "all")
    df_gap_prev = get_gap(origin, datetime_from, datetime_to)

    if not df_flights.empty and not df_flights_prev.empty:
        # drop flights from df that take longer than flight_duration
        flight_duration_s = flight_duration * 3600
        df_flights = df_flights.\
            drop(df_flights[df_flights.total_duration_s > flight_duration_s].index)
        df_flights_prev = df_flights_prev.\
            drop(df_flights_prev[df_flights_prev.total_duration_s > flight_duration_s].index)

        # Get unweighted KPIs
        df_kpi = get_unweighted_kpi(df_flights, df_gap)
        df_kpi_prev = get_unweighted_kpi(df_flights_prev, df_gap_prev)

        if len(df_kpi) > 1 and len(df_kpi_prev) > 1:
            return df_kpi.to_json(orient="split"), df_kpi_prev.to_json(orient="split"), []

    return dash.no_update, \
           dash.no_update, \
           dmc.Center(
               [
                   dmc.Alert(
                       "Try changing some of the settings above - maybe the flight duration is a bit tight?",
                       title="No airports found to compare",
                       color="yellow"
                   )
               ],
               mb=10
           )


@callback(
    Output("df_weighted_kpi", "data"),
    Output("df_weighted_kpi_prev", "data"),
    Output("ap_preference", "data"),
    Input("df_unweighted_kpi", "data"),
    Input("df_unweighted_kpi_prev", "data"),
    Input("ap_weight", "value"),
    prevent_initial_call=True
)
def get_weighted_data(df, df_prev, weight):
    df_kpi = pd.read_json(df, orient="split")
    df_kpi_prev = pd.read_json(df_prev, orient="split")

    # Get weighted KPIs
    df_weighted_kpi = get_weighted_kpi(df_kpi, weight)
    df_weighted_kpi_prev = get_weighted_kpi(df_kpi_prev, weight)

    # Align dataframes to fill missing airports with 0
    df_weighted_kpi = df_weighted_kpi.set_index("airport")
    df_weighted_kpi_prev = df_weighted_kpi_prev.set_index("airport")
    df_weighted_kpi, df_weighted_kpi_prev = df_weighted_kpi.align(
        df_weighted_kpi_prev,
        join="outer",
        axis=0,
        fill_value=0
    )

    # get airport details
    df_airports = get_airport_details_ap(df_weighted_kpi)

    # replace ICAO code with IATA code (e.g. EGKK -> LGW for London Gatwick)
    df_weighted_kpi = pd.concat(
        [
            df_weighted_kpi,
            df_airports[["airport_iata_code", "airport_name"]]
        ],
        axis=1
    )
    df_weighted_kpi = df_weighted_kpi. \
        reset_index(drop=True). \
        rename(columns={"airport_iata_code": "airport"}). \
        set_index("airport")

    df_weighted_kpi_prev = pd.concat(
        [
            df_weighted_kpi_prev,
            df_airports[["airport_iata_code", "airport_name"]]
        ],
        axis=1
    )
    df_weighted_kpi_prev = df_weighted_kpi_prev. \
        reset_index(drop=True). \
        rename(columns={"airport_iata_code": "airport"}). \
        set_index("airport")

    # Sort by rating
    df_weighted_kpi = df_weighted_kpi.reset_index().sort_values("rating", ascending=False)
    df_weighted_kpi_prev = df_weighted_kpi_prev.reset_index().sort_values("rating", ascending=False)

    return df_weighted_kpi.to_json(orient="split"), df_weighted_kpi_prev.to_json(orient="split"), weight


@callback(
    Output("ap_content", "children"),
    Input("df_weighted_kpi", "data"),
    Input("df_weighted_kpi_prev", "data"),
    State("ap_preference", "data"),
    State("ap_active_tab", "data"),
    prevent_initial_call=True
)
def get_ap_content(df, df_prev, weight, active_tab):
    df_kpi = pd.read_json(df, orient="split")
    df_kpi_prev = pd.read_json(df_prev, orient="split")

    # page content
    content = []

    # content header
    content_header = dmc.Group(
        [
            # Title/Subtitle
            html.Div(
                [
                    dmc.Text("Best airports", weight=500, style={"fontSize": 30}),
                    dmc.Text("Switch between the tabs to explore more.", color="dimmed")
                ]
            ),
            # Preference dropdown
            dmc.Select(
                data=[
                    {"label": "No preference", "value": "NA"},
                    {"label": "Flights (GAP)", "value": "kpi1"},
                    {"label": "Airlines (GAP)", "value": "kpi2"},
                    {"label": "Destinations", "value": "kpi3"},
                    {"label": "Flights (ODP)", "value": "kpi4"},
                    {"label": "Airlines (ODP)", "value": "kpi5"},
                    {"label": "Flight Duration", "value": "kpi6"},
                    {"label": "Stops", "value": "kpi7"},
                    {"label": "Layover Time", "value": "kpi8"},
                ],
                radius="sm",
                size="sm",
                label="Preference",
                value=weight,
                icon=[DashIconify(icon="ic:outline-scale", width=25)],
                style={
                    "width": 180
                },
                id="ap_weight"
            )
        ],
        position="apart",
        align="flex-start",
        style={"marginBottom": 15}
    )
    content.append(content_header)

    # Content for "Overview" tab
    overview_container = []

    # Ranking Header
    overview = dmc.Container(
        [
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.Text(
                                [
                                    "Rank"
                                ],
                                size="lg",
                                align="center",
                                weight=500
                            )
                        ],
                        lg=1,
                        md=1,
                        sm=1,
                        xs=1
                    ),
                    dmc.Col(
                        [
                            dmc.Text(
                                [
                                    "Airport"
                                ],
                                size="lg",
                                weight=500
                            )
                        ],
                        lg=9,
                        md=9,
                        sm=9,
                        xs=9
                    ),
                    dmc.Col(
                        [
                            dmc.Text(
                                [
                                    "Rating"
                                ],
                                size="lg",
                                align="center",
                                weight=500
                            )
                        ],
                        lg=2,
                        md=2,
                        sm=2,
                        xs=2
                    )
                ]
            )
        ],
        p=5,
        style={
            "borderBottom": "2px solid rgb(222, 226, 230)"
        }
    )
    overview_container.append(overview)

    # Airports for Ranking
    i = 0
    for index, row in df_kpi.iterrows():
        i += 1
        overview = dmc.Container(
            [
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                dmc.Text(
                                    [
                                        i
                                    ],
                                    size="lg",
                                    align="center",
                                )
                            ],
                            lg=1,
                            md=1,
                            sm=1,
                            xs=1
                        ),
                        dmc.Col(
                            [
                                dmc.Text(
                                    [
                                        row.airport_name,
                                        " (",
                                        row.airport,
                                        ")"
                                    ],
                                    size="lg"
                                )
                            ],
                            lg=9,
                            md=9,
                            sm=9,
                            xs=9
                        ),
                        dmc.Col(
                            [
                                dmc.Text(
                                    [
                                        f"{row.rating:.2f}"
                                    ],
                                    size="lg",
                                    align="center"
                                )
                            ],
                            lg=2,
                            md=2,
                            sm=2,
                            xs=2
                        )
                    ]
                )
            ],
            p=10,
            style={
                "borderBottom": "1px solid rgb(222, 226, 230)"
            }
        )
        overview_container.append(overview)

    # Content for "Airport Details" tab
    airport_details = []
    i = 0
    for index, row in islice(df_kpi.iterrows(), 10):
        i += 1

        # Calculate rating difference
        prev_rating = df_kpi_prev.loc[df_kpi_prev.airport == row.airport]["rating"].values[0]
        diff = create_display_diff(row.rating, prev_rating)

        airport_detail = dmc.Container(
            [
                # Airport ranking header
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text(("Rank ", i), color="dimmed", size="sm"),
                                        dmc.Text(
                                            (
                                                row.airport_name,
                                                " (",
                                                row.airport,
                                                ")"
                                            ),
                                            size="lg",
                                            align="center"
                                        )
                                    ],
                                    direction="column",
                                    position="center",
                                    spacing=0
                                )
                            ],
                            lg=9,
                            md=9,
                            sm=9,
                            xs=12
                        ),
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        dmc.Text("Rating", color="dimmed", size="sm"),
                                        dmc.Group(
                                            [
                                                dmc.Text((f"{row.rating:.2f}", "/10.00"), size="lg", align="center"),
                                                dmc.Space(w="xs"),
                                                dmc.Text(diff, color="dimmed", size="xs")
                                            ],
                                            direction="row",
                                            align="center",
                                            spacing=0
                                        )
                                    ],
                                    direction="column",
                                    position="center",
                                    spacing=0
                                )
                            ],
                            lg=3,
                            md=3,
                            sm=3,
                            xs=12
                        ),
                    ],
                ),
                dmc.Divider(variant="solid", style={"marginTop": 10, "marginBottom": 20}),

                # Airport ranking KPIs
                dmc.Grid(
                    [
                        # Create KPIs
                        create_kpi("GAP · Flights", row, df_kpi_prev, row.airport, "kpi1_weighted"),
                        create_kpi("GAP · Airlines", row, df_kpi_prev, row.airport, "kpi2_weighted"),
                        create_kpi("GAP · Destinations", row, df_kpi_prev, row.airport, "kpi3_weighted"),
                        create_kpi("ODP · Flights", row, df_kpi_prev, row.airport, "kpi4_weighted"),
                        create_kpi("ODP · Airlines", row, df_kpi_prev, row.airport, "kpi5_weighted"),
                        create_kpi("ODP · Flight Duration", row, df_kpi_prev, row.airport, "kpi6_weighted"),
                        create_kpi("ODP · Stops", row, df_kpi_prev, row.airport, "kpi7_weighted"),
                        create_kpi("ODP · Layover Time", row, df_kpi_prev, row.airport, "kpi8_weighted"),
                    ]
                ),
                dmc.Divider(variant="solid", style={"marginTop": 10, "marginBottom": 20}),

                # Bar Chart
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                create_apd_bar(row, df_kpi_prev)
                            ],
                            lg=6,
                            md=6,
                            sm=12,
                            xs=12
                        )
                    ],
                    justify="center"
                )


            ],
            p=25,
            style={
                "border": "1px solid rgb(222, 226, 230)",
                "borderRadius": "4px",
                "marginBottom": 20
            }
        )
        airport_details.append(airport_detail)

    # Create subcontent
    subcontent = dmc.Tabs(
        [
            # Overview
            dmc.Tab(
                [
                    dmc.Text("Overview", weight=400, style={"fontSize": 26}),
                    dmc.Text(
                        [
                            "Some more information about this tab coming soon"
                        ],
                        color="dimmed",
                        size="sm",
                        style={"marginBottom": 15}
                    ),
                    html.Div(
                        overview_container,
                        style={
                            "marginBottom": 20
                        }
                    )
                ],
                label="Overview",
            ),

            # Airport Details
            dmc.Tab(
                [
                    dmc.Text("Airport ranking", weight=400, style={"fontSize": 26}),
                    dmc.Text(
                        [
                            "The numbers shown below are calculated using a Weighted Sum Model and represent relative "
                            "scores. These performance indicators are split into two groups: General Airport "
                            "Performance (GAP) and Origin-to-Destination Performance (ODP). The indicators in the "
                            "first group (GAP) describe general airport statistics, where an airport is ranked without "
                            "considering a destination. The second group (ODP) takes the destination into account."
                        ],
                        color="dimmed",
                        size="sm",
                        style={"marginBottom": 15}
                    ),
                    html.Div(
                        airport_details
                    )
                ],
                label="Airport Details",
            ),

            # Visualizations
            dmc.Tab(
                [
                    dmc.Text("Visualizations", weight=400, style={"fontSize": 26}),
                    dmc.Text(
                        [
                            "Some more information about this tab coming soon"
                        ],
                        color="dimmed",
                        size="sm",
                        style={"marginBottom": 15}
                    ),
                    html.Div(
                        [
                            # Static Heatmap
                            create_heatmap("Title coming soon", "Description coming soon", df_kpi),

                            # Interactive Horizontal Bar Chart
                            dmc.Paper(
                                [
                                    dmc.Group(
                                        [
                                            html.Div(
                                                [
                                                    dmc.Text("Title coming soon", weight=300, style={"fontSize": 26}),
                                                    dmc.Text("Description coming soon", color="dimmed"),
                                                ]
                                            ),
                                            # Dropdown for KPI that should be displayed
                                            dmc.Select(
                                                data=[
                                                    {"label": "Flights (GAP)", "value": "kpi1"},
                                                    {"label": "Airlines (GAP)", "value": "kpi2"},
                                                    {"label": "Destinations", "value": "kpi3"},
                                                    {"label": "Flights (ODP)", "value": "kpi4"},
                                                    {"label": "Airlines (ODP)", "value": "kpi5"},
                                                    {"label": "Flight Duration", "value": "kpi6"},
                                                    {"label": "Stops", "value": "kpi7"},
                                                    {"label": "Layover Time", "value": "kpi8"},
                                                ],
                                                radius="xl",
                                                size="sm",
                                                value="kpi1",
                                                style={
                                                    "width": 150
                                                },
                                                id="viz_kpi"
                                            )
                                        ],
                                        position="apart",
                                        align="flex-start",
                                        style={"marginBottom": 15}
                                    ),
                                    dcc.Graph(
                                        figure=create_viz_bar(df_kpi, "kpi1"),
                                        id="fig_viz_bar",
                                        config={"scrollZoom": True}
                                    )
                                ],
                                p="lg",
                                radius="sm",
                                withBorder=True,
                                mb=15
                            ),

                            # Correlation Heatmap
                            html.Div(
                                create_corr_heatmap("Title coming soon", "Description coming soon", df_kpi)
                            )
                        ],
                        style={
                            "marginBottom": 20
                        }
                    )
                ],
                label="Visualizations",
            )
        ],
        position="center",
        tabPadding="xl",
        active=active_tab,
        id="ap_tabs",
        style={
            "marginBottom": 15
        }
    )

    # add subcontent
    content.append(subcontent)

    return content


@callback(
    Output("ap_airport_to", "data"),
    Input("ap_airport_to", "value")
)
def get_airport_to(value):
    return get_airports_to()


@callback(
    Output("ap_airport_from", "data"),
    Input("ap_airport_from", "value")
)
def get_airport_from(value):
    return get_airports_from("ap")


@callback(
    Output("ap_active_tab", "data"),
    Input("ap_tabs", "active"),
    prevent_initial_call=True
)
def put_active_tab(active_tab):
    return active_tab


@callback(
    Output("fig_viz_bar", "figure"),
    Input("viz_kpi", "value"),
    State("df_weighted_kpi", "data"),
    prevent_initial_call=True
)
def update_viz_bar(kpi, df):
    df_kpi = pd.read_json(df, orient="split")

    return create_viz_bar(df_kpi, kpi)
