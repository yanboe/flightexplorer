import dash_mantine_components as dmc
import numpy as np
import plotly.express as px
from dash import dcc

kpi = [
    "Flights (GAP)", "Airlines (GAP)", "Destinations", "Flights (ODP)",
    "Airlines (ODP)", "Flight Duration", "Stops", "Layover Time"
]


def create_corr_heatmap(title, description, df):
    # Create correlation matrix
    df_corr = df[["kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"]].corr(method="pearson")

    # Remove upper triangle of the array and invert it (so we keep the diagonal correlations of 1)
    mask = np.invert(np.tril(np.ones_like(df_corr, dtype=bool)))
    df_corr = df_corr.mask(mask)

    fig = px.imshow(
        df_corr,
        x=kpi,
        y=kpi,
        text_auto=".2f",
        aspect="auto",
    )
    fig.update_traces(
        hovertemplate="%{y} vs. %{x}<extra></extra>",
        hoverongaps=False
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
            "tickangle": -45,
            "title": None
        },
        yaxis={
            "title": None
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )

    return dmc.Paper(
        [
            dmc.Text(title, weight=300, style={"fontSize": 26}),
            dmc.Text(description, color="dimmed"),
            dcc.Graph(figure=fig, id="fig_corr_heatmap"),
        ],
        p="lg",
        radius="sm",
        withBorder=True,
        mb=15
    )
