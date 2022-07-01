import dash_mantine_components as dmc
from dash import Input, Output, html, dcc, page_container
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
                                dcc.Link(
                                    [
                                        dmc.MediaQuery(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.ThemeIcon(
                                                            DashIconify(
                                                                icon="cil:airplane-mode",
                                                                width=22
                                                            ),
                                                            radius=30,
                                                            size=36,
                                                            variant="light",
                                                            color="indigo"
                                                        ),
                                                        dmc.Text("Flight Planner", size="xl", color="gray"),
                                                    ]
                                                )
                                            ],
                                            smallerThan="sm",
                                            styles={"display": "none"},
                                        ),
                                        dmc.MediaQuery(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.ThemeIcon(
                                                            DashIconify(
                                                                icon="cil:airplane-mode",
                                                                width=22
                                                            ),
                                                            radius=30,
                                                            size=36,
                                                            variant="light",
                                                            color="indigo"
                                                        ),
                                                        dmc.Text("Flight Planner", size="xl", color="gray"),
                                                    ]
                                                )
                                            ],
                                            largerThan="sm",
                                            styles={"display": "none"},
                                        ),
                                    ],
                                    href="#",
                                    style={"paddingTop": 5, "textDecoration": "none"},
                                ),
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
                                        href="#",
                                    ),
                                    html.A(
                                        dmc.Tooltip(
                                            dmc.ThemeIcon(
                                                DashIconify(
                                                    icon="bi:discord",
                                                    width=22,
                                                ),
                                                radius=30,
                                                size=36,
                                                variant="outline",
                                            ),
                                            label="Discord",
                                            position="bottom",
                                        ),
                                        href="#",
                                    ),
                                ],
                                position="right",
                                align="center",
                                spacing="xl",
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
        # fixed=True,
        p="md",
    )


def create_form():
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
                                        icon=[DashIconify(icon="clarity:map-marker-line", width=25)],
                                        limit=10,
                                        placeholder="Where from?",
                                        size="lg",
                                        maxDropdownHeight=500,
                                        id="airport_from"
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
                                        icon=[DashIconify(icon="clarity:map-marker-line", width=25)],
                                        limit=10,
                                        placeholder="Where to?",
                                        size="lg",
                                        maxDropdownHeight=500,
                                        id="airport_to"
                                    )
                                ]
                            ),
                        ],
                        lg=4,
                        md=4,
                        sm=6,
                        xs=12
                    ),
                    # DatePicker
                    dmc.Col(
                        [
                            html.Div(
                                [
                                    dmc.DatePicker(
                                        minDate=date(2019, 1, 1),
                                        maxDate=date(2022, 3, 31),
                                        value=date(2019, 6, 11),
                                        inputFormat="MMM D, YYYY",
                                        icon=[DashIconify(icon="clarity:date-line", width=25)],
                                        amountOfMonths=2,
                                        size="lg",
                                        clearable=False,
                                        id="datepicker"
                                    )
                                ]
                            ),
                        ],
                        lg=4,
                        md=4,
                        sm=12,
                        xs=12
                    ),
                    # Departure Time
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
                                        icon=[DashIconify(icon="akar-icons:clock", width=25)],
                                        id="dep_time"
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
                                        icon=[DashIconify(icon="ic:round-connecting-airports", width=25)],
                                        id="max_stops",
                                    )
                                ]
                            ),
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12
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
                                        id="flight_duration"
                                    )
                                ]
                            )
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12
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
                                        id="layover_duration"
                                    )
                                ]
                            )
                        ],
                        lg=6,
                        md=6,
                        sm=6,
                        xs=12
                    )
                ],
            ),
            dmc.Divider(
                variant="solid",
                style={
                    "marginTop": "30px",
                    "marginBottom": "30px"
                }
            )
        ],
        mt="30px"
    )


def create_appshell(nav_data):
    return dmc.MantineProvider(
        [
            create_header(),
            create_form(),
            dcc.Location(id="url"),
            html.Div(
                [
                    dmc.Container(
                        [
                            page_container
                        ],
                    )
                ],
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

