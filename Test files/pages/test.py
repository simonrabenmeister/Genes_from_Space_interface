import streamlit as st
import pandas as pd
import requests
import time
import numpy as np
import geojson
import json
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from functions import get_output
from functions import GBIF
from functions import mapbbox
from functions import edit_points
from functions import polygon_clustering
from functions import LC_area
from functions import TC_area



if "bbox" not in st.session_state:
    st.session_state.bbox = None
if "stage" not in st.session_state:
    st.session_state.stage = "start"           
if "height" not in st.session_state:
    st.session_state.height = 1000
if "center" not in st.session_state:
    st.session_state.center = {"lat": 45.0, "lng": 5.0}  # Default center coordinates
if "zoom" not in st.session_state:
    st.session_state.zoom = 5  # Default zoom level
if "country" not in st.session_state:
    st.session_state.country = None
if "index" not in st.session_state:
    st.session_state.index = None
if "index_boundry" not in st.session_state:
    st.session_state.index_boundry = None
if "last_object_clicked" not in st.session_state:
    st.session_state.last_object_clicked = None
if "timeseries" not in st.session_state:
    st.session_state.timeseries = None
if "area_table" not in st.session_state:
    st.session_state.area_table = None
if "cover_maps" not in st.session_state:
    st.session_state.cover_maps = None
if "obs" not in st.session_state:
    st.session_state.obs = None
if "buffer" not in st.session_state:
    st.session_state.buffer = None
if "distance" not in st.session_state:
    st.session_state.distance = None
if "polygons" not in st.session_state:
    st.session_state.polygons = None
if "poly_creation" not in st.session_state:
    st.session_state.poly_creation = None
if "index_poly" not in st.session_state:
    st.session_state.index_poly = None
if "edit_polygons" not in st.session_state:
    st.session_state.edit_polygons = None
if "baseyear" not in st.session_state:
    st.session_state.baseyear = None
if "GBIF_data" not in st.session_state:
    st.session_state.GBIF_data = {
        "species": None,
        "countries": None,
        "start_y": None,
        "end_y": None,
        "bbox": None,
        "index data": None,
        "index boundry": None
    }
if "polyinfo" not in st.session_state:
    st.session_state.polyinfo = {
        "buffer": None,
        "distance": None
    }
if "LC" not in st.session_state:
    st.session_state.LC = {
        "LC_type": None,
        "LC_class": None,
        "index": None
    }


#################### Functions ####################





##Load necessary functions, files etc
texts = pd.read_csv("texts.csv").set_index("id")
country_names = pd.read_csv("countries.txt", header=None)[0].to_numpy()  # Assuming the file has no header


LC_names = ["automatic"
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
    0, 10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220]
##Page layout:

st.set_page_config(page_title="Habitat Change", page_icon="🌍", layout="wide")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 3rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.height = st.slider(
            "Page Height",0, 2000, st.session_state.height
        )
        st.session_state.lan = st.radio("Select Language", ["en"], index=0)




def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")




col1, col2= st.columns(2)


with col1.container( border=True, key="image-container", height=st.session_state.height):

    st.title("Genes from Space Tool")

    st.markdown(rtext('1_ti'))
    st.markdown(rtext("1_te"))
    point_source = st.selectbox("Select a tool", [ "Upload your own point observations", "Source points from GBIF", "Upload your own Polygons"], index=st.session_state.GBIF_data["index data"],  placeholder="Select Point source")
    if point_source=="Upload your own Polygons":
        st.session_state.GBIF_data["index data"]=2
        st.markdown(rtext("1.1_ti"))
        st.markdown(rtext("1.1_te"))
    #Upload your own Polygon file
        poly_link= st.file_uploader("Upload your own Polygons", type=["geojson"], label_visibility="collapsed", key="point_source", )
        st.session_state.polygons = pd.read_json(poly_link, lines=True)

    #Download example file
        st.download_button(
            label="Download Example file",
            data=open("/Users/simonrabenmeister/Desktop/Genes_from_Space/Genes_from_Space_interface/Test files/polygon_example.geojson", "rb").read(),
            file_name="polygon_example.geojson",
            mime="application/geo+json",
        )
        if st.session_state.polygons:
    ####################Missing part######################
            ##move on to LC
            LC = "placeholder"
    if point_source=="Upload your own point observations":
        st.session_state.GBIF_data["index data"]=0
        st.markdown(rtext("1.2_ti"))
        st.markdown(rtext("1.2_te"))
    #Upload your own point file
        obs_link = st.file_uploader("Upload your own point observations", type=["csv"], label_visibility="collapsed", key="point_source")
        st.session_state.obs = pd.read_csv(obs_link, sep="\t")
    #Download example file
        st.download_button(
            label="Download Example file",
            data=open("/Users/simonrabenmeister/Desktop/Genes_from_Space/Genes_from_Space_interface/Test files/points_example.csv", "rb").read(),
            file_name="points_example.csv",
            mime="text/csv",
        )
    ####################Missing part######################
            ##move on to point selection


    if point_source=="Source points from GBIF":
        st.session_state.GBIF_data["index data"]=1
        st.markdown(rtext("1.3_ti"))
        st.markdown(rtext("1.3_te"))

        with st.form(key='GBIF', enter_to_submit=False):
            with st.expander(rtext("1.3.1_ti"), expanded=False):
                st.markdown(rtext("1.3.1_te"))
            st.session_state.GBIF_data["species"]=st.text_input("Species Name", placeholder="Example: Quercus sartorii", value=st.session_state.GBIF_data["species"])
            st.session_state.baseyear=st.number_input("baseline Year", value=st.session_state.baseyear, step=1, min_value=1900, max_value=2021)
            if st.session_state.baseyear is not None:
                st.session_state.GBIF_data["start_y"]=st.session_state.baseyear-10
                st.session_state.GBIF_data["end_y"]=st.session_state.baseyear
            region=st.radio("Area of interest selection", ["Map selection", "Country"], index=st.session_state.GBIF_data["index boundry"])
            if st.form_submit_button("Submit"):
                st.session_state.polyinfo = {
                    "buffer": None,
                    "distance": None
                }
                st.session_state.LC = {
                    "LC_type": None,
                    "LC_class": None,
                    "index": None
                }  

                if region=="Country":
                    st.session_state.GBIF_data["index boundry"]=1
                    st.session_state.stage="country"
                if region=="Map selection":
                    st.session_state.GBIF_data["index boundry"]=0
                    st.session_state.stage="bbox_draw"

                st.session_state.obs = None
        if region == "Country": 
            st.session_state.GBIF_data["bbox"] = None
            st.session_state.GBIF_data["countries"] = st.multiselect("Select countries", country_names, default=st.session_state.GBIF_data["countries"])

        if region=="Map selection":
            bbox_input = st.text_input("Bounding Box",placeholder="[5.831977, 45.721522, 10.763195, 47.901613]", value=st.session_state.GBIF_data["bbox"])
            st.session_state.GBIF_data["countries"] = []
            if bbox_input is not None:
                try:
                    st.session_state.GBIF_data["bbox"] = list(map(float, bbox_input.strip("[]").split(",")))
                except ValueError:
                    st.error("Invalid bounding box format. Please enter in the format: [min_lon, min_lat, max_lon, max_lat]")
        
        if st.session_state.GBIF_data["countries"] or st.session_state.GBIF_data["bbox"]:
            if st.button("Fetch Points"):
                
                st.session_state.polyinfo = {
                        "buffer": None,
                        "distance": None
                    }
                st.session_state.LC = {
                        "LC_type": None,
                        "LC_class": None,
                        "index": None
                    }  

                st.session_state.obs = None
                with st.spinner("Wait for it..."):
                    data = {
                        "pipeline@52": st.session_state.GBIF_data["species"],
                        "pipeline@60": st.session_state.GBIF_data["countries"], 
                        "pipeline@54": [st.session_state.GBIF_data["start_y"]],
                        "pipeline@55": [st.session_state.GBIF_data["end_y"]],
                        "pipeline@56": [0.1],  # Example value for coordinate precision
                        "pipeline@57": [0.1],  # Example value for coordinate uncertainty
                        "pipeline@58": st.session_state.GBIF_data["bbox"]
                    }
                    if data["pipeline@58"] is None:
                        data["pipeline@58"] = []
                    GBIF_response = GBIF(data)
                    output_GBIF = get_output(GBIF_response.text)
                    GBIF_output_code=output_GBIF["GFS_IndicatorsTool>GBIF_obs.yml@51"]
                    obs_file = open(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{GBIF_output_code}/GBIF_obs.csv")
                    obs = pd.read_csv(obs_file, sep='\t')
                    st.session_state.obs_edit = obs
                    if st.session_state.obs_edit is not None:
                        st.session_state.stage="Manipulate points"
    
    if st.session_state.obs is not None:
        st.markdown(rtext("2_ti"))
        st.markdown(rtext("2_te"))
        st.session_state.poly_creation=st.selectbox("Polygon creation", ["Buffer", "Select yourself"], index=st.session_state.index_poly, placeholder="Select Polygon creation")
        if st.session_state.poly_creation=="Buffer":
            st.markdown(rtext("2.2_ti"))
            st.markdown(rtext("2.2_te"))
            st.session_state.index_poly=0
            with st.form(key='parameters', enter_to_submit=False):
                st.session_state.polyinfo["buffer"]=st.number_input("Buffer", value=st.session_state.polyinfo["buffer"])
                st.session_state.polyinfo["distance"]=st.number_input("Distance", value=st.session_state.polyinfo["distance"])
                with st.expander(rtext("2.2.1_ti"), expanded=False):
                    st.markdown(rtext("2.2.1_te"))
                if st.form_submit_button("Submit"):
                    st.session_state.stage="polygon_clustering"
        if st.session_state.poly_creation=="Select yourself":
            st.session_state.index_poly=1
            st.markdown(rtext("2.1_te"))
            st.session_state.polyinfo["buffer"] = st.number_input("Buffer size in km", value=st.session_state.polyinfo["buffer"])

   
    if st.session_state.stage=="LC":
        if st.session_state.polygons is not None:
            st.markdown(rtext("3_ti"))
            st.markdown(rtext("3_te"))
            st.session_state.LC["LC_type"]=st.selectbox("Land Cover Type", ["Tree Cover", "manual Land Cover", "automatic Land Cover"], index=st.session_state.LC["index"])  
            with st.expander(rtext("3.1_ti"), expanded=False):
                st.markdown(rtext("3.1_te"))
        with st.form(key='areas', enter_to_submit=False):
            
            if st.session_state.LC["LC_type"]=="manual Land Cover":
                st.session_state.LC["index"]=1
                LC_class = st.multiselect("select LC class", options=LC_names, key="LC_class")
                st.session_state.LC["LC_class"] = [values[LC_names.index(name)] for name in LC_class]
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()

            if st.session_state.LC["LC_type"]=="automatic Land Cover":
                st.session_state.LC["index"]=2
                st.session_state.LC["LC_class"] = [0]
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()
        
            if st.session_state.LC["LC_type"]=="Tree Cover":
                st.session_state.LC["index"]=0
                st.session_state.LC["LC_class"]="Treecover"
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2023, 5).astype(int).tolist()
            
            if st.form_submit_button("Submit"):
                with st.spinner("Wait for it..."):
                    timeseries = st.session_state.LC["timeseries"]

                    if st.session_state.LC["LC_type"]=="manual Land Cover" or st.session_state.LC["LC_type"]=="automatic Land Cover":
                        data = {
                            "pipeline@197": st.session_state.poly_directory,
                            "pipeline@198": timeseries,
                            "pipeline@199": st.session_state.LC["LC_class"]
                        }
                        st.session_state.area=LC_area(data)
                    if st.session_state.LC["LC_type"]=="Tree Cover":
                        data = {
                            "pipeline@197": st.session_state.poly_directory,
                            "pipeline@204": timeseries
                        }
                        st.session_state.area= TC_area(data)
                    if "area" in st.session_state:
                        
                        output_area=get_output(st.session_state.area.text)
                        st.session_state.area.text
                        output_area
                        area_output_code=output_area["GFS_IndicatorsTool>pop_area_by_habitat.yml@200"]
                        if st.session_state.LC["LC_type"]=="Tree Cover":
                            cover_output_code=output_area["GFS_IndicatorsTool>get_TCY.yml@203"]
                        if st.session_state.LC["LC_type"]=="manual Land Cover" or st.session_state.LC["LC_type"]=="automatic Land Cover":
                            cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                        st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                        pop_area=f"/output/{area_output_code}/pop_habitat_area.tsv"

                        area_file_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{area_output_code}/pop_habitat_area.tsv"
            
                        st.session_state.area_table = pd.read_csv(area_file_path, sep='\t')
    if st.session_state.area_table is not None:
        rel_habitat_change_table = st.session_state.area_table.copy()
        for i in range(1, st.session_state.area_table.shape[1]):  # Start from the second column (index 1)
            rel_habitat_change_table.iloc[:, i] = (st.session_state.area_table.iloc[:, i] / st.session_state.area_table.iloc[:, 1] * 100) - 100
        st.session_state.rel_habitat_change_table = rel_habitat_change_table
        st.session_state.NC= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines{st.session_state.cover_maps}/HabitatNC.tif"
        st.session_state.GAIN= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines{st.session_state.cover_maps}/HabitatGAIN.tif"
        st.session_state.LOSS= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines{st.session_state.cover_maps}/HabitatLOSS.tif"

        if st.button("See results"):
            st.session_state.pop_polygons = st.session_state.polygons
            st.switch_page("pages/Output_display.py")
with col2:
    if st.session_state.stage=="bbox_draw":
        mapbbox()
    if st.session_state.stage=="Manipulate points":
        edit_points()
    if st.session_state.stage=="polygon_clustering":
        polygon_clustering()
    if st.session_state.stage=="LC":
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

        # Add the polygons to the map
        fg = folium.FeatureGroup(name="Polygons")
        fg.add_child(folium.GeoJson(st.session_state.polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        # Display the map
        st.session_state.output2 = st_folium(m, feature_group_to_add=fg, use_container_width=True)