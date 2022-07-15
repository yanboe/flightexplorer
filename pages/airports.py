import dash
import pytz
import dash_mantine_components as dmc
import pandas as pd

from dash import html, callback, Input, Output, dcc, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime, timedelta
from itertools import islice

from figures.bar import create_bar
from figures.heatmap import create_heatmap
from figures.scatter import create_scatter
from layout.appshell import create_form
from layout.utils import create_kpi, create_display_diff
from lib.flights import get_flights
from lib.kpi import get_unweighted_kpi, get_weighted_kpi
from utils.airport_utils import get_airports_from, get_airports_to, get_airports_by_key, get_airport_details_ap


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

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
                    id="ap_content"
                ),
                html.Div(id="ap_404"),
                dcc.Store(id="df_unweighted_kpi"),
                dcc.Store(id="df_unweighted_kpi_prev"),
                dcc.Store(id="df_weighted_kpi"),
                dcc.Store(id="df_weighted_kpi_prev"),
                dcc.Store(id="ap_weight_store")
            ],
            loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
        ),
        # hidden "preference" dropdown
        html.Div(pref_select, style={"display": "none"}),
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
def get_unweighted_data(airport_from, airport_to, flight_date, period,
                        max_stops, flight_duration, layover_duration):

    if (airport_from is None or airport_to is None or flight_date is None or
        flight_duration is None or layover_duration is None):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # Get list of airports based on selected value
    origin = get_airports_by_key(airport_from)
    destination = get_airports_by_key(airport_to)

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

    # get flights + kpi for previous period
    period_int = int(period)
    delta = timedelta(days=period_int)

    datetime_from = datetime_from - delta
    datetime_to = datetime_to - delta
    df_flights_prev = get_flights(origin, destination, datetime_from, datetime_to, layover_duration, stop_cnt, "all")

    if not df_flights.empty or not df_flights_prev.empty:
        # drop flights that take longer than flight_duration
        flight_duration_s = flight_duration * 3600
        df_flights.drop(df_flights[df_flights.total_duration_s > flight_duration_s].index, inplace=True)
        df_flights_prev.drop(df_flights_prev[df_flights_prev.total_duration_s > flight_duration_s].index, inplace=True)

        df_kpi = get_unweighted_kpi(df_flights)
        df_kpi_prev = get_unweighted_kpi(df_flights_prev)

        if len(df_kpi) > 1 and len(df_kpi_prev) > 1:
            return df_kpi.to_json(orient="split"), df_kpi_prev.to_json(orient="split"), dash.no_update

    return dash.no_update, \
           dash.no_update, \
           dmc.Center(
               [
                   dmc.Alert(
                       "Try changing some of the settings above - maybe the flight duration is a bit tight?",
                       title="No airports found to compare",
                       color="yellow"
                   )
               ]
           )




@callback(
    Output("df_weighted_kpi", "data"),
    Output("df_weighted_kpi_prev", "data"),
    Output("ap_weight_store", "data"),
    Input("df_unweighted_kpi", "data"),
    Input("df_unweighted_kpi_prev", "data"),
    Input("ap_weight", "value"),
    prevent_initial_call=True
)
def get_weighted_data(df, df_prev, weight):
    df_kpi = pd.read_json(df, orient="split")
    df_kpi_prev = pd.read_json(df_prev, orient="split")

    # Weighted KPIs
    df_weighted_kpi = get_weighted_kpi(df_kpi, weight)
    df_weighted_kpi_prev = get_weighted_kpi(df_kpi_prev, weight)

    return df_weighted_kpi.to_json(orient="split"), df_weighted_kpi_prev.to_json(orient="split"), weight


@callback(
    Output("ap_content", "children"),
    Input("df_weighted_kpi", "data"),
    Input("df_weighted_kpi_prev", "data"),
    State("ap_weight_store", "data"),
    prevent_initial_call=True
)
def get_ap_content(df, df_prev, weight):
    df_kpi = pd.read_json(df, orient="split")
    df_kpi_prev = pd.read_json(df_prev, orient="split")
    print(df_kpi)
    print(df_kpi_prev)

    # Align dataframes to fill missing airports with 0
    df_kpi = df_kpi.set_index("airport")
    df_kpi_prev = df_kpi_prev.set_index("airport")
    df_kpi, df_kpi_prev = df_kpi.align(df_kpi_prev, join="outer", axis=0, fill_value=0)

    # Sort by rating
    df_kpi = df_kpi.reset_index().sort_values("rating", ascending=False)
    df_kpi_prev = df_kpi_prev.reset_index().sort_values("rating", ascending=False)

    print(df_kpi)
    print(df_kpi_prev)

    # get airport details (full name)
    df_airports = get_airport_details_ap(df_kpi)

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

    ranking_items = []
    i = 0

    # Create container for every airport
    for index, row in islice(df_kpi.iterrows(), 10):
        i += 1

        # Calculate rating difference
        prev_rating = df_kpi_prev.loc[df_kpi_prev.airport == row.airport]["rating"].values[0]
        diff = create_display_diff(row.rating, prev_rating)

        fig_bar = create_bar(row, df_kpi_prev)
        ranking_item = dmc.Container(
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
                                                df_airports.loc[row.airport, "airport_name"],
                                                " (",
                                                df_airports.loc[row.airport, "airport_iata_code"],
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
                                                dmc.Text((f"{row.rating:.2f}", "/10"), size="lg", align="center"),
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

                # Radar Chart
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                fig_bar
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
        ranking_items.append(ranking_item)

    import plotly.figure_factory as ff

    values = [[5, 4, 15, 23, 1, 4, 6, 2, 5, 4, 1, 14, 8, 21, 4, 1, 5, 8, 1, 7, 12, 20, 2, 2, 13]]
    dist_fig = ff.create_distplot(values, ["dist"])

    # Create subcontent
    subcontent = dmc.Tabs(
        [
            # Overview Tab
            dmc.Tab(
                [
                    dmc.Text("Overview", weight=400, style={"fontSize": 26}),
                    dcc.Graph(figure=dist_fig)
                ],
                label="Overview",
            ),

            # Airports Tab
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
                        ranking_items
                    )
                ],
                label="Airports",
            ),

            # Visualizations Tab
            dmc.Tab(
                [
                    dmc.Text("Visualizations", weight=400, style={"fontSize": 26, "marginBottom": 15}),
                    html.Div(
                        [
                            # Static Heatmap
                            create_heatmap("Heatmap", "Heatmap Description", df_kpi),

                            # Interactive Scatter Plot
                            dmc.Paper(
                                [
                                    dmc.Text("Scatter Plot", weight=300, style={"fontSize": 26}),
                                    dmc.Text("Scatter Plot Description", color="dimmed"),
                                    dcc.Graph(
                                        figure=create_scatter(df_kpi, df_kpi.kpi1_weighted, df_kpi.kpi2_weighted),
                                        id="fig_scatter"
                                    )
                                ],
                                p="lg",
                                radius="sm",
                                withBorder=True,
                                mb=15
                            )
                        ]
                    )
                ],
                label="Visualizations",
            )
        ],
        position="center",
        tabPadding="xl",
    )

    # add subcontent
    content.append(subcontent)

    return content


@callback(
    Output("ap_airport_to", "data"),
    Input("ap_airport_to", "value")
)
def get_airport_to(value):
    print("ap airport to")
    return get_airports_to()


@callback(
    Output("ap_airport_from", "data"),
    Input("ap_airport_from", "value")
)
def get_airport_from(value):
    print("ap airport from")
    return get_airports_from("ap")
