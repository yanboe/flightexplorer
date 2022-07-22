import dash
import dash_mantine_components as dmc

from dash import html, dcc
from dash_iconify import DashIconify


layout = dmc.Container(
    [
        # Title + Subtitle
        dmc.Container(
            [
                dmc.Text(
                    "Airport Explorer",
                    align="center",
                    style={"fontSize": 30}
                ),
                dmc.Text(
                    "Find the airport best suited to your needs",
                    align="center"
                ),
            ],
            pl=8,
            pr=8,
            style={"marginTop": 30, "marginBottom": 20},
        ),

        # Paper for "explore flights" and "compare airports"
        dmc.Container(
            [
                dmc.Grid(
                    [
                        # Compare airports
                        dmc.Col(
                            [
                                dcc.Link(
                                    [
                                        dmc.Paper(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.ThemeIcon(
                                                            DashIconify(icon="ic:round-ssid-chart", height=20),
                                                            size=40,
                                                            radius=40,
                                                            variant="light"
                                                        ),
                                                        dmc.Text(
                                                            "Compare Airports",
                                                            weight=500,
                                                            style={"marginTop": 15, "marginBottom": 5}
                                                        ),
                                                        dmc.Text(
                                                            "Which airport do you usually choose when travelling? "
                                                            "Do you compare flights from different airports? "
                                                            "This tool makes it easy to find the best airport for "
                                                            "your needs. Simply enter your region and your destination "
                                                            " and you're good to go!",
                                                            color="dimmed",
                                                            size="sm",
                                                            align="center",
                                                            style={"lineHeight": 1.6, "marginBottom": 10}
                                                        ),
                                                    ],
                                                    direction="column",
                                                    spacing=0,
                                                    align="center"
                                                )
                                            ],
                                            p="lg"
                                        )
                                    ],
                                    href="/airports/",
                                    style={"textDecoration": "none"}
                                )
                            ],
                            lg=5,
                            md=5,
                            sm=12,
                            xs=12,
                            style={
                                "border": "1px solid rgb(222, 226, 230)",
                                "borderRadius": "4px",
                                "padding": 0,
                                "display": "flex",
                                "margin": 15,
                            }
                        ),

                        # Explore flights
                        dmc.Col(
                            [
                                dcc.Link(
                                    [
                                        dmc.Paper(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.ThemeIcon(
                                                            DashIconify(
                                                                icon="ic:round-airplanemode-active",
                                                                height=20,
                                                                rotate=1
                                                            ),
                                                            size=40,
                                                            radius=40,
                                                            variant="light"
                                                        ),
                                                        dmc.Text(
                                                            "Explore Flights",
                                                            weight=500,
                                                            style={"marginTop": 15, "marginBottom": 5}
                                                        ),
                                                        dmc.Text(
                                                            [
                                                                "This tool lets you explore flights based on your ",
                                                                "selection. Since the flights are sourced from the ",
                                                                "OpenSky Network, only past flights are available."
                                                            ],
                                                            color="dimmed",
                                                            size="sm",
                                                            align="center",
                                                            style={"lineHeight": 1.6, "marginBottom": 10}
                                                        ),
                                                    ],
                                                    direction="column",
                                                    spacing=0,
                                                    align="center"
                                                )
                                            ],
                                            p="lg"
                                        )
                                    ],
                                    href="/flights/",
                                    style={"textDecoration": "none", "height": "100%"}
                                )
                            ],
                            lg=5,
                            md=5,
                            sm=12,
                            xs=12,
                            style={
                                "border": "1px solid rgb(222, 226, 230)",
                                "borderRadius": "4px",
                                "padding": 0,
                                "display": "flex",
                                "margin": 15,
                            }
                        ),
                    ],
                    justify="center",
                    grow=True
                )
            ],
            pl=8,
            pr=8
        ),

        # Paper for additional information
        dmc.Container(
            [
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text(
                                                    "What's the purpose of this website?",
                                                    weight=500,
                                                    size="xl",
                                                    style={"marginTop": 15, "marginBottom": 5}
                                                ),
                                                dmc.Text(
                                                    [
                                                        "I've created this app for my Master's Thesis at the ",
                                                        html.A(
                                                            "University of Applied Sciences of the Grisons",
                                                            href="https://www.fhgr.ch/en/",
                                                            target="_blank",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        ". The main goal of the app is to offer a tool that allows ",
                                                        "users to compare airports in their region to find the one ",
                                                        "best suited to their needs.",
                                                        dmc.Space(h=10),
                                                        "The data for this project is provided by the ",
                                                        html.A(
                                                            "OpenSky Network",
                                                            href="https://opensky-network.org/",
                                                            target="_blank",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        ", a non-profit association based in Switzerland. The full ",
                                                        "dataset can be downloaded ",
                                                        html.A(
                                                            "here",
                                                            href="https://zenodo.org/record/6797232",
                                                            target="_blank",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        ". ",
                                                        dmc.Space(h=10),
                                                        "The app itself is built with ",
                                                        html.A(
                                                            "Dash",
                                                            href="https://dash.plotly.com/",
                                                            target="_blank",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        " and uses ",
                                                        html.A(
                                                            "Dash Mantine Components",
                                                            href="https://www.dash-mantine-components.com/",
                                                            target="_blank",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        "."
                                                    ],
                                                    size="md",
                                                    style={"lineHeight": 1.6, "marginBottom": 30}
                                                ),
                                                dmc.Text(
                                                    [
                                                        "Still have questions? Head over to the ",
                                                        dcc.Link(
                                                            "FAQ",
                                                            href="/faq/",
                                                            style={
                                                                "textDecoration": "none",
                                                                "color": "#1c7ed6"
                                                            }
                                                        ),
                                                        " page!"
                                                    ],
                                                    size="sm",
                                                    style={"lineHeight": 1.6, "marginBottom": 10}
                                                ),
                                            ],
                                            direction="column",
                                            spacing=0,
                                        )
                                    ],
                                    p="lg"
                                )
                            ],
                            lg=10,
                            md=10,
                            sm=12,
                            xs=12,
                            style={
                                "border": "1px solid rgb(222, 226, 230)",
                                "borderRadius": "4px",
                                "padding": 0,
                                "display": "flex",
                                "margin": 15,
                                "marginTop": 23,
                            }
                        )
                    ],
                    justify="center",
                    grow=True
                )
            ],
            pl=8,
            pr=8
        ),
    ],
    pl=0,
    pr=0
)

dash.register_page(
    __name__,
    path="/",
    name="Home",
    title="Home",
    layout=layout
)
