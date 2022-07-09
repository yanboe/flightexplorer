import dash
from dash import html

layout = html.Div("Coming soon...")

dash.register_page(
    __name__,
    path="/about/",
    name="About",
    title="About",
    layout=layout
)
