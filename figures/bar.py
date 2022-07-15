import plotly.graph_objects as go

from dash import dcc

config = {
    "staticPlot": True
}


def create_bar(row, df_prev):

    # Create dataframe with values of comparative period
    dff_prev = df_prev.loc[df_prev["airport"] == row.airport]
    if dff_prev.empty:
        prev_hline = 0
    else:
        prev_hline = dff_prev.iloc[0]["rating"]

    dff_prev = dff_prev.drop(
        [
            "airport", "rating",
            "kpi1", "kpi2", "kpi3", "kpi4",
            "kpi5", "kpi6", "kpi7", "kpi8"
        ],
        axis=1)
    dff_prev_t = dff_prev.T.reset_index()
    df_p = dff_prev_t.set_axis(["theta", "r"], axis=1).reset_index(drop=True)

    # Create dataframe with values of selected period
    dff_sel = row.drop(["kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"])
    dff_sel_t = dff_sel.T
    dff_sel_t = dff_sel_t.drop(["airport", "rating"]).reset_index()
    df_s = dff_sel_t.set_axis(["theta", "r"], axis=1).reset_index(drop=True)

    kpi = [
        "Flights (GAP)", "Airlines (GAP)", "Destinations (GAP)", "Flights (ODP)",
        "Airlines (ODP)", "Flight Duration (ODP)", "Stops (ODP)", "Layover Time (ODP)"
    ]

    # annotation position of hline so they don't overlap
    if row.rating >= prev_hline:
        ann_pos_sel = "top right"
        ann_pos_prev = "bottom right"
    else:
        ann_pos_sel = "bottom right"
        ann_pos_prev = "top right"

    fig = go.Figure()

    # Selected period
    fig.add_trace(
        go.Bar(
            x=kpi,
            y=df_s["r"],
            name="Selected period",
            marker={
                "color": "#228be6"
            }
        )
    )
    fig.add_hline(
        y=row.rating,
        line_dash="dot",
        annotation={
            "text": "Rating (selected period)",
            "font": {
                "family": "Roboto, sans-serif",
                "size": 14
            },
        },
        annotation_position=ann_pos_sel
    )

    # Previous period
    fig.add_trace(
        go.Bar(
            x=kpi,
            y=df_p["r"],
            name="Previous period",
            marker={
                "color": "#ced4da"
            }
        )
    )
    fig.add_hline(
        y=prev_hline,
        line_dash="dot",
        annotation={
            "text": "Rating (previous period)",
            "font": {
                "family": "Roboto, sans-serif",
                "size": 14
            },
        },
        annotation_position=ann_pos_prev

    )
    fig.update_layout(
        margin={"r": 0, "t": 20, "l": 0, "b": 20},
        autosize=True,
        font={
            "family": "Roboto, sans-serif",
            "size": 14,
        },
        xaxis={
            "tickangle": -45,
            "showgrid": False,
            "zeroline": True,
            "linecolor": "#868e96",
        },
        yaxis={
            "title": "Score",
            "range": [0, 10],
            "showgrid": False,
            "zeroline": True,
            "linecolor": "#868e96",
            "ticks": "outside",
            "tickcolor": "#868e96"
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.05,
            "xanchor": "left",
            "x": 0
        },
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return dcc.Graph(figure=fig, config=config)
