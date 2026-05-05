import pandas as pd
import streamlit as st

DATA_PATH = "data/Flight_delay.csv"

_DTYPES = {
    "UniqueCarrier": "category",
    "Airline": "category",
    "Origin": "category",
    "Dest": "category",
    "Org_Airport": "category",
    "Dest_Airport": "category",
    "CancellationCode": "category",
    "DayOfWeek": "int8",
    "Cancelled": "int8",
    "Diverted": "int8",
}


@st.cache_data(show_spinner="Loading flight data...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype=_DTYPES, low_memory=False)
    return df
