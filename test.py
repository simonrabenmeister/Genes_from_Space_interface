
import streamlit as st
import time
import pandas as pd
from io import StringIO
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
import geojson

st.markdown('''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:20px;
    }
</style>
''', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Pipeline", "Inputs"])
