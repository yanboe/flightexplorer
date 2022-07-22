import plotly.graph_objects as go

kpi_config = {
    "kpi1": {
        "xaxis_title": "# of Flights (GAP)",
        "format": "",
        "suffix": ""
    },
    "kpi2": {
        "xaxis_title": "# of Airlines (GAP)",
        "format": "",
        "suffix": ""
    },
    "kpi3": {
        "xaxis_title": "# of Destinations",
        "format": "",
        "suffix": ""
    },
    "kpi4": {
        "xaxis_title": "# of Flights (ODP)",
        "format": "",
        "suffix": ""
    },
    "kpi5": {
        "xaxis_title": "# of Airlines (ODP)",
        "format": "",
        "suffix": ""
    },
    "kpi6": {
        "xaxis_title": "Average Flight Duration",
        "format": ".2f",
        "suffix": " hr"
    },
    "kpi7": {
        "xaxis_title": "Average # of Stops",
        "format": ".2f",
        "suffix": ""
    },
    "kpi8": {
        "xaxis_title": "Average Layover Duration",
        "format": ".2f",
        "suffix": " hr"
    }
}


def create_viz_bar(df, kpi):
    if kpi == "kpi6" or kpi == "kpi8":
        df[kpi] = df[kpi] / 3600

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df[kpi],
            y=df.airport,
            orientation="h",
            marker={
                "color": "#228be6"
            },
            customdata=df.airport_name,
            hovertemplate=(
                "<b>%{customdata}</b><br><br>" +
                kpi_config[kpi]["xaxis_title"] +
                format_value(kpi_config[kpi]["format"]) +
                kpi_config[kpi]["suffix"]
            )
        )
    )
    fig.add_vline(
        x=df[kpi].mean(),
        line_dash="dot",
        line_color="red",
        annotation={
            "text": "Average: " + str(f"{df[kpi].mean():.2f}") + kpi_config[kpi]["suffix"],
            "font": {
                "family": "Roboto, sans-serif",
                "size": 14,
                "color": "red"
            },
        },
        annotation_position="bottom right"
    )
    fig.update_xaxes(
        ticksuffix=kpi_config[kpi]["suffix"]
    )
    fig.update_yaxes(
        categoryorder="total ascending"
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
            "title": kpi_config[kpi]["xaxis_title"],
            "showgrid": True,
            "zeroline": True,
            "linecolor": "#868e96",
            "ticks": "outside",
            "tickcolor": "#868e96",
            "gridcolor": "#868e96"
        },
        yaxis={
            "title": None,
            "showgrid": False,
            "zeroline": True,
            "linecolor": "#868e96",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        modebar_orientation="v"
    )

    return fig


def format_value(f):
    """
    Formats the hover text depending on the requested format (e.g. 1003 or 1003.54)
    """
    if f == ".2f":
        return ": %{x:.2f}<extra></extra>"
    else:
        return ": %{x}<extra></extra>"
