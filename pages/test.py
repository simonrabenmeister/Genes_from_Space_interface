import streamlit as st
st.set_page_config(
    page_title="Login",
    page_icon="🔏",
    layout="wide")



col1, col2 = st.columns(2)

with col1:
    with st.container(key="image-container", border=True, height=height):
        st.markdown("Hello, this is a test page for the Genes from Space interface.")
        st.image(
            "https://via.placeholder.com/300",
            caption="Placeholder Image",
            use_column_width=True
        )
        st.text_input(
            "Enter your name:",
            placeholder="Type here..."
        )
        st.text_area(
            "Enter your message:",
            placeholder="Type your message here..."
        )
        st.button(
            "Submit",
            key="submit-button"
        )
        st.checkbox(
            "I agree to the terms and conditions",
            key="terms-checkbox"
        )
        st.radio(
            "Choose an option:",
            options=["Option 1", "Option 2", "Option 3"],
            key="radio-options"
        )
        st.selectbox(
            "Select a value:",
            options=["Value 1", "Value 2", "Value 3"],
            key="selectbox-values"
        )
        st.slider(
            "Adjust the slider:",
            min_value=0,
            max_value=100,
            value=50,
            key="slider-adjust"
        )
        st.markdown(
            """
            ### Additional Information
            This is a test interface for the Genes from Space project. Below are some key points:
            - This interface is built using Streamlit.
            - It is designed to be user-friendly and interactive.
            - Feel free to explore the options and provide your feedback.
            """
        )
with col2:
   st.markdown("Hello, this is a test page for the Genes from Space interface.")

st.markdown(
    """
    <style>
        st.container {
            height: 90vh !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)