import altair as alt
import pandas as pd
import streamlit as st

from analysis.accessors import DType
from analysis.data import _ewm_data, _ewm_draw

# Functions


@st.cache_data
def process_csv(csv, dateformat="ISO"):
    df = pd.read_csv(csv, header=0, names=["date", "volume"])

    kw = dateformats[dateformat][1]
    df["date"] = pd.to_datetime(df["date"], **kw)
    return df.astype({"volume": DType.U16})


@st.cache_data
def serialize_df(df):
    return df.to_csv()


def filter_and_plot_data(df, start, end, windows, show_daily=True):
    # provided dates from widget are datetime.date instances
    # pandas only plays ball with datetime.datetime instances or strings
    mask = (df.date >= start.isoformat()) & (df.date <= end.isoformat())
    selected = df.loc[mask]

    daily = df.groupby("date", as_index=False)["volume"].sum()
    data = _ewm_data(daily, windows, "volume")
    data = data.loc[data.date.isin(selected.date)]
    chart = _ewm_draw(data, "volume", show_daily=show_daily)
    data = data.pivot_table(values="value", index="date", columns="window").reindex()
    chart.height = 500
    return (chart, data)


def reset_date(name, value):
    st.session_state[name] = value


def compare_metric(compare, window, label):
    before = compare.at[0, str(window)]
    after = compare.at[1, str(window)]
    return st.metric(f"{label} Volume ({window} days)", after, after - before)


# App
st.set_page_config(
    page_title="Volume Analysis",
    page_icon="📊",
    layout="wide",
)
st.title("Toms Volume analyser")
auth = st.empty()
help = st.container()
data_sidebar = st.sidebar.container()
data_info = st.expander("Data statistics")
display_selectors = st.container()
chart_display = st.container()

# authentication
# auth.text_input("Activation Code", key="auth_code")

# if "auth_code" not in st.session_state:
#     st.session_state["auth_code"] = "1"

# with auth:
#     # code = st.text_input("Activation Code", key="auth_code")
#     if st.session_state.auth_code == "":
#         st.stop()
#     if st.session_state.auth_code != st.secrets["auth_code"]:
#         st.error("Access Denied")
#         del st.session_state.auth_code
#         st.rerun()
#     st.success("Access Granted")


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

with data_info:
    left, right = st.columns(2)
    left.table(df["volume"].describe())
    # right.table(df.head())


with display_selectors:
    st.header("Chart Controls")
    date_min = df.date.min().date()
    date_max = df.date.max().date()
    dates = st.slider(
        "Choose start and end dates",
        date_min,
        date_max,
        (date_min, date_max),
    )
    daily_toggle = st.checkbox("Daily Volumes")
    # windows = st.selectbox("Average Windows", [(10, 30, 90), (7, 28, 112)])

with chart_display:
    st.header("EWM Average Volume Data")
    chart, data = filter_and_plot_data(
        df, dates[0], dates[1], windows=(10, 30, 90), show_daily=daily_toggle
    )
    compare = data.take([0, -1]).reset_index()

    _cols = st.columns(3)
    with _cols[0]:
        compare_metric(compare, 10, "Acute")
    with _cols[1]:
        compare_metric(compare, 30, "Chronic")
    with _cols[2]:
        compare_metric(compare, 90, "Baseline")

    st.altair_chart(chart, use_container_width=True)

    st.dataframe(data)
    data_download = st.download_button(
        "Download charted data",
        serialize_df(data),
        file_name="volumes.csv",
        mime="text/csv",
    )
