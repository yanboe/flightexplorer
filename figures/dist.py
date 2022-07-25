import plotly.graph_objects as go
import scipy.stats as stats
import pandas as pd

from config.kpi_config import kpi_config


def create_dist(df, kpi):
    fig = go.Figure()
    if kpi == "all":
        # Normalize values
        columns = ["kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"]
        np_z = stats.zscore(df[columns])
        df_z = pd.DataFrame(data=np_z, columns=columns)

        # Add trace per indicator
        for kpi_ in kpi_config:
            fig.add_trace(
                go.Box(
                    y=df_z[kpi_],
                    name=kpi_config[kpi_]["xaxis_title"]
                ),
            )
    else:
        fig.add_trace(
            go.Box(
                y=df[kpi],
                marker={
                    "color": "#228be6"
                },
                name=kpi_config[kpi]["xaxis_title"],
            )
        )
    fig.update_layout(
        margin={"r": 0, "t": 20, "l": 0, "b": 20},
        autosize=True,
        font={
            "family": "Roboto, sans-serif",
            "size": 14,
        },
        hoverlabel={
            "bgcolor": "white"
        },
        xaxis={
            "showgrid": True,
            "zeroline": True,
            "tickangle": -45 if kpi == "all" else None,
        },
        yaxis={
            "title": "z-Score" if kpi == "all" else None,
            "autorange": True,
            "showgrid": True,
            "zeroline": True,
            "linecolor": "#868e96",
            "ticks": "outside",
            "tickcolor": "#868e96",
            "gridcolor": "#868e96",
            "zerolinecolor": "#868e96",
            "zerolinewidth": 1
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    return fig
