import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GFS-tool",
    page_icon="🌍",
    layout="wide"
)

if "height" not in st.session_state:
    st.session_state.height = 1000
st.write("# Welcome to Genes from Space! 🌍")
with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.height = st.slider(
            "Page Height",0, 2000, st.session_state.height
        )
        st.session_state.lan = st.radio("Select Language", ["en"], index=0)

texts = pd.read_csv("texts.csv").set_index("id")


def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")

with st.expander(rtext("disclaimer_ti")):
    st.markdown(rtext("disclaimer_te"))

st.markdown(rtext("0_ti"))
st.markdown(rtext("0_te"))
with st.expander(rtext("h_exp1_ti")):
    st.markdown(rtext("h_exp1_te"))
with st.expander(rtext("h_exp2_ti")):
    st.markdown(rtext("h_exp2_te"))
    st.image("images/pipeline_description.png")
with st.expander(rtext("h_exp3_ti")):
    st.markdown(rtext("h_exp3_te"))
