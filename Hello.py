import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
import base64
st.set_page_config(
    page_title="Genes from Space",
    page_icon="🌍",
    layout="wide"
)

height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.3)
st.image('images/logo.png')
with st.sidebar:
    with st.expander("Settings", expanded=False):

        st.session_state.lan = st.radio("Select Language", ["en", "sp"], index=0)

texts = pd.read_csv("texts_copy.csv").set_index("id")


def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")



# st.markdown(rtext("0_ti"))
# st.markdown(rtext("0_te"))
# with st.expander(rtext("h_exp1_ti")):
#     st.markdown(rtext("h_exp1_te"))
# with st.expander(rtext("h_exp2_ti")):
#     st.markdown(rtext("h_exp2_te"))
#     st.image("images/step1.png")
#     st.image("images/step2.png")

# with st.expander(rtext("h_exp3_ti")):
#     st.markdown(rtext("h_exp3_te"))

# st.markdown(rtext("0_te2"))


col1, col2, col3 = st.columns([1,10,1])

with col2:
    with st.expander(rtext("disclaimer_ti")):
        st.markdown(rtext("disclaimer_te"))
    st.markdown(rtext("hello_1"))
    st.image('images/EO_intro-2048x928.png', caption='Earth observation Intro', width=st.session_state.height*2)
    st.markdown(rtext("hello_2"))

    st.image('images/Ne500-1-1536x659.png', caption='Ne500',width=st.session_state.height*2)
    st.markdown(rtext("hello_3"))
    st.image('images/PM-1536x749.png', caption='PM',width=st.session_state.height*2)
    st.markdown(rtext("hello_4"))
    st.image('images/PopPolygons-1536x641.png', caption='Population Polygons',width=st.session_state.height*2)
    st.markdown(rtext("hello_5"))
    st.image('images/AreaChange-1536x636.png', caption='Area change',width=st.session_state.height*2)
    st.markdown(rtext("hello_6"))
    st.image('images/PointsToPoly-2048x422.png', caption='Points to Polygons',width=st.session_state.height*2)
    st.markdown(rtext("hello_7"))
    st.image('images/LandcoverToHabitat-2048x504.png', caption='Landcover to habitat',width=st.session_state.height*2)
    st.markdown(rtext("hello_8"))
    st.markdown("\n")  # Add a break
    st.markdown(rtext("thanks_ti"))
    st.markdown(rtext("thanks_te"))
# Define custom CSS for consistent spacing
    # Encode the images to base64
    nomis_logo_path = "/home/ubuntu/Genes_from_Space_interface/images/Nomis_Logo.png"
    uzh_logo_path = "/home/ubuntu/Genes_from_Space_interface/images/uzh_logo.png"

    nomis_logo_base64 = base64.b64encode(open(nomis_logo_path, "rb").read()).decode()
    uzh_logo_base64 = base64.b64encode(open(uzh_logo_path, "rb").read()).decode()

    # Define custom CSS for consistent spacing and layout
    st.markdown(
        """
        <style>
        .image-container {
            display: flex;
            justify-content: left;
            align-items: center;
            gap: 20px; /* Adjust spacing between images */
        }
        .image-container img {
            max-width: auto;
            height: 150px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create a container for the images
    st.markdown(
        f"""
        <div class="image-container">
            <img src="data:image/png;base64,{nomis_logo_base64}" alt="Nomis Logo">
            <img src="data:image/png;base64,{uzh_logo_base64}" alt="UZH Logo">
        </div>
        """,
        unsafe_allow_html=True
    )