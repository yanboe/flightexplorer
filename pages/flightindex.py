import dash
import dash_mantine_components as dmc
from dash import html, callback, Input, Output

from lib.appshell import create_form


page_content = dmc.Container(
    dmc.LoadingOverlay(
        [
            html.Div(id="page-content"),
        ],
        loaderProps={"variant": "oval", "color": "blue", "size": "xl"},
    )
)
layout = [create_form(), page_content]

dash.register_page(
    __name__,
    path="/flightindex/",
    name="Flight Index",
    title="Flight Index",
    layout=layout
)
