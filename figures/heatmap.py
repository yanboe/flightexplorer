import dash_mantine_components as dmc
import plotly.express as px

from dash import dcc

config = {
    #"staticPlot": True,
}


def create_heatmap(title, description, df):
    # Drop irrelevant parameters
    df = df.drop(["rating", "kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"], axis=1)
    df = df.set_index("airport")
    df = df.rename_axis("Indicator", axis="columns")
    fig = px.imshow(
        df,
        labels={
            "x": "Indicator",
            "y": "Airport",
            "color": "Score"
        },
        x=["Flights (GAP)", "Airlines (GAP)", "Destinations (GAP)", "Flights (ODP)",
           "Airlines (ODP)", "Flight Duration (ODP)", "Stops (ODP)", "Layover Time (ODP)"],
        text_auto=True,
        aspect="auto"
    )
    fig.update_xaxes(side="bottom")
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
    )

    return dmc.Paper(
        [
            dmc.Text(title, weight=300, style={"fontSize": 26}),
            dmc.Text(description, color="dimmed"),
            dcc.Graph(figure=fig, id="fig_heatmap", config=config),
        ],
        p="lg",
        radius="sm",
        withBorder=True,
        mb=15
    )
