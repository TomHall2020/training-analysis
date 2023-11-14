import altair as alt

EWM_COLORS = {
    "daily": "#888",
    7: "#e68",
    10: "#e68",
    28: "#6bd",
    30: "#6bd",
    90: "#bd2",
    112: "#bd2",
}


def map_scale(mapping, **kwargs):
    return alt.Scale(
        domain=list(mapping.keys()), range=list(mapping.values()), **kwargs
    )


def _ewm_data(df, windows, metric, start_value=None):
    if start_value:
        df = df.copy()
        df.at[0, metric] = start_value
    ewms = df.vol.ewm_multi(df[metric], windows)

    return (
        ewms.round()
        .astype(int)
        .join(df[[metric, "date"]])
        .melt(id_vars="date", var_name="window")
    )


def _ewm_draw(data, metric, custom_color_scale=False, show_daily=True):
    # view = alt.selection_interval(encodings=["x"], bind="scales")
    base = (
        alt.Chart(data, title=f"Average {metric}", width=500).encode(
            x=alt.X("yearmonthdate(date):T", axis=alt.Axis(grid=False), title="Date"),
            y=alt.Y("value:Q", title=metric),
        )
        # .add_params(view)
    )

    volumes = (
        base.transform_filter(f"datum.window == '{metric}'")
        .mark_rule(opacity=0.5, color=EWM_COLORS["daily"])
        .encode(
            tooltip=["date:T", "value:Q"],
        )
    )

    if custom_color_scale:
        scale = map_scale(custom_color_scale)
    else:
        scale = alt.Scale(scheme="set1")
    averages = (
        base.transform_filter(f"datum.window != '{metric}'")
        .mark_line()
        .encode(
            color=alt.Color("window:N", scale=scale).legend(orient="top"),
            tooltip=["date:T", "window:O", "value:Q"],
        )
    )
    if show_daily:
        chart = volumes + averages
    else:
        chart = averages
    # chart.usermeta = dict(averages=averages, volumes=volumes)
    return chart


def ewm_plot(df, windows=(7, 28, 112), metric="volume", start_value=None, vcs=False):
    daily = df.groupby("date", as_index=False)[metric].sum()
    data = _ewm_data(daily, windows, metric, start_value)
    chart = _ewm_draw(data, metric, custom_color_scale=vcs)
    return chart
