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
import uuid
import os
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Habitat Change", page_icon="🌍", layout="wide")

with open("directories.txt", "r") as file:
    directories = file.readlines()
st.session_state.biab_dir = directories[0].strip()
st.session_state.api_link= directories[2].strip()
if "LC_class_names" not in st.session_state:
    st.session_state.LC_class_names=None
if "countries" not in st.session_state:
    st.session_state.countries = []
if "output_stage" not in st.session_state:
    st.session_state.output_stage = "upload"
if "original_polygons" not in st.session_state:
    st.session_state.original_polygons = None
if "bbox" not in st.session_state:
    st.session_state.bbox = None
if "stage" not in st.session_state:
    st.session_state.stage = "start"           
if "center" not in st.session_state:
    st.session_state.center = {"lat": 0.0, "lng": 0.0}  # Default center coordinates
if "zoom" not in st.session_state:
    st.session_state.zoom = 3  # Default zoom level
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
if "obs_edit" not in st.session_state:
    st.session_state.obs_edit = None
  # Default base year selection
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
if "LC_class_index" not in st.session_state:
    st.session_state.LC_class_index = None  # Default LC type
if "GBIF_index" not in st.session_state:
    st.session_state.GBIF_index = None  # Default index for GBIF selection
if "region_index" not in st.session_state:
    st.session_state.region_index = None  
if "polyinfo" not in st.session_state:
    st.session_state.polyinfo = {
        "buffer": None,
        "distance": None,
        "polygons": None
    }
if "LC" not in st.session_state:
    st.session_state.LC = {
        "LC_class": None,
        "timeseries": None
    }
if "data_source_index" not in st.session_state:
    st.session_state.data_source_index = None  # Default index for data source selection
if "LC_index" not in st.session_state:
    st.session_state.LC_index = None  # Default index for LC selection
if "LC_selection" not in st.session_state:
    st.session_state.LC_selection = None  # Default LC selection
if "species" not in st.session_state:
    st.session_state.species = None  # Default species name
if "run_id" not in st.session_state:
    st.session_state.run_id = str(uuid.uuid4())

st.session_state.run_dir= os.path.join(f"{st.session_state.biab_dir}/userdata/interface_polygons/", st.session_state.run_id)
height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.7)
if "data_source" not in st.session_state:
    st.session_state.data_source = None  # Default data source index
##Load necessary functions, files etc
texts = pd.read_csv("texts.csv").set_index("id")
country_names = pd.read_csv("countries.txt", header=None)[0].to_numpy()  # Assuming the file has no header

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
    "Permanent snow and ice", "Shrubland"
]
values = [
    10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 122
]


st.markdown("""
    <style>
           .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
           /* Fix whitespace under Folium map */
           iframe[title="streamlit_folium.st_folium"] {
            height: 500px !important;
            max-height: 500px !important;
            min-height: 500px !important;
           }
    </style>
    """, unsafe_allow_html=True)
    
st.markdown("# Genes from Space Tool")
with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.lan = st.radio("Select Language", ["en"], index=0)

def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")
col1, col2= st.columns(2)


with col1.container( border=False, key="image-container", height=st.session_state.height):

    st.markdown(rtext("1_ti"))
    st.markdown(rtext("1_te"))




    selection=["Upload your own point observations", "Source points from GBIF", "Upload your own Polygons"]

    st.session_state["data_source"] = st.selectbox(
        "Select a tool", selection, 
        index=st.session_state["data_source_index"],  
        placeholder="Select Point source", 
        key="data_source_key",
        on_change=lambda: (
        setattr(st.session_state, 'data_source_index', selection.index(st.session_state.data_source_key)),
        setattr(st.session_state, 'polyinfo', {"buffer": None, "distance": None, "polygons": None}),
        setattr(st.session_state, 'obs', None),
        setattr(st.session_state, 'obs_edit', None),
        setattr(st.session_state, 'buffer', None),
        setattr(st.session_state, 'distance', None),
        setattr(st.session_state, 'LC_selection', None),
        setattr(st.session_state, 'LC', {"LC_class": None, "timeseries": None}),
        setattr(st.session_state, 'LC_index', None),
        setattr(st.session_state, 'area_table', None),
        setattr(st.session_state, 'stage', "upload"),
        setattr(st.session_state, 'LC_class_index', None),
        setattr(st.session_state, "index_poly", None)
        )
    )
    with st.expander(rtext("1_exp_ti"), expanded=False):
        st.markdown(rtext("1_exp"))
    if st.session_state["data_source"] is not None:
        st.markdown(rtext("1_1_ti"))
        st.markdown(rtext("1_1_te"))
        name_to_species = st.text_input(rtext('1_1_in'), placeholder="Example: Quercus sartorii",value=st.session_state["species"],  disabled=st.session_state["species"]!=None)
        if name_to_species:
            
            if st.session_state["species"]==None: ## the GBIF check can be made before the species is confirmed. Once the species is set, this can not be changed. 

                # Make the API call

                response = requests.get(f"https://api.gbif.org/v1/species/match", params={"name": name_to_species})
                response = response.json()

                # Check if the request was successful

                if response["matchType"] != "NONE":
                # Parse the JSON response

                    st.write(rtext('1_1_in_te1')+" **"+str(response['scientificName'])+"** "+rtext('1_1_in_te2'))
                    if st.button(rtext('1_1_in_bu1')):
                        st.session_state["species"] = response["scientificName"]
                        st.rerun() # force streamlit to re-run page and deactivate name_to_specie form

                else:

                    st.write(rtext('1_1_in_te3'))
                    if st.button(rtext('1_1_in_bu2')):
                        st.session_state["species"] = name_to_species                
                        st.rerun() # force streamlit to re-run page and deactivate name_to_specie form

        
        st.number_input("Baseline Year", step=1, min_value=1900, max_value=2021, key="baseyear_selection", value=st.session_state.baseyear, on_change=lambda: (setattr(st.session_state, 'baseyear', st.session_state.baseyear_selection)))
        with st.expander(rtext("1_2_exp"), expanded=False):
            st.markdown(rtext("1_2_te"))
        if st.session_state["baseyear"] is not None:             
            st.session_state.GBIF_data["start_y"]=st.session_state.baseyear-10
            st.session_state.GBIF_data["end_y"]=st.session_state.baseyear
    if st.session_state.baseyear is not None and st.session_state["species"] is not None:
        if st.session_state["data_source"]=="Upload your own Polygons":

            st.markdown(rtext("1.1_ti"))
            st.markdown(rtext("1.1_te"))
        #Upload your own Polygon file
            poly_link= st.file_uploader("Uplad your own Polygons", type=["geojson"], label_visibility="collapsed", key="point_source", on_change=lambda: st.session_state.update({"stage": "polygon_clustering"}))
            if poly_link is not None:
                try:
                    st.session_state.polyinfo["polygons"] = geojson.load(poly_link)


                except Exception as e:
                    st.error(f"Error reading the GeoJSON file: {e}")
                # Calculate the center of the polygon
                coordinates = st.session_state.polyinfo["polygons"]["features"][0]["geometry"]["coordinates"][0]
                flattened_coordinates = [point for sublist in coordinates for point in sublist]
                lats = [point[1] for point in flattened_coordinates]
                lngs = [point[0] for point in flattened_coordinates]
                center_lat = sum(lats) / len(lats)
                center_lng = sum(lngs) / len(lngs)

                # Update session state with the center coordinates
                st.session_state.center = {"lat": center_lat, "lng": center_lng}
        #Download example file
            st.download_button(
                label="Download Example file",
                data=open("polygon_example.geojson", "rb").read(),
                file_name="polygon_example.geojson",
                mime="application/geo+json",
            )

            if st.session_state.polyinfo["polygons"] is not None:
                run=os.path.join(st.session_state.run_dir, "updated_polygons.geojson")
                os.makedirs(os.path.dirname(run), exist_ok=True)  # Ensure the directory exists
                with open(run, "w") as f:
                    geojson.dump(st.session_state.polyinfo["polygons"], f)
                st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
                st.session_state.stage = "LC"

        if st.session_state["data_source"]=="Upload your own point observations":

            st.markdown(rtext("1.2_ti"))
            st.markdown(rtext("1.2_te"))
        #Upload your own point file
            obs_link = st.file_uploader("Upload your own point observations", type=["csv"], label_visibility="collapsed", key="point_source", 
                                        on_change=lambda: st.session_state.update({"stage": "Manipulate points"}))
            if obs_link is not None and st.session_state.obs_edit is None:
                try:
                    st.session_state.obs_edit = pd.read_csv(obs_link, sep="\t")
                    # Check if the required columns are present
                    required_columns = ["decimallongitude", "decimallatitude"]
                    if not all(col in st.session_state.obs_edit.columns for col in required_columns):
                        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")

                except Exception as e:
                    st.error(f"Error reading the CSV file: {e}")
            if st.session_state.obs_edit is not None:
                # Calculate the center of all point observations in total
                lats = st.session_state.obs_edit["decimallatitude"].to_numpy()
                lngs = st.session_state.obs_edit["decimallongitude"].to_numpy()
                center_lat = np.mean(lats)
                center_lng = np.mean(lngs)

                # Update session state with the center coordinates
                st.session_state.center = {"lat": center_lat, "lng": center_lng}
                

        #Download example file
            st.download_button(
                label="Download Example file",
                data=open("points_example.csv", "rb").read(),
                file_name="points_example.csv",
                mime="text/csv"
            )

        if st.session_state["data_source"]=="Source points from GBIF":


            st.markdown(rtext("1.3_ti"))


            region_list=["Map selection", "Country"]
            region = st.selectbox(
                "Region Selection",
                region_list,
                index=st.session_state["region_index"],
                placeholder="Select Region",
                key="region_selection",
                on_change=lambda: (
                setattr(st.session_state, 'region_index', region_list.index(st.session_state.region_selection)),
                setattr(st.session_state, 'stage', "country" if st.session_state.region_selection == "Country" else "bbox_draw"),
                )
            )
            with st.expander(rtext("1.3_exp"), expanded=False):
                st.markdown(rtext("1.3_te"))
            if region== "Country": 
                st.session_state.GBIF_data["bbox"] = None
                countries = st.multiselect("Select countries", country_names, default=st.session_state.countries,key="country_selection", on_change=lambda: setattr(st.session_state, 'countries', st.session_state.country_selection))
            if region=="Map selection":
                st.markdown(rtext("1.3.2_ti"))
                st.markdown(rtext("1.3.2_te"))
                st.session_state.countries = []
            if st.session_state.countries or st.session_state.GBIF_data["bbox"]:
                if st.button("Get observations from GBIF"):
                    
                    st.session_state.polyinfo = {
                            "buffer": None,
                            "distance": None,
                            "polygons": None
                        }
                    st.session_state.LC = {
                            "LC_type": None,
                            "LC_class": None,
                            "index": None
                        }  

                    st.session_state.obs = None
                    with st.spinner("Wait for it..."):
                        data = {
                            "pipeline@52": st.session_state.species,
                            "pipeline@60": st.session_state.countries, 
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
                        obs_file = open(f"{st.session_state.biab_dir}/output/{GBIF_output_code}/GBIF_obs.csv")
                        obs = pd.read_csv(obs_file, sep='\t')
                        st.session_state.obs_edit = obs
                        st.session_state.stage = "Manipulate points"
    if st.session_state.obs_edit is not None and st.session_state.baseyear is not None:
        # Calculate the center of all point observations in total
        lats = st.session_state.obs_edit["decimallatitude"].to_numpy()
        lngs = st.session_state.obs_edit["decimallongitude"].to_numpy()
        center_lat = np.mean(lats)
        center_lng = np.mean(lngs)

        # Update session state with the center coordinates
        st.session_state.center = {"lat": center_lat, "lng": center_lng}
        st.markdown(rtext("1.3.3_ti"))
        st.markdown(rtext("1.3.3_te"))
        if st.button("save points"):
            st.session_state.obs = st.session_state.obs_edit
            st.session_state.poly_creation = None
            st.session_state.LC = {
                "LC_type": None,
                "LC_class": None,
                "index": None
            }  
            st.session_state.area_table = None
            st.session_state.cover_maps = None
            st.session_state.stage="polygon_clustering"

            
    if st.session_state.obs is not None:
        st.markdown(rtext("2_ti"))
        st.markdown(rtext("2_te"))
        buffer_selection= ["Automated calculation of population boundaries", "Draw population boundaries manually"]
        st.session_state.poly_creation = st.selectbox(
            "Polygon creation",
            buffer_selection,
            index=st.session_state.index_poly,
            placeholder="Select Polygon creation",
            on_change=lambda: (
            setattr(st.session_state, 'index_poly', buffer_selection.index(st.session_state.index_poly_key)),
            setattr(st.session_state, "polyinfo",{"buffer": None, "distance": None, "polygons": None}),
            setattr(st.session_state, "stage", "polygon_clustering")
            ),
            key="index_poly_key"
        )

        if st.session_state.poly_creation=="Automated calculation of population boundaries":
            st.markdown(rtext("2.2_ti"))
            st.markdown(rtext("2.2_te"))
            st.session_state.index_poly=0
            with st.form(key='parameters', enter_to_submit=False):
                st.number_input("Buffer", value=st.session_state.buffer, key="buffer_input")
                st.number_input("Distance", value=st.session_state.distance, key="distance_input")
                with st.expander(rtext("2.2.1_ti"), expanded=False):
                    st.markdown(rtext("2.2.1_te"))
                if st.form_submit_button("Submit"):
                    st.session_state.stage="polygon_clustering"

                    # Reset subsequent session states
                    st.session_state.LC = {
                        "LC_type": None,
                        "LC_class": None,
                        "index": None
                    }
                    st.session_state.area_table = None
                    st.session_state.cover_maps = None
                    setattr(st.session_state, 'buffer', st.session_state.buffer_input)
                    setattr(st.session_state, 'distance', st.session_state.distance_input)
        if st.session_state.poly_creation=="Draw population boundaries manually":
            st.session_state.index_poly=1
            st.markdown(rtext("2.1_te"))
            st.session_state.buffer=st.number_input("Buffer", value=st.session_state.buffer, key="buffer_input", on_change=lambda: setattr(st.session_state, 'buffer', st.session_state.buffer_input))
    if st.session_state.stage=="LC":
        if st.session_state.polyinfo["polygons"] is not None:
            st.markdown(rtext("3_ti"))
            st.markdown(rtext("3_te"))
            LC_selection = ["Tree Cover", "manual Land Cover", "automatic Land Cover"]
            st.session_state.LC_selection= st.selectbox(
                "Land Cover Type",
                LC_selection,
                index=st.session_state.LC_index,
                placeholder="Select Land Cover Type",
                key="LC_type_key",
                on_change=lambda: setattr(st.session_state, "LC_index", LC_selection.index(st.session_state.LC_type_key))
            )

            
            with st.expander(rtext("3.1_ti"), expanded=False):
                st.markdown(rtext("3.1_te"))
        with st.form(key='areas', enter_to_submit=False):

            if st.session_state.LC_selection=="manual Land Cover":
                LC_class = st.multiselect("select LC class", options=LC_names, key="LC_class", default=st.session_state.LC_class_names)
                
                st.session_state.LC["LC_class"] = [values[LC_names.index(name)] for name in LC_class]
                if 2020-st.session_state.baseyear < 5:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
                else:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()

            if st.session_state.LC_selection=="automatic Land Cover":
                st.session_state.LC["LC_class"] = [0]
                if 2020-st.session_state.baseyear < 5:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
                else:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()
        
            if st.session_state.LC_selection=="Tree Cover":
                st.session_state.LC["LC_class"]=["Treecover"]
                if 2020-st.session_state.baseyear < 5:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
                else:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()
            
            if st.form_submit_button("Submit"):
                st.session_state.run_id = str(uuid.uuid4())
                
                setattr(st.session_state, "LC_class_index",  st.session_state.LC["LC_class"])
                if st.session_state.LC_selection=="manual Land Cover":
                    setattr(st.session_state,"LC_class_names",  LC_class)
                with st.spinner("Wait for it..."):
                    timeseries = st.session_state.LC["timeseries"]
                    if st.session_state.LC_selection=="manual Land Cover" or st.session_state.LC_selection=="automatic Land Cover":
                        data = {
                            "pipeline@197": st.session_state.poly_directory,
                            "pipeline@198": timeseries,
                            "pipeline@199": st.session_state.LC["LC_class"]
                        }
                        st.session_state.area=LC_area(data)
                    if st.session_state.LC_selection=="Tree Cover":
                        data = {
                            "pipeline@197": st.session_state.poly_directory,
                            "pipeline@204": timeseries
                        }
                        st.session_state.area= TC_area(data)

                    # Reset subsequent session states
                    st.session_state.area_table = None
                    st.session_state.cover_maps = None

                    if "area" in st.session_state:
                        
                        output_area=get_output(st.session_state.area.text)

                        area_output_code=output_area["GFS_IndicatorsTool>pop_area_by_habitat.yml@200"]
                        if st.session_state.LC_selection=="Tree Cover":
                            cover_output_code=output_area["GFS_IndicatorsTool>get_TCY.yml@203"]
                        if st.session_state.LC_selection=="manual Land Cover":
                            st.session_state.LC_classnames=[LC_names[values.index(value)] for value in st.session_state.LC["LC_class"]]
                            cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                            st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                        pop_area=f"/output/{area_output_code}/pop_habitat_area.tsv"
                        if st.session_state.LC_selection == "automatic Land Cover":
                            cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                            st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                            LC_class = json.load(open(f"{st.session_state.biab_dir}/output/{cover_output_code}/output.json"))["lc_classes"]
                            st.session_state.LC_classnames = [LC_names[values.index(value)] for value in LC_class]
                        area_file_path = f"{st.session_state.biab_dir}/output/{area_output_code}/pop_habitat_area.tsv"
                        st.session_state.area_table = pd.read_csv(area_file_path, sep='\t')
                        
    if st.session_state.area_table is not None:
        rel_habitat_change_table = st.session_state.area_table.copy()
        for i in range(1, st.session_state.area_table.shape[1]):  # Start from the second column (index 1)
            rel_habitat_change_table.iloc[:, i] = (st.session_state.area_table.iloc[:, i] / st.session_state.area_table.iloc[:, 1] * 100) - 100
        st.session_state.rel_habitat_change_table = rel_habitat_change_table
        st.session_state.NC= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatNC.tif"
        st.session_state.GAIN= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatGAIN.tif"
        st.session_state.LOSS= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatLOSS.tif"
        
        if st.button("See results"):
            st.session_state.output_stage = "run"
            st.session_state.default_dens=None
            st.session_state.default_nenc=None
            st.session_state.properties=None
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
        fg.add_child(folium.GeoJson(st.session_state.polyinfo["polygons"], popup=folium.GeoJsonPopup(fields=["name"])))
        # Display the map
        st.session_state.output2 = st_folium(m, feature_group_to_add=fg, use_container_width=True)