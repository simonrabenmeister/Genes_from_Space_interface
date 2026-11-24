
import streamlit as st

import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
import base64
import uuid
st.set_page_config(
    page_title="Genes from Space",
    page_icon="🌍",
    layout="wide"
)
st.markdown(
    """
    <style>
    /* Hide the batch page from the sidebar nav; its URL still works */
    [data-testid="stSidebarNav"] a[href$="/Batch_Processing"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)
# Ensure a session ID exists for log correlation across all pages
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# Initialize the height state variable/key
height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.3)
else:
    # Fallback if JS eval fails or returns None
    if 'height' not in st.session_state:
        st.session_state.height = 500
st.image('images/logo_GfS.png')
with st.sidebar:

    st.session_state.lan = st.radio("Select Language", ["en", "sp"], index=0)
    # Display the session ID for user confirmation when debugging
    st.divider()
    st.caption(
        f"**Debug Session ID:** `{st.session_state.get('session_id', 'Loading...')}`"
        )
    

def show_faq():
    st.markdown(
        '<h2 style="font-size:26px;">Tool updates, user guide and Frequently Asked Questions (FAQ)</h2>',
        unsafe_allow_html=True
    )

    st.markdown("""
    This page provides the latest updates related to the tool, detailed user guide information as well as answers to frequently asked questions (FAQ) and troubleshooting tips.
    """)

   # User Guide
    st.subheader("User Guide")

    st.markdown("""
    The User Guide provides detailed instructions on how to use the
    tool, including input data requirements,
    parameter selection, processing steps and interpretation of results.
    """)

    USER_GUIDE_URL = "https://drive.google.com/file/d/1-nLp9wAl4Tdakr-o0M8WDCu48L8-wgBb/view?usp=sharing"

    st.link_button(
        "📖 Download the User Guide",
        USER_GUIDE_URL,
        type="secondary"
    )
    # Frequently Asked Questions
    st.subheader("Frequently Asked Questions (FAQ)")


    # 1. Browser compatibility
    with st.expander("1. I can’t open the tool in a specific web-browser."):
        st.markdown("""
        Try different browsers if the tool doesn’t load in your specific browser. It works well on google chrome, firefox and safari.
        """)

    # 2. CSV / TSV coordinate file
    with st.expander("2. I can't import my .csv or .tsv coordinate file."):
        st.markdown("""
        The monitoring tool accepts tab-separated (.tsv), comma-separated (.csv) or semicolon-separated (.csv or .tsv) files. The file must include the columns decimallongitude and decimallatitude, with coordinates provided in WGS84.

        Quick fix: Export a .txt file and change the ending to .tsv or .csv using either tab, comma or semicolon as separation of the values.
        """)

    # 3. Excel file format
    with st.expander("3. Why can’t I re-upload my observation points after opening them in Excel?"):
        st.markdown("""
        Excel may change the file format or modify the data when you save a file. If prompted, keep the original .csv or .tsv format rather than saving it as .xlsx. If you have already saved the file as .xlsx, export it again as .csv or tab-delimited text (.txt for .tsv files). For tab-delimited .txt files, make sure to change the file extension to .tsv or .csv before re-uploading the file.
        """)

    # 4. Drawing bounding box
    with st.expander("4. How do I draw the bounding box?"):
        st.markdown("""
        Click the square icon on the left, then click and drag on the map to draw a rectangular region of interest. Alternatively, select the polygon icon to draw a custom-shaped region, double-clicking to finish and close the polygon.
        """)

    # 5. GBIF species name
    with st.expander("5. GBIF doesn’t recognise my species name."):
        st.markdown("""
        Check the spelling of the species name. Check the use of capital letters (usually Genus species).
        """)

    # 6. Observation buffer / dispersal distance
    with st.expander("6. My observation buffer/dispersal distance values are rather small and in [m] not [km]."):
        st.markdown("""
        The tool only limits the observation buffer, with a minimum size of 0.5 km. The dispersal distance does not have this restriction.

        The observation buffer defines the area around each observation point where the species is assumed to occur, while the dispersal distance defines the maximum distance between observation areas for them to be considered part of the same population.

        Please make sure both values are appropriate for your species of interest. For more detailed explanations and guidance on selecting suitable values, please refer to the corresponding chapters in the User Guide.
        """)

    # 7. Land cover vs forest cover
    with st.expander("7. Should I use Landcover or Forest cover?"):
        st.markdown("""
        Global Forest Watch (GFW) provides global binary forest cover data at 30 m resolution from 2000 onwards, making it particularly suitable for forest-dwelling species and small study areas. Processing times can be long for large geographic areas. For more details, see the corresponding chapter in the User Guide.

        ESA CCI Land Cover provides global land cover data at 300 m resolution from 1992 to 2022, making it suitable for large-scale analyses and species associated with specific land cover types. We recommend using 2004 as the earliest baseline year due to greater dataset consistency from this year onwards. For more details, see the corresponding chapter in the User Guide.
        """)

    # 8. Pipeline error
    with st.expander("8. Pipeline error (Bon-in-a-Box) – job ended with status: error"):
        st.markdown("""
        An error occurred somewhere in the pipeline.

        If the error appears at the very end, after clicking “process habitat maps”, it is likely related to the visualisation. Please contact us at [info@genesfromspace.org](mailto:info@genesfromspace.org).

        If the error occurs earlier in the pipeline, the tool was unable to process your selected input parameters. Try adjusting them, for example, by selecting a different observation buffer, dispersal distance or land cover classes.

        For example, the error below occurs when:
        """)

    # 9. No observations in selected region
    with st.expander("9. Bon-in-a-Box pipeline error after searching a species in a specific region."):
        st.markdown("""
        Your selected species does not have any observation points in that specific region.

        Use the full country where possible. For subregions, draw the bounding box using the “Draw region of interest on map” function. Don’t use the subregion selection in the “select one or more countries” function, as this isn’t working yet.
        """)

    # 10. Server connection error
    with st.expander("10. Connection error – could not reach the Bon-in-a-Box server"):
        st.markdown("""
        If this happens the server is down, please contact us at [info@genesfromspace.org](mailto:info@genesfromspace.org).
        """)

    # 11. Ubuntu path error
    with st.expander('11. I get an error referring to a path on a ubuntu server ("/home/ubuntu/Genes_from_Space_interface/pages/[...], line [...], in <module> [...]"'):
        st.markdown("""
        If this happens there is an issue in the tool interface, please contact us at [info@genesfromspace.org](mailto:info@genesfromspace.org).
        """)


show_faq()

