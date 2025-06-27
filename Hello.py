import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
st.set_page_config(
    page_title="GFS-tool",
    page_icon="🌍",
    layout="wide"
)

height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.7)
st.write("# Welcome to Genes from Space! 🌍")
with st.sidebar:
    with st.expander("Settings", expanded=False):

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

