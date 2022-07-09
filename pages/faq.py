import dash
import dash_mantine_components as dmc

from dash import html

layout = html.Div(
    [
        dmc.Text("Frequently Asked Questions")
    ]
)

dash.register_page(
    __name__,
    path="/faq/",
    name="FAQ",
    title="FAQ",
    layout=layout
)
