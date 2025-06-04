import streamlit as st
from streamlit import session_state as _state

_PERSIST_STATE_KEY = f"{__name__}_PERSIST"


def persist(key: str) -> str:
    """Mark widget state as persistent."""
    if _PERSIST_STATE_KEY not in _state:
        _state[_PERSIST_STATE_KEY] = set()

    _state[_PERSIST_STATE_KEY].add(key)

    return key


def load_widget_state():
    """Load persistent widget state."""
    if _PERSIST_STATE_KEY in _state:
        _state.update({
            key: value
            for key, value in _state.items()
            if key in _state[_PERSIST_STATE_KEY]
        })
# Removed persist import as it caused an ImportError
if 'selectbox_option' not in st.session_state:
    st.session_state.selectbox_option = "Email"

option_list = ['Email', 'Home phone', 'Mobile phone']

    

option = st.selectbox(
    'How would you like to be contacted?',
    option_list,
    key=persist('selectbox_option'))

# Index value of selected option
st.session_state.selectbox_option = option
st.write('Index:', st.session_state.selectbox_option)

# Selected option
st.write('You selected:', option_list[st.session_state.selectbox_option])