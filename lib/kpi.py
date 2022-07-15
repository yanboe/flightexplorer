import pandas as pd


def get_unweighted_kpi(df_odp):
    # TODO: KPIs for General Airport Performance
    kpi1 = df_odp.groupby(["f1_airport_from"])["f1_airport_from"].count(). \
        reset_index(name="kpi1").set_index("f1_airport_from")
    kpi2 = df_odp.groupby(["f1_airport_from"])["f1_airport_from"].count(). \
        reset_index(name="kpi2").set_index("f1_airport_from")
    kpi3 = df_odp.groupby(["f1_airport_from"])["f1_airport_from"].count(). \
        reset_index(name="kpi3").set_index("f1_airport_from")

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

    df_kpi = pd.concat([kpi1, kpi2, kpi3, kpi4, kpi5, kpi6, kpi7, kpi8], axis=1).reset_index()
    df_kpi = df_kpi.rename(columns={"f1_airport_from": "airport"})

    return df_kpi


def get_weighted_kpi(df, preference):
    """
    This function returns a dataframe with weighted KPIs. The KPIs are rescaled (min-max) to a range of [0, 10].
    If no preference is selected, every normalized value is multiplied by a weight of 10 (8 * 10 = 80).
    If a preference is selected, the respective normalized value is multiplied by a weight of 30. The remaining
    normalized values are multiplied by a weight of 50 / 7 (30 + 7 * (50/7) = 80).
    """

    # Determine the weight per KPI
    if preference == "NA":
        factor = 10
    else:
        factor = 50 / 7

    # To distinguish between preferential and non-preferential indicators
    calc_max = ["kpi1", "kpi2", "kpi3", "kpi4", "kpi5"]

    # Iterate over all columns to calculate the weighted KPI
    for column in df:
        if column == "airport":
            continue
        # KPI with preference
        elif column == preference:
            if column in calc_max:
                df[(column + "_weighted")] = ((df[column] - df[column].min(skipna=True))
                                              / (df[column].max(skipna=True) - df[column].min(skipna=True))
                                              ) * 30
            else:
                df[(column + "_weighted")] = (1 - (df[column] - df[column].min(skipna=True))
                                              / (df[column].max(skipna=True) - df[column].min(skipna=True))
                                              ) * 30
        # KPI without preference
        else:
            if column in calc_max:
                df[(column + "_weighted")] = ((df[column] - df[column].min(skipna=True))
                                              / (df[column].max(skipna=True) - df[column].min(skipna=True))
                                              ) * factor
            else:
                df[(column + "_weighted")] = (1 - (df[column] - df[column].min(skipna=True))
                                              / (df[column].max(skipna=True) - df[column].min(skipna=True))
                                              ) * factor

    # Total rating
    df["rating"] = df[["kpi1_weighted", "kpi2_weighted", "kpi3_weighted", "kpi4_weighted",
                       "kpi5_weighted", "kpi6_weighted", "kpi7_weighted", "kpi8_weighted"]].sum(axis=1) / 8

    return df
