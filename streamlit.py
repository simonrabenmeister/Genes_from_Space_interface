

import streamlit as st
import time
import pandas as pd
from io import StringIO
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import geojson
import api_calls
import webbrowser 
import questions


# Initialize user input save
#characterizes Pipeline type
if "save" not in st.session_state:
    st.session_state.save= {}
    st.session_state.save["poly"]=""
    st.session_state.save["points"]=""
#
if "savecheck" not in st.session_state:
    st.session_state.savecheck= {}

if "type" not in st.session_state:
    st.session_state.type= {}
 
if "commit" not in st.session_state:
    st.session_state.commit=False
#saves inputs for pipeline
if "input" not in st.session_state:
    st.session_state.input= {}



##Tab Styling
st.markdown('''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:20px;
    }
</style>
''', unsafe_allow_html=True)

##Header
st.markdown("# Genes from Space Monitoring Tool")
st.markdown('''Hello! This is a automatic fill out form for the Genes from Space Tool. It helps you find the right Pipeline for your needs.
            If you want, you can check out The tool on Bon in a Box directly: [Bon in a Box](https://pipelines-2.geobon.org/pipeline-form/GenesFromSpace%3EToolComponents%3EGetHabitatMaps%3EGFS_Habitat_map_GFW_tree_canopy_2000-2023)''')







LCtype= st.selectbox(
    'Select Land cover Type:',
    ('Forest cover', 'Land cover'),
    index=None,
    placeholder="Select LC Type...")

if LCtype:
    st.session_state.save["LCtype"]=LCtype
    poly=st.radio(
        "Do you have preprocessed polygons?",
        key="visibility",
        options=["yes", "no"],
        index=None
    )
    


    if poly=="yes":
        st.session_state.save["poly"]="yes"
        st.session_state.save["points"]="NA"
        st.session_state.save["area_type"]= "NA"


    if poly=="no":
        #inhibit commit button showing when changing selection
        if st.session_state.save["poly"]=="yes":
            del st.session_state.save["area_type"]
        st.session_state.save["poly"]="no"
        points=st.radio(
            "Do you have preprocessed polygons?",
            options=["GBIF", "preexisting observations"],
            index=None
        )
        

        if points=="preexisting observations":
                st.session_state.save["points"]="pre"
                st.session_state.save["area_type"]= "NA"

        if points=="GBIF":
            if st.session_state.save["points"]=="pre":
                del st.session_state.save["area_type"]
            st.session_state.save["points"]="GBIF"
            area_type=st.radio(
                "Country or BBox?",
                options=["BBox", "Country"],
                index=None
            )
    
            if area_type:
                        st.session_state.save["area_type"]=area_type


if len(st.session_state.save)==4:
    st.write("Are you happy with your choices? If so click on Submit and you will be directed to the correct pipeline.")
    if st.button("Commit"):
        st.session_state.commit=True
        st.session_state.savecheck=st.session_state.save.copy()
    types = {
        "LC_bbox": {"LCtype": "Land cover", "poly": "no", "points": "GBIF", "area_type": "BBox"},
        "TC_bbox": {"LCtype": "Forest cover", "poly": "no", "points": "GBIF", "area_type": "BBox"},
        "LC_country": {"LCtype": "Land cover", "poly": "no", "points": "GBIF", "area_type": "Country"},
        "TC_country": {"LCtype": "Forest cover", "poly": "no", "points": "GBIF", "area_type": "Country"},
        "LC_poly": {"LCtype": "Land cover", "poly": "yes", "points": "NA", "area_type": "NA"},
        "TC_poly": {"LCtype": "Forest cover", "poly": "yes", "points": "NA", "area_type": "NA"},
        "LC_obs": {"LCtype": "Land cover", "poly": "no", "points": "pre", "area_type": "NA"},
        "TC_obs": {"LCtype": "Forest cover", "poly": "no", "points": "pre", "area_type": "NA"}
    }

    urls = {
        "LC_bbox": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox",
        "TC_bbox": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_GBIF_bbox",
        "LC_country": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_countries",
        "TC_country": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_GBIF_countries",
        "LC_poly": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_polygon",
        "TC_poly": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForestcover_v_polygon",
        "LC_obs": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_obs_server",
        "TC_obs": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_obs_server"
    }

    for key, value in types.items():
        st.session_state.type[key] = st.session_state.save == value
        if st.session_state.type[key]:
            st.write(urls[key])


if st.session_state.commit==False or st.session_state.savecheck!=st.session_state.save:
    st.write("Please Commit your selection before proceding")
if st.session_state.savecheck==st.session_state.save:
    for key, value in st.session_state.type.items():
        if value:
            script=getattr(questions, key)
            inputs=script()
            st.write(st.session_state.input)
if st.button("Run Script"):
    for key, value in st.session_state.type.items():
        func = None
        if value:
            func = getattr(api_calls, key)

        if func:
            link="http://130.60.24.27/pipeline-form/"+func(st.session_state.input).text[:-33] + '/' + func(st.session_state.input).text[-32:]
            st.write(link)
            webbrowser.open(link)
            
