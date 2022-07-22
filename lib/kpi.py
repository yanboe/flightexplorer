import pandas as pd
from sklearn.preprocessing import QuantileTransformer
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def get_unweighted_kpi(df_odp, df_gap):

    # KPIs for Origin-to-Destination Performance
    kpi4 = df_odp.groupby(["f1_airport_from"])["f1_airport_from"].count().\
        reset_index(name="kpi4").set_index("f1_airport_from")
    kpi5 = df_odp.groupby(["f1_airport_from"])["f1_airline_code"].nunique().\
        reset_index(name="kpi5").set_index("f1_airport_from")
    kpi6 = df_odp.groupby(["f1_airport_from"])["total_duration_s"].mean().\
        reset_index(name="kpi6").set_index("f1_airport_from")
    kpi7 = df_odp.groupby(["f1_airport_from"])["stop_count"].mean().\
        reset_index(name="kpi7").set_index("f1_airport_from")
    kpi8 = df_odp.groupby(["f1_airport_from"])["layover_duration_1_s"].mean().\
        reset_index(name="kpi8").set_index("f1_airport_from")

    # Concat GAP and ODP KPIs
    df_kpi = pd.concat([df_gap, kpi4, kpi5, kpi6, kpi7, kpi8], axis=1).reset_index()
    df_kpi = df_kpi.rename(columns={"f1_airport_from": "airport"})

    # Drop rows that only have GAP KPIs
    df_kpi = df_kpi.dropna(subset=["kpi4", "kpi5", "kpi6", "kpi7"])
    df_kpi["kpi8"] = df_kpi["kpi8"].fillna(0)

    return df_kpi


def get_weighted_kpi(df_unweighted, preference):

    df = df_unweighted.copy()
    df = df.set_index("airport")

    transformer = QuantileTransformer(output_distribution="uniform")
    df_norm = pd.DataFrame(
        transformer.fit_transform(df),
        columns=["kpi1", "kpi2", "kpi3", "kpi4", "kpi5", "kpi6", "kpi7", "kpi8"]
    )

    # switch cost indicators
    df_norm["kpi6"] = 1 - df_norm["kpi6"]
    df_norm["kpi7"] = 1 - df_norm["kpi7"]
    df_norm["kpi8"] = 1 - df_norm["kpi8"]

    # Determine the weight per KPI
    if preference == "NA":
        weight = 0.125
    else:
        weight = 0.8 / 7

    # compute weighted KPIs
    df_weighted = pd.DataFrame()
    for column in df_norm:
        if column == preference:
            df_weighted[(column + "_weighted")] = df_norm[column] * 0.2
        else:
            df_weighted[(column + "_weighted")] = df_norm[column] * weight

    # create rating sum
    df_rating = pd.DataFrame()
    df_rating["rating"] = df_weighted.sum(axis=1) * 10

    # scaling so highest value is always 10
    x = 100 / 2
    if preference == "NA":
        df_weighted = df_weighted * 80
    else:
        df_weighted = df_weighted * x

    # copy rating sum
    df_weighted["rating"] = df_rating["rating"]

    df = df.reset_index()
    df_final = pd.concat([df, df_weighted], axis=1)

    return df_final
