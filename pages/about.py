import dash
import dash_mantine_components as dmc

from dash import html

layout = dmc.Container(
    [
        dmc.Center(
            [
                dmc.Group(
                    [
                        html.A(
                            [
                                dmc.Tooltip(
                                    [
                                        dmc.Avatar(
                                            [

                                            ],
                                            size="xl",
                                            radius="md"
                                        ),
                                    ],
                                    label="View profile on GitHub",
                                    position="bottom",
                                    withArrow=True,
                                    arrowSize=3
                                )
                            ],
                            href="https://github.com/yanboe/",
                            target="_blank"
                        ),
                        html.Div(
                            [
                                dmc.Text("Software Engineer & Master's Student", size="xs", transform="uppercase", weight=700, color="dimmed"),
                                dmc.Text("Yannik Böni", size="lg", weight=500),
                                dmc.Text("yannik.boeni@stud.fhgr.ch", size="xs", color="dimmed"),
                            ]
                        )
                    ],
                    position="center",
                    direction="row",
                    noWrap=True
                )
            ],
        )
    ],
    pl=0,
    pr=0
)

dash.register_page(
    __name__,
    path="/about/",
    title="About | Airport Explorer",
    description="About Airport Explorer",
    layout=layout
)
