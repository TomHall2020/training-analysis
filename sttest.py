import pandas as pd
import streamlit as st
from analysis.accessors import DType
from analysis.data import EWM_COLORS, _ewm_data, _ewm_draw, ewm_plot

# Functions


@st.cache_data
def process_csv(csv, dateformat="ISO"):
    df = pd.read_csv(csv, header=0, names=["date", "volume"])

    kw = dateformats[dateformat][1]
    df["date"] = pd.to_datetime(df["date"], **kw)
    return df.astype({"volume": DType.U16})


def filter_and_plot_data(df, start, end, windows):
    # provided dates from widget are datetime.date instances
    # pandas only plays ball with datetime.datetime instances or strings
    mask = (df.date >= start.isoformat()) & (df.date <= end.isoformat())
    selected = df.loc[mask]

    daily = df.groupby("date", as_index=False)["volume"].sum()
    data = _ewm_data(daily, windows, "volume")
    chart = _ewm_draw(data.loc[data.date.isin(selected.date)], "volume")

    chart.width = 800
    chart.height = 500
    return chart


def reset_date(name, value):
    st.session_state[name] = value


# App
st.set_page_config(
    page_title="Volume Analysis",
    page_icon="📊",
    layout="wide",
)
st.title("Toms Volume analyser")
help = st.container()
data_sidebar = st.sidebar.container()
data_info = st.expander("Data statistics")
display_selectors = st.container()
chart_display = st.container()

with help:
    st.markdown(
        """
    To use, simply upload a csv file of your volumes with two columns, date and volume.
    eg:
    ```csv
    date,volume
    20/10/2016,200
    21/10/2016,100
    ```
    """
    )

dateformats = {
    "ISO": ("YYYY-MM-DD", dict(format="ISO8601")),
    "Day first": ("DD/MM/YYYY", dict(dayfirst=True)),
    "Month first": ("MM/DD/YYYY", dict(dayfirst=False)),
}
with data_sidebar:
    st.header("Data Input")
    with st.form(key="data-input"):
        csv = st.file_uploader("Upload volume csv file here", type=".csv", key="csv")
        datefmt = st.selectbox(
            "Choose a date format",
            [*dateformats.keys()],
            format_func=lambda option: f"{option} ({dateformats[option][0]})",
            index=1,
            key="datefmt",
        )
        st.form_submit_button("Analyse")
if csv:
    st.session_state["df"] = df = process_csv(csv, st.session_state.datefmt)
else:
    st.session_state["df"] = df = process_csv("data/Training_Vol18-19.csv", datefmt)

# with st.expander("Data statistics"):
with data_info:
    left, right = st.columns(2)
    left.dataframe(df["volume"].describe())
    right.dataframe(df.head())


# date filters


with display_selectors:
    date_min = df.date.min().date()
    date_max = df.date.max().date()
    dates = st.slider(
        "Choose start and end dates",
        date_min,
        date_max,
        (date_min, date_max),
    )
    # windows = st.selectbox("Average Windows", [(10, 30, 90), (7, 28, 112)])

with chart_display:
    chart = filter_and_plot_data(df, dates[0], dates[1], windows=(10, 30, 90))
    st.altair_chart(chart)
