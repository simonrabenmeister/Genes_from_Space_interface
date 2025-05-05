import streamlit as st

st.set_page_config(
    page_title="GFS-tool",
    page_icon="🌍",
)

if "height" not in st.session_state:
    st.session_state.height = 1000
st.write("# Welcome to Streamlit! 🌍")

with st.sidebar:
    with st.expander("Page Height", expanded=False):
        st.session_state.height = st.slider(
            "Page Height", 0, 2000, st.session_state.height
        )

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)