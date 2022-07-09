import dash
import dash_mantine_components as dmc

from dash import html, dcc
from dash_iconify import DashIconify


layout = html.Div(
    [
        # Title + Subtitle
        dmc.Container(
            [
                dmc.Text(
                    "Meaningful title",
                    align="center",
                    style={"fontSize": 30}
                ),
                dmc.Text(
                    "Meaningful subtitle",
                    align="center"
                ),
            ],
            size="lg",
            style={"marginTop": 30, "marginBottom": 20}
        ),

        # Paper for "explore flights" and "compare airports"
        dmc.Container(
            [
                dmc.Grid(
                    [
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
                                                            DashIconify(icon="cil:airplane-mode", height=20, rotate=1),
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
                                                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                                            "Etiam gravida, nisi vel varius condimentum, purus turpis "
                                                            "interdum nibh, in semper mauris purus in felis. Maecenas "
                                                            "lacinia lectus hendrerit, pellentesque nunc sit amet, "
                                                            "varius dui. Vivamus cursus lectus risus, non rutrum "
                                                            "libero laoreet in. Etiam lorem lorem, semper sit amet "
                                                            "urna ac, tempus commodo nibh. Ut pellentesque gravida "
                                                            "mi, at dignissim arcu. Donec cursus leo felis, "
                                                            "in rhoncus tortor aliquet nec. Phasellus congue volutpat "
                                                            "volutpat.",
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
                                                            DashIconify(icon="uil:comparison", height=20),
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
                                                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                                                            "Etiam gravida, nisi vel varius condimentum, purus turpis "
                                                            "interdum nibh, in semper mauris purus in felis. Maecenas "
                                                            "lacinia lectus hendrerit, pellentesque nunc sit amet, "
                                                            "varius dui. Vivamus cursus lectus risus, non rutrum "
                                                            "libero laoreet in. Etiam lorem lorem, semper sit amet "
                                                            "urna ac, tempus commodo nibh.",
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
                    ],
                    justify="center",
                    grow=True
                )
            ],
            size="lg"
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
                                                    "Explain what this website is about",
                                                    weight=500,
                                                    size="xl",
                                                    style={"marginTop": 15, "marginBottom": 5}
                                                ),
                                                dmc.Text(
                                                    "Explain some more",
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
            size="lg"
        )
    ]
)

dash.register_page(
    __name__,
    path="/",
    name="Home",
    title="Home",
    layout=layout
)
