import random

from dash import dcc
import dash_mantine_components as dmc
import plotly.graph_objects as go


def create_figure():
    return go.Figure(
        {
            "data": [
                go.Bar(
                    x=list(range(10)),
                    y=[random.randint(200, 1000) for _ in range(10)],
                    name="SF",
                    marker={"line": {"width": 0}},
                    marker_color=dmc.theme.DEFAULT_COLORS["gray"][4],
                ),
                go.Bar(
                    x=list(range(10)),
                    y=[random.randint(200, 1000) for _ in range(10)],
                    name=u"Montréal",
                    marker={"line": {"width": 0}},
                    marker_color=dmc.theme.DEFAULT_COLORS["indigo"][4],
                ),
            ],
            "layout": go.Layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis={"showgrid": False, "zeroline": False, "visible": False},
                yaxis={"showgrid": False, "zeroline": False, "visible": False},
                showlegend=False,
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
            ),
        }
    )


def create_graph_dummy(graph_id):
    return dmc.Paper(
        [
            dmc.Text(id=("fi_graph_title_" + str(graph_id)), style={"fontSize": 30, "fontWeight": 400}),
            dcc.Graph(figure=create_figure(), id=("fi_graph_" + str(graph_id)), responsive=True),
        ],
        p="xl",
        radius="sm",
        withBorder=True,
        mb=15
    )
