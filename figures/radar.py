import warnings
import plotly.express as px

from dash import dcc
warnings.simplefilter(action="ignore", category=FutureWarning)

config = {
    "staticPlot": True
}


def create_radar(row):
    # Drop unweighted parameters
    row = row.drop(["time",
                    "kpi1_unweighted", "kpi2_unweighted", "kpi3_unweighted", "kpi4_unweighted",
                    "kpi5_unweighted", "kpi6_unweighted", "kpi7_unweighted", "kpi8_unweighted"])

    # Transpose row
    df_transposed = row.T.reset_index()
    df_transposed = df_transposed.drop([0, 1])
    df = df_transposed.set_axis(["theta", "r"], axis=1).reset_index(drop=True)

    theta = [
        "Flights (GAP)", "Airlines (GAP)", "Destinations (GAP)", "Flights (ODP)",
        "Airlines (ODP)", "Flight Duration (ODP)", "Stops (ODP)", "Layover Time (ODP)"
    ]

    fig = px.line_polar(
        df,
        r="r",
        theta=theta,
        line_close=True,
        range_r=[0, 10]
    )
    fig.update_traces(
        fill="toself",
        fillcolor="rgba(34, 139, 230, 0.5)",
        line={"color": "rgb(34, 139, 230)"}
    )
    fig.update_layout(
        margin={"r": 80, "t": 20, "l": 80, "b": 20},
        autosize=True,
        modebar={
            "orientation": "v"
        },
    )
    fig.update_polars(
        bgcolor="#dee2e6",
        angularaxis={
            "tickfont": {
                "family": "Roboto, sans-serif",
                "size": 14
            },
        },
        radialaxis={
            "angle": 90,
            "dtick": 1,
            "tick0": 1,
            "ticklabelstep": 2,
            "tickangle": 90,
            "tickfont": {
                "family": "Roboto, sans-serif",
                "size": 14
            },
        },
        gridshape="linear"
    )
    return dcc.Graph(figure=fig, config=config)
