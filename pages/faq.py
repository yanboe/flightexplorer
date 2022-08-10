import dash
import dash_mantine_components as dmc

from dash import html

layout = dmc.Container(
    [
        dmc.Container(
            [
                dmc.Text("Frequently Asked Questions", style={"fontSize": 26}),
            ],
            px=0,
            style={"marginBottom": 20}
        ),
        dmc.Container(
            [
                dmc.Accordion(
                    [
                        dmc.AccordionItem(
                            label="What is this about?",
                            children=[
                                dmc.Container(
                                    [
                                        dmc.Text("Coming soon")
                                    ],
                                    mt=20
                                ),
                            ]
                        ),
                        dmc.AccordionItem(
                            label="What data is used for this app?",
                            children=[
                                dmc.Container(
                                    [
                                        dmc.Text("Flight Data Source", style={"fontSize": 22}),
                                        html.P(
                                            [
                                                'Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic and '
                                                'Matthias Wilhelm. "Bringing Up OpenSky: A Large-scale ADS-B Sensor Network '
                                                'for Research". In ',
                                                html.I(
                                                    "Proceedings of the 13th IEEE/ACM International Symposium on Information "
                                                    "Processing in Sensor Networks (IPSN),"
                                                ),
                                                " pages 83-94, April 2014. ",
                                                dmc.Space(h=10),
                                                html.I("The OpenSky Network, "),
                                                html.A(
                                                    "https://opensky-network.org/",
                                                    href="https://opensky-network.org/",
                                                    target="_blank",
                                                    style={
                                                        "textDecoration": "none",
                                                        "color": "#1c7ed6",
                                                        "fontStyle": "italic"
                                                    }
                                                )
                                            ],
                                        ),
                                        dmc.Text("Flight Processing Library", style={"fontSize": 22}),
                                        html.P(
                                            [
                                                'Xavier Olive. "Traffic, a toolbox for processing and analysing '
                                                'air traffic data." ',
                                                html.I("Journal of Open Source Software"),
                                                " 4(39), July 2019."
                                            ]
                                        ),
                                        dmc.Text("Airport, Region and Country Data", style={"fontSize": 22}),
                                        html.P(
                                            [
                                                "The airport, region and country data is provided by ",
                                                html.A(
                                                    "OurAirports",
                                                    href="https://ourairports.com/data/",
                                                    target="_blank",
                                                    style={
                                                        "textDecoration": "none",
                                                        "color": "#1c7ed6",
                                                    }
                                                ),
                                                "."
                                            ]
                                        )
                                    ],
                                    mt=20
                                )
                            ],
                        ),
                    ],
                    multiple=True,
                    offsetIcon=False
                )
            ],
            px=0
        )
    ],
    pl=0,
    pr=0
)

dash.register_page(
    __name__,
    path="/faq/",
    title="FAQ | Airport Explorer",
    description="Frequently Asked Questions about Airport Explorer",
    layout=layout
)
