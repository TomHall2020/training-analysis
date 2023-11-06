import pandas as pd
import streamlit as st
from analysis.accessors import DType
from analysis.data import ewm_plot

# Functions


@st.cache_data
def process_csv(csv):
    df = pd.read_csv(csv, header=0, names=["date", "volume"])
    df["date"] = pd.to_datetime(df["date"])
    return df.astype({"volume": DType.U16})


def filter_and_plot_data():
    # provided dates from widget are datetime.date instances
    # pandas only plays ball with datetime.datetime instances or strings
    mask = (df.date >= start_date.isoformat()) & (df.date <= end_date.isoformat())
    selected = df.loc[mask]

    chart = ewm_plot(selected, windows=(10, 30, 90))
    chart.width = 800
    chart.height = 500
    return chart


def reset_start_date():
    st.session_state.start_date = df.date.min()


def reset_end_date():
    st.session_state.end_date = df.date.max()


# App

st.set_page_config(
    page_title="Volume Analysis",
    page_icon="📊",
)
st.title("Toms Volume analyser")
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
csv = st.file_uploader("Upload volume csv file here", type=".csv")
if csv:
    df = process_csv(csv)
else:
    df = process_csv("data/Training_Vol18-19.csv")

st.session_state["df"] = df

with st.expander("Data statistics"):
    st.dataframe(df["volume"].describe())
    st.write(df.dtypes)

# date filters
with st.container():
    left, right = st.columns(2)
    selected = df.copy()
    start_date = left.date_input("Start Date", df.date.min(), key="start_date")
    left.button("Reset", key="reset_start", on_click=reset_start_date)
    end_date = right.date_input("End Date", df.date.max(), key="end_date")
    right.button("Reset", key="reset_end", on_click=reset_end_date)

chart = filter_and_plot_data()
st.altair_chart(chart)
# experimental section
# st.markdown("---")

# extra = st.data_editor(df.tail())

# st.altair_chart(ewm_plot(extra))
