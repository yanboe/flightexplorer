import plotly.express as px


kpi = [
    "Flights (GAP)", "Airlines (GAP)", "Destinations", "Flights (ODP)",
    "Airlines (ODP)", "Flight Duration", "Stops", "Layover Time"
]


def create_heatmap(df):
    df = df.set_index("airport")

    # Create customdata
    airport_names = [df.airport_name for i in range(8)]
    customdata = list(map(list, zip(*airport_names)))

    fig = px.imshow(
        df[["kpi1_weighted", "kpi2_weighted", "kpi3_weighted", "kpi4_weighted",
            "kpi5_weighted", "kpi6_weighted", "kpi7_weighted", "kpi8_weighted"]],
        x=kpi,
        text_auto=".2f",
        aspect="auto",
        labels={
            "x": "Indicator",
            "y": "Airport",
            "color": "Rating"
        }
    )
    fig.update_traces(
        customdata=customdata,
        hovertemplate=
        "<b>%{customdata}</b><br><br>" +
        "Indicator: %{x}<br>" +
        "Rating: %{z:.2f}<extra></extra>"
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

    return fig
