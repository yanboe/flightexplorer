import dash
import dash_mantine_components as dmc

from dash import html, callback, Input, Output, dcc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils.airport_utils import get_airports_from, get_airports_to, get_airports_by_key
from lib.appshell import create_form
from lib.utils import create_graph_dummy


graphs = html.Div(
    [
        create_graph_dummy(graph_id=1),
        create_graph_dummy(graph_id=2),
    ]
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
                    id="fi_content"
                ),
            ],
            loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
        ),
        html.Div(graphs, style={"display": "none"})
    ]
)
layout = [create_form("fi"), page_content]

dash.register_page(
    __name__,
    path="/airports/",
    name="Compare Airports",
    title="Compare Airports",
    layout=layout
)


@callback(
    Output("fi_content", "children"),
    Output("fi_dep_time", "value"),
    Output("fi_max_stops", "value"),
    Input("fi_airport_from", "value"),
    Input("fi_airport_to", "value"),
    Input("fi_date", "value"),
    Input("fi_dep_time", "value"),
    Input("fi_max_stops", "value"),
    Input("fi_flight_duration", "value"),
    Input("fi_layover_duration", "value"),
    prevent_initial_call=True
)
def get_flightindex(airport_from, airport_to, flight_date, dep_time,
                    max_stops, flight_duration, layover_duration):

    if (airport_from is None or airport_to is None or flight_date is None or
        flight_duration is None or layover_duration is None):
        # Do not update if mandatory fields are empty
        raise PreventUpdate

    # Get list of airports based on selected value
    origin = get_airports_by_key(airport_from)
    destination = get_airports_by_key(airport_to)

    # page content
    content = []

    # content header
    content_header = dmc.Group(
        [
            # Title/Subtitle
            html.Div(
                [
                    dmc.Text("Results", style={"fontSize": 30, "fontWeight": 400}),
                    dmc.Text("Only the first 10 flights are shown.", color="dimmed", )
                ]
            ),
        ],
        position="apart",
        align="flex-start",
        style={"marginBottom": 15}
    )
    content.append(content_header)

    subcontent = dmc.Tabs(
        [
            dmc.Tab(
                label="Airports",
                icon=[DashIconify(icon="clarity:view-list-line", width=22)]
            ),
            dmc.Tab(
                graphs,
                label="Visualizations",
                icon=[DashIconify(icon="clarity:line-chart-line", width=22)]
            )
        ],
        grow=True,
        position="center"
    )

    # add subcontent
    content.append(subcontent)
    #content.append(graphs)

    return content, dep_time, max_stops


@callback(
    Output("fi_airport_to", "data"),
    Input("fi_airport_to", "value")
)
def get_airport_to(value):
    return get_airports_to()


@callback(
    Output("fi_airport_from", "data"),
    Input("fi_airport_from", "value")
)
def get_airport_from(value):
    return get_airports_from()


# TODO: Input
@callback(
    Output("fi_graph_title_1", "children"),
    Input("fi_airport_from", "value")
)
def get_title(value):
    return "sup"


# TODO: Input
@callback(
    Output("fi_graph_title_2", "children"),
    Input("fi_airport_from", "value")
)
def get_title(value):
    return "sup 2"
