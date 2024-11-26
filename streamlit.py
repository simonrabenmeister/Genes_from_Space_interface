

import streamlit as st
import time
import pandas as pd
from io import StringIO
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
import geojson

# Initialize user input save
if "save" not in st.session_state:
    st.session_state.save= {}
if "commit" not in st.session_state:
    st.session_state.commit=False
if "input" not in st.session_state:
    st.session_state.input= {}
st.write("Hello! This is a automatic fill out form for the Genes from Space Tool. It helps you find the right Pipeline for your needs")
url = "https://pipelines-2.geobon.org/pipeline-form/GenesFromSpace%3EToolComponents%3EGetHabitatMaps%3EGFS_Habitat_map_GFW_tree_canopy_2000-2023"
st.write("If you want to check all the pipelines on your own check this out [link](%s)" % url)
LC_names = [
    "Cropland, rainfed",
    "Herbaceous cover",
    "Tree or shrub cover",
    "Cropland, irrigated or post-flooding",
    "Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)",
    "Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)",
    "Tree cover, broadleaved, evergreen, closed to open (>15%)",
    "Tree cover, broadleaved, deciduous, closed to open (>15%)",
    "Tree cover, broadleaved, deciduous, closed (>40%)",
    "Tree cover, broadleaved, deciduous, open (15-40%)",
    "Tree cover, needleleaved, evergreen, closed to open (>15%)",
    "Tree cover, needleleaved, evergreen, closed (>40%)",
    "Tree cover, needleleaved, evergreen, open (15-40%)",
    "Tree cover, needleleaved, deciduous, closed to open (>15%)",
    "Tree cover, needleleaved, deciduous, closed (>40%)",
    "Tree cover, needleleaved, deciduous, open (15-40%)",
    "Tree cover, mixed leaf type (broadleaved and needleleaved)",
    "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)",
    "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)",
    "Shrubland",
    "Grassland",
    "Lichens and mosses",
    "Sparse vegetation (tree, shrub, herbaceous cover) (<15%)",
    "Tree cover, flooded, fresh or brackish water",
    "Tree cover, flooded, saline water",
    "Shrub or herbaceous cover, flooded, fresh/saline/brackish water",
    "Urban areas",
    "Bare areas",
    "Water bodies",
    "Permanent snow and ice"
]

LCtype=""
poly=""
points=""
area_type=""
commit=""

LCtype= st.selectbox(
    'Select Land cover Type:',
    ('Tree cover', 'Land cover'),
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
    mapgeojson()
    st.session_state.save["poly"]="yes"
    st.session_state.save["points"]="NA"
    st.session_state.save["area_type"]= "NA"


if poly=="no":
     st.session_state.save["poly"]="no"
     points=st.radio(
        "Do you have preprocessed polygons?",
        options=["GBIF", "preexisting observations"],
        index=None
    )

if points=="preexisting observations":
    mapcsv()
    st.session_state.save["points"]="pre"
    st.session_state.save["area_type"]= "NA"

if points=="GBIF":
    st.session_state.save["points"]="GBIF"
    area_type=st.radio(
        "Country or BBox?",

        options=["BBox", "Country"],
        index=None
    )
    
if area_type:
            st.session_state.save["area_type"]=area_type


if len(st.session_state.save)==4:
    st.write("Are yo happy with your choices? If so click on Submit and you will be directed to the correct pipeline.")
    if st.button("Commit"):
        st.session_state.commit=True
        st.write(st.session_state.save)
            

LC_GBIF_bbox=st.session_state.save=={"LCtype":"Land cover","poly":"no","points":"GBIF","area_type":"BBox"}
FC_GBIF_bbox=st.session_state.save=={"LCtype":"Forest cover","poly":"no","points":"GBIF","area_type":"BBox"}
LC_GBIF_country=st.session_state.save=={"LCtype":"Land cover","poly":"no","points":"GBIF","area_type":"Country"}
FC_GBIF_country=st.session_state.save=={"LCtype":"Forest cover","poly":"no","points":"GBIF","area_type":"Country"}
LC_poly=st.session_state.save=={"LCtype":"Land cover","poly":"yes","points":"NA","area_type":"NA"}
FC_poly=st.session_state.save=={"LCtype":"Forest cover","poly":"yes","points":"NA","area_type":"NA"}
LC_obs=st.session_state.save=={"LCtype":"Land cover","poly":"no","points":"pre","area_type":"NA"}
FC_obs=st.session_state.save=={"LCtype":"Forest cover","poly":"no","points":"pre","area_type":"NA"}


if st.session_state.save== LC_GBIF_bbox:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox")

if st.session_state.save== FC_GBIF_bbox:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox")

if st.session_state.save== LC_GBIF_country:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox")

if st.session_state.save== FC_GBIF_country:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox")

if st.session_state.save== LC_poly:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_polygon")

if st.session_state.save== FC_poly:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3EForestcover_v_polygon")

if st.session_state.save== LC_obs:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_obs")

if st.session_state.save== FC_obs:
    st.write("http://172.23.69.197/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_obs")

if st.session_state.commit:
    NeNc = st.text_input(
        "Ne:Nc ratio",
        placeholder="Example: 0.01"
    )
    st.session_state.input["NeNc"]= NeNc
    Title = st.text_input(
        "Title of the Run",
        placeholder="Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023"
    )
    st.session_state.input["Title"]= Title
    density = st.text_input(
        "population densities. One or multiple",
        placeholder="50, 100, 1000"
    )
    st.session_state.input["density"]= density
    years=list(range(1992,2020))
    interest_years = options = st.multiselect(
    "Years of interest",
    years,
)
    st.session_state.input["interst years"]= interest_years

    if LC_GBIF_bbox or FC_GBIF_bbox or LC_GBIF_country or FC_GBIF_country or LC_obs or FC_obs:

        if not (LC_obs or FC_obs):
            species_name=st.text_input(
            "Species name",
            placeholder="Quercus sartorii"
            )    
            st.session_state.input["species name"]= species_name
            start_year=st.text_input(
            "Start year",
            placeholder="1980"
            )
            st.session_state.input["start year"]= start_year
            end_year=st.text_input(
            "End year",
            placeholder="2020"
            )
            st.session_state.input["end year"]= end_year
        buffer=st.text_input(
        "Buffer size",
        placeholder="15"
        )
        st.session_state.input["buffer"]= buffer
        pop_distance=st.text_input(
        "distance between populations",
        placeholder="25"
        )
        st.session_state.input["pop distance"]= pop_distance

        if LC_GBIF_bbox or FC_GBIF_bbox:
            bbox=st.text_input(
            "BBox coordinates",
            placeholder="-99, 22, -92, 29"
            )
            st.session_state.input["bbox"]= bbox
        if LC_GBIF_country or FC_GBIF_country:
            country=st.text_input(
            "country of interest",
            placeholder="Mexico"
            )
            st.session_state.input["country"]= country


    if LC_GBIF_bbox or LC_obs or LC_GBIF_country or LC_poly : 
        LC_class=st.multiselect(
        "Land cover class",
        LC_names
        )
        st.session_state.input["LC class"]= LC_class


    if st.button("Send to tool"):
        
        st.write(st.session_state.input)


values = [
    10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220
]


