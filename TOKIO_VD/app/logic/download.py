import streamlit as st
from pandas import DataFrame

@st.cache_data
def generate_download_data(dataframe: DataFrame, separator: str = ";", encoding_type: str = "utf-16"):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return dataframe.to_csv(index=False, sep=separator, encoding=encoding_type,decimal=".").encode(encoding_type)
