

import streamlit as st
import time
import pandas as pd
from io import StringIO
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
import geojson
import api_calls


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
values = [
    10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220
]

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




tab1, tab2= st.tabs(["Pipeline", "Inputs"])

with tab1:
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
            mapgeojson()
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
        write=st.write(st.session_state.save)
        if st.button("Commit"):
            st.session_state.commit=True
            st.session_state.savecheck=st.session_state.save.copy()
            st.write(st.session_state.save)
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

with tab2:
    if st.session_state.commit==False or st.session_state.savecheck!=st.session_state.save:
        st.write("Please Commit your selection before proceding")
    if st.session_state.savecheck==st.session_state.save:
        if st.session_state.commit:
            ne_nc = st.text_input(
                "Ne:Nc ratio",
                placeholder="Example: 0.01"
            )
            if ne_nc:
                st.session_state.input["ne_nc"]= float(ne_nc)
            Title = st.text_input(
                "Title of the Run",
                placeholder="Quercus sartorii, Mexico, Habitat decline by tree cover loss, 2000-2023"
            )
            if Title:
                st.session_state.input["runtitle"]= Title
            
            density = st.text_input(
                "population densities. One or multiple",
                placeholder="50, 100, 1000"
            )
            if density:
                st.session_state.input["pop_density"]= float(density)
            if st.session_state.save["LCtype"]=="Land cover":
                years=list(range(1992,2021))
            if st.session_state.save["LCtype"]=="Forest cover":
                years=list(range(2000,2024))          
            interest_years = options = st.multiselect(
            "Years of interest",
            years,
            )
            if interest_years:
                st.session_state.input["years"]= interest_years

            if st.session_state.type["LC_bbox"] or st.session_state.type["TC_bbox"] or st.session_state.type["LC_country"] or st.session_state.type["TC_country"] or st.session_state.type["LC_obs"] or st.session_state.type["TC_obs"]:

                if not (st.session_state.type["LC_obs"] or st.session_state.type["TC_obs"]):
                    species_name=st.text_input(
                    "Species name",
                    placeholder="Quercus sartorii"
                    )  
                    if species_name:  
                        st.session_state.input["species"]= species_name
                    start_year=st.text_input(
                    "Start year",
                    placeholder="1980"
                    )
                    if start_year:
                        st.session_state.input["start_year"]= float(start_year)
                    end_year=st.text_input(
                    "End year",
                    placeholder="2020"
                    )
                    if end_year:
                        st.session_state.input["end_year"]= float(end_year)
                buffer=st.text_input(
                "Buffer size",
                placeholder="15"
                )
                if buffer:
                    st.session_state.input["buffer_size"]= float(buffer)
                pop_distance=st.text_input(
                "distance between populations",
                placeholder="25"
                )
                if pop_distance:
                    st.session_state.input["pop_distance"]= float(pop_distance)

                if st.session_state.type["LC_bbox"] or st.session_state.type["TC_bbox"]:
                    bbox=st.text_input(
                    "BBox coordinates",
                    placeholder="-99, 22, -92, 29"
                    )
                    if bbox:
                        st.session_state.input["bbox"]= bbox
                if st.session_state.type["LC_country"] or st.session_state.type["TC_country"]:
                    country=st.text_input(
                    "country of interest",
                    placeholder="Mexico"
                    )
                    if country:
                        st.session_state.input["countries"]= country


            if st.session_state.type["LC_bbox"] or st.session_state.type["LC_obs"] or st.session_state.type["LC_country"] or st.session_state.type["LC_poly"] : 
                LC_class=st.multiselect(
                "Land cover class",
                LC_names
                )
                if LC_class:
                    st.session_state.input["LC class"]=[values[LC_names.index(name)] for name in LC_class]
            if st.session_state.type["LC_obs"] or st.session_state.type["TC_obs"]:
                csv=mapcsv()
                if st.button("Upload CSV"):
                    st.session_state.input["csv"]=csv
                
            if st.session_state.type["TC_poly"] or st.session_state.type["LC_poly"]:
                geojson=mapgeojson()
                if st.button("Upload Geojson"):
                    st.session_state.input["geojson"]=geojson

    if st.button("Run Script"):
        st.write(st.session_state.type)


        for key, value in st.session_state.type.items():
            func = None
            if value:
                func = getattr(api_calls, key)

            if func:
                st.write(func)
                st.write(st.session_state.input)
                st.write("http://130.60.24.27/pipeline/"+func(st.session_state.input).text)
            
                
    