
import streamlit as st
import uuid

st.set_page_config(
    page_title="Genes from Space",
    page_icon="🌍",
    layout="wide"
)

# Initialize session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# Define navigation order
pages = [
    st.Page("pages/Methods.py", title="Methods", default=True),
    st.Page("pages/Input_form.py", title="Input form"),
    st.Page("pages/Results.py", title="Results"),
    st.Page("pages/FAQ.py", title="Updates, user guide and FAQ"),
]

# Run navigation
pg = st.navigation(pages)
pg.run()
