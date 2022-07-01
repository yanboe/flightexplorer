import dash
from dash import html

dash.register_page(
    __name__,
    "/",
    title="Test",
    description="Test"
)

layout = html.Div("Hello")
