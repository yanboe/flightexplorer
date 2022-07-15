import plotly.express as px
from layout.utils import create_figure


def create_scatter(df, kpi_x, kpi_y):
    df = df.drop(["rating", "kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"], axis=1)
    return create_figure()
