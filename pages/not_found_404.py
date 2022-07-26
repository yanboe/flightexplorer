import dash
import dash_mantine_components as dmc

from dash import html

layout = html.Div(
    [
        dmc.Container(
            [
                dmc.Text("Error 404.", weight=500),
                dmc.Text("Sorry, we can't find this page.", color="dimmed"),
                dmc.Space(h=30),
                dmc.Anchor("Return back to home", href="/", underline=False)
            ],
            pl=0,
            pr=0
        )
    ]
)

dash.register_page(
    __name__,
    path="/404/",
    title="Error 404 (Not Found) | Airport Explorer",
    description="Error 404: Requested page not found",
    layout=layout
)
