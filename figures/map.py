import plotly.graph_objects as go
import dash_mantine_components as dmc

from dash import dcc
from os import environ

from utils.map_utils import get_map_lines, get_map_markers

MAPBOX_KEY = environ.get("MAPBOX_KEY")
MAPBOX_STYLE = environ.get("MAPBOX_STYLE")

config = {
    "displaylogo": False,
    "displayModeBar": True
}


def create_map(df_flights, df_airports):
    # Get map lines and map markers
    df_map_lines = get_map_lines(df_flights, df_airports)
    df_map_markers = get_map_markers(df_map_lines, df_airports)

    # Create map
    fig = go.Figure()
    grouped = df_map_lines.groupby("flight", sort=False)

    # Create lines (flight paths)
    for name, group in grouped:
        fig.add_trace(
            go.Scattermapbox(
                mode="lines",
                lon=group.lon,
                lat=group.lat,
                legendgrouptitle={
                    "text": "Flights",
                    "font": {
                        "family": "Roboto, sans-serif",
                        "size": 16
                    },
                },
                line={
                    "color": group.color.iloc[0]
                },
                name=name,
            )
        )

    # Create markers (airports)
    fig.add_trace(
        go.Scattermapbox(
            mode="text+markers",
            lon=df_map_markers.lon,
            lat=df_map_markers.lat,
            marker={
                "size": 8,
                "color": "grey",
            },
            hoverlabel={
                "font": {
                    "family": "Roboto, sans-serif",
                    "size": 14
                },
                "bgcolor": "white"
            },
            hoverinfo="text",
            showlegend=False,
            text=df_map_markers.index,
            textposition="middle right",
            textfont={

            }
        )
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox={
            "accesstoken": MAPBOX_KEY,
            "style": MAPBOX_STYLE,
            "zoom": 3,
            "center": {
                "lat": df_map_lines.lat.iloc[0],
                "lon": df_map_lines.lon.iloc[0]
            }
        },
        autosize=True,
        modebar={
            "orientation": "v"
        },
        legend={
            "yanchor": "top",
            "y": 0.99,
            "xanchor": "left",
            "x": 0.01
        }
    )

    return dmc.Container(
        [
            dcc.Graph(
                figure=fig,
                config=config
            )
        ],
        pt=0,
        pb=0,
        pr=0,
        pl=0,
        mb=15,
        style={
            "border": "1px solid rgb(222, 226, 230)",
            "borderRadius": "4px"
        }
    )
