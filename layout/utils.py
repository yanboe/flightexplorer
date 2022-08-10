import dash_mantine_components as dmc
import plotly.graph_objects as go
import random


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


def create_kpi(title, row, df, airport, kpi):
    # KPI value of selected period
    value = row[(kpi + "_weighted")]
    absolute_value = ("Absolute Value: " + f"{row[kpi]:.2f}")

    # KPI value of previous period
    df = df.set_index("airport")
    value_prev = df.loc[airport][(kpi + "_weighted")]

    # Calculate difference and format it with +/- sign (e.g. 3.13 -> +3.13)
    diff = create_display_diff(value, value_prev)

    return dmc.Col(
        [
            dmc.Tooltip(
                [
                    dmc.Text(title, color="dimmed", size="xs", style={"lineHeight": 1.3}),
                    dmc.Text(f"{value:.2f}", weight=500, style={"fontSize": 24, "lineHeight": 1.3}),
                    dmc.Text(
                        ("Previous period: ", f"{value_prev:.2f}", diff),
                        size="xs",
                        color="dimmed",
                        style={"lineHeight": 1.3}
                    )
                ],
                label=absolute_value,
                withArrow=True,
                arrowSize=3
            )
        ],
        lg=3,
        md=3,
        sm=4,
        xs=6,
        style={
            "marginBottom": 10
        }
    )


def create_display_diff(now, prev):
    # Calculate difference and format it with +/- sign (e.g. 3.13 -> +3.13)
    diff = now - prev
    if diff == 0:
        return f" ({diff:+})"
    else:
        return f" ({diff:+.2f})"


def create_period_selector(viz_id):
    return dmc.Chips(
        data=[
            {"label": "Selected Period", "value": "sp"},
            {"label": "Previous Period", "value": "pp"},
        ],
        radius="xl",
        size="sm",
        value="sp",
        id=viz_id
    )