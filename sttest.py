import pandas as pd
import streamlit as st
from scrape_session_data import EWM_COLORS, VAULT_DIR, ewm_plot, parse_session_files


@st.cache_data
def load_rows():
    season = VAULT_DIR / "Training Log/22-23/"
    rows = parse_session_files(season.joinpath("sessions").glob("*.md"))
    return rows


def process_csv(csv):
    df = pd.read_csv(csv, header=0, names=["date", "volume"])
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")
    return df


def render_page():
    st.title("Volume analysis")
    st.markdown(
        """
    ## Tom's volume analyser.
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
    df = process_csv(csv)
    st.dataframe(df["volume"].describe())
    chart = ewm_plot(df, windows=(10, 30, 90))
    chart.width = 800
    chart.height = 500
    st.altair_chart(chart)


render_page()
