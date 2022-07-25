import dash_mantine_components as dmc

from dash import html, dcc, page_container
from dash_iconify import DashIconify
from datetime import date


def create_header():
    return dmc.Header(
        [
            dmc.Container(
                [
                    dmc.Group(
                        [
                            # Logo/Page Name
                            dmc.Center(
                                [
                                    dcc.Link(
                                        [
                                            # Hide long text on small viewports
                                            dmc.MediaQuery(
                                                [
                                                    dmc.Group(
                                                        [
                                                            dmc.ThemeIcon(
                                                                DashIconify(
                                                                    icon="ic:round-airplanemode-active",
                                                                    width=22,
                                                                    rotate=1
                                                                ),
                                                                radius=30,
                                                                size=36,
                                                                variant="light",
                                                                color="blue"
                                                            ),
                                                            dmc.Text("Airport Explorer", size="xl", color="gray"),
                                                        ]
                                                    )
                                                ],
                                                smallerThan="sm",
                                                styles={"display": "none"},
                                            ),

                                            # Hide short text on large viewports
                                            dmc.MediaQuery(
                                                [
                                                    dmc.Group(
                                                        [
                                                            dmc.ThemeIcon(
                                                                DashIconify(
                                                                    icon="ic:round-airplanemode-active",
                                                                    width=22,
                                                                    rotate=3
                                                                ),
                                                                radius=30,
                                                                size=36,
                                                                variant="light",
                                                                color="blue"
                                                            ),
                                                            dmc.Text("", size="xl", color="gray"),
                                                        ]
                                                    )
                                                ],
                                                largerThan="sm",
                                                styles={"display": "none"},
                                            ),
                                        ],
                                        href="/",
                                        style={"textDecoration": "none"},
                                    ),
                                ]
                            ),
                            # Icons
                            dmc.Group(
                                [
                                    html.A(
                                        dmc.Tooltip(
                                            dmc.ThemeIcon(
                                                DashIconify(
                                                    icon="radix-icons:github-logo",
                                                    width=22,
                                                ),
                                                radius=30,
                                                size=36,
                                                variant="outline",
                                                color="gray",
                                            ),
                                            label="Source Code",
                                            position="bottom",
                                        ),
                                        href="https://github.com/yanboe/flightexplorer",
                                        target="_blank"
                                    )
                                ],
                                position="right",
                                align="center",
                                spacing="xl"
                            ),
                        ],
                        position="apart",
                        align="flex-start",
                    ),
                ],
                fluid=True,
            )
        ],
        height=70,
        fixed=True,
        p="md",
    )


def create_navbar():
    return dmc.Navbar(
        [
            dmc.Group(
                [
                    # Home
                    dcc.Link(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="ic:outline-home", width=18),
                                        size=30,
                                        radius=30,
                                        variant="light"
                                    ),
                                    dmc.Text("Home", size="sm", color="gray")
                                ]
                            )
                        ],
                        href="/",
                        style={"textDecoration": "none"}
                    ),

                    # /flights/
                    dcc.Link(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="ic:round-airplanemode-active", width=18, rotate=1),
                                        size=30,
                                        radius=30,
                                        variant="light"
                                    ),
                                    dmc.Text("Explore Flights", size="sm", color="gray")
                                ]
                            )
                        ],
                        href="/flights/",
                        style={"textDecoration": "none"}
                    ),

                    # /airports/
                    dcc.Link(
                        [
                            dmc.Group(
                                [
                                    dmc.ThemeIcon(
                                        DashIconify(icon="ic:round-ssid-chart", width=18),
                                        size=30,
                                        radius=30,
                                        variant="light"
                                    ),
                                    dmc.Text("Compare Airports", size="sm", color="gray")
                                ]
                            )
                        ],
                        href="/airports/",
                        style={"textDecoration": "none"}
                    ),
                    dmc.Divider(style={"marginBottom": 20, "marginTop": 20}),

                    # /faq/
                    dcc.Link(
                        [
                            dmc.Text("FAQ", size="sm", color="gray")
                        ],
                        href="/faq/",
                        style={"textDecoration": "none"}
                    ),

                    # /about/
                    dcc.Link(
                        [
                            dmc.Text("About", size="sm", color="gray")
                        ],
                        href="/about/",
                        style={"textDecoration": "none"}
                    ),
                ],
                grow=True,
                position="left",
                spacing="sm",
                direction="column",
                style={"paddingLeft": 30, "paddingRight": 30},
            ),
        ],
        fixed=True,
        position={"top": 70},
        width={"base": 300},
        id="navbar",
        style={
            "backgroundColor": "#f8f9fa"
        }
    )


def create_form(page):
    return dmc.Container(
        [
            dmc.Grid(
                [
                    # Airport From
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Select(
                                        searchable=True,
                                        clearable=True,
                                        nothingFound="No airport found!",
                                        icon=[DashIconify(icon="ic:outline-place", width=25)],
                                        limit=10,
                                        placeholder="Where from?",
                                        size="lg",
                                        maxDropdownHeight=500,
                                        id=(page + "_airport_from")
                                    )
                                ]
                            ),
                        ],
                        lg=4,
                        md=4,
                        sm=6,
                        xs=12
                    ),
                    # Airport To
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Select(
                                        searchable=True,
                                        clearable=True,
                                        nothingFound="No airport found!",
                                        icon=[DashIconify(icon="ic:outline-place", width=25)],
                                        limit=10,
                                        placeholder="Where to?",
                                        size="lg",
                                        maxDropdownHeight=500,
                                        id=(page + "_airport_to")
                                    )
                                ]
                            ),
                        ],
                        lg=4,
                        md=4,
                        sm=6,
                        xs=12
                    ),
                    # DatePicker (Flights) / DateRangePicker (Airports)
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.DatePicker(
                                        minDate=date(2019, 1, 1),
                                        maxDate=date(2022, 6, 30),
                                        value=date(2022, 5, 11),
                                        inputFormat="MMM D, YYYY",
                                        icon=[DashIconify(icon="ic:outline-calendar-month", width=25)],
                                        size="lg",
                                        clearable=False,
                                        id=(page + "_date")
                                    )
                                    if page == "fl"
                                    else
                                    dmc.DateRangePicker(
                                        minDate=date(2019, 1, 1),
                                        maxDate=date(2022, 6, 30),
                                        value=[date(2022, 5, 11), date(2022, 5, 18)],
                                        inputFormat="MMM D, YYYY",
                                        icon=[DashIconify(icon="ic:outline-calendar-month", width=25)],
                                        allowSingleDateInRange=True,
                                        size="lg",
                                        clearable=False,
                                        id=(page + "_date")
                                    )
                                ]
                            ),
                        ],
                        lg=4,
                        md=4,
                        sm=12,
                        xs=12
                    ),
                    # Departure Time (Flights) / Comparison Period (Airports)
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Select(
                                        data=[
                                            {"label": "Anytime", "value": "anytime"},
                                            {"label": "00:00 - 05:59", "value": "night"},
                                            {"label": "06:00 - 11:59", "value": "morning"},
                                            {"label": "12:00 - 17:59", "value": "afternoon"},
                                            {"label": "18:00 - 23:59", "value": "evening"},
                                        ],
                                        label="Departure Time",
                                        size="md",
                                        value="afternoon",
                                        icon=[DashIconify(icon="ic:outline-watch-later", width=25)],
                                        maxDropdownHeight=500,
                                        id=(page + "_dep_time")
                                    )
                                    if page == "fl"
                                    else
                                    dmc.Select(
                                        data=[
                                            {"value": "7", "label": "Last week"},
                                            {"value": "30", "label": "Last month"},
                                            {"value": "365", "label": "Last year"}
                                        ],
                                        label="Comparison Period",
                                        size="md",
                                        value="7",
                                        icon=[DashIconify(icon="ic:outline-calendar-month", width=25)],
                                        maxDropdownHeight=500,
                                        id=(page + "_period")
                                    )
                                ]
                            ),
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12
                    ),
                    # Max Stops
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Select(
                                        data=[
                                            {"label": "Any number of stops", "value": "9"},
                                            {"label": "Nonstop only", "value": "0"},
                                            {"label": "1 stop or less", "value": "1"},
                                            {"label": "2 stops or less", "value": "2"},
                                        ],
                                        label="Stops",
                                        size="md",
                                        value="9",
                                        icon=[DashIconify(icon="ic:round-airline-stops", width=25)],
                                        id=(page + "_max_stops"),
                                    )
                                    if page == "fl"
                                    else
                                    dmc.Select(
                                        data=[
                                            {"label": "Nonstop only", "value": "0"},
                                            {"label": "1 stop or less", "value": "1"},
                                        ],
                                        label="Stops",
                                        size="md",
                                        value="1",
                                        icon=[DashIconify(icon="ic:round-airline-stops", width=25)],
                                        id=(page + "_max_stops"),
                                    )
                                ]
                            ),
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12,
                    ),
                    # Flight Duration
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Text("Flight duration", weight=500),
                                    dmc.Slider(
                                        min=0,
                                        max=48,
                                        step=1,
                                        value=12,
                                        size="md",
                                        marks=[
                                            {"value": 12, "label": "12 hr"},
                                            {"value": 24, "label": "24 hr"},
                                            {"value": 36, "label": "36 hr"},
                                        ],
                                        id=(page + "_flight_duration")
                                    )
                                ]
                            )
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12,
                    ),
                    # Layover Duration
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.Text("Layover duration (per stop)", weight=500),
                                    dmc.Slider(
                                        min=0,
                                        max=24,
                                        step=1,
                                        value=6,
                                        size="md",
                                        marks=[
                                            {"value": 6, "label": "6 hr"},
                                            {"value": 12, "label": "12 hr"},
                                            {"value": 18, "label": "18 hr"},
                                        ],
                                        id=(page + "_layover_duration")
                                    )
                                ]
                            )
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12,
                    )
                ],
            ),
            dmc.Divider(
                variant="solid",
                style={
                    "marginTop": "40px",
                    "marginBottom": "30px"
                }
            )
        ],
        pl=0,
        pr=0
    )


def create_appshell(nav_data):
    return dmc.MantineProvider(
        [
            create_header(),
            create_navbar(),
            html.Div(
                [
                    dmc.Container(
                        page_container,
                        pt=90,
                        pl=5,
                        pr=5
                    ),
                ],
                id="wrapper"
            )
        ],
        theme={
            "fontFamily": "Roboto, sans-serif",
            "breakpoints": {
                "xs": 0,
                "sm": 576,
                "md": 768,
                "lg": 992,
                "xl": 1200
            }
        },
        withGlobalStyles=True,
        withNormalizeCSS=True
    )
