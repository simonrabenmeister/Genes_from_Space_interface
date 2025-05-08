import streamlit as st

st.set_page_config(
    page_title="GFS-tool",
    page_icon="🌍",
)

if "height" not in st.session_state:
    st.session_state.height = 1000
st.write("# Welcome to Genes from Space! 🌍")

with st.sidebar:
    with st.expander("Page Height", expanded=False):
        st.session_state.height = st.slider(
            "Page Height", 0, 2000, st.session_state.height
        )

st.markdown(
    """
    Genes from Space is a tool designed to analyze genetic diversity from space.

    **👈 Use the sidebar** to adjust settings and explore the tool's features.

    ### Features:
    - Visualize genetic data in interactive charts.
    - Generate detailed reports for research purposes.

    ### Learn more:
    - Visit our [official website](https://genesfromspace.example.com)
    - Check out the [documentation](https://docs.genesfromspace.example.com)
    - Join the discussion in our [community forums](https://community.genesfromspace.example.com)
    """
)