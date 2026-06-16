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
from functions import (
    get_output, 
    GBIF, 
    mapbbox, 
    edit_points, 
    polygon_clustering, 
    LC_area, 
    TC_area, 
    LC_info, 
    BiaBError, 
    _show_biab_error
)
from logging_config import log_and_show, log_and_warn
import uuid
import os
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval
from functions import manual_polygon_addition
st.set_page_config(page_title="Genes From Space", page_icon="🌍", layout="wide")

# Ensure a session ID exists for log correlation across all pages
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# Initialize the height state variable/key
if 'height' not in st.session_state:
    # Try to get screen height if possible, otherwise default
    try:
        height_source = streamlit_js_eval(js_expressions='screen.height', key='SCR_page') 
        if height_source is not None:
            st.session_state.height = int(height_source * 0.3)
        else:
            st.session_state.height = 500
    except Exception:
        # Fallback if JS eval fails or function is missing
        st.session_state.height = 500

# Remove whitespace from the top of the page and sidebar

with open("directories.txt", "r") as file:
    directories = file.readlines()
st.session_state.biab_dir = directories[0].strip()
st.session_state.api_link= directories[2].strip()
if "lan" not in st.session_state:
    st.session_state.lan = "en"
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
if "info" not in st.session_state:
    st.session_state.info = None
if "poly_old" not in st.session_state:
    st.session_state.poly_old = None
if "GBIF_range" not in st.session_state:
    st.session_state.GBIF_range = None
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
if "obs_csv" not in st.session_state:
    st.session_state.obs_csv = None
if "all_drawings" not in st.session_state:
    st.session_state.all_drawings = None
if "polygon_addition" not in st.session_state:
    st.session_state.polygon_addition = None
st.session_state.run_dir= os.path.join(f"{st.session_state.biab_dir}/userdata/interface_polygons/", st.session_state.run_id)
height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.5)
if "data_source" not in st.session_state:
    st.session_state.data_source = None  # Default data source index
##Load necessary functions, files etc
texts = pd.read_csv("texts.csv").set_index("id")
country_names = pd.read_csv("countries.txt", header=None)[0].to_numpy()  # Assuming the file has no header

LC_dict = {
    "Rainfed cropland": [10, 11, 12],
    "Irrigated cropland": [20],
    "Mosaic cropland (>50%) / natural vegetation (<50%)": [30],
    "Mosaic natural vegetation (>50%) / cropland (<50%)": [40],
    "Tree cover, broadleaved, evergreen, closed to open (>15%)": [50],
    "Tree cover, broadleaved, deciduous, closed to open (>15%)": [60, 61, 62],
    "Tree cover, needleleaved, evergreen, closed to open (>15%)": [70, 71, 72],
    "Tree cover, needleleaved, deciduous, closed to open (>15%)": [80, 81, 82],
    "Tree cover, mixed leaf type (broadleaved and needleleaved)": [90],
    "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)": [100],
    "Tree cover, flooded, fresh or brackish water": [160],
    "Tree cover, flooded, saline water": [170],
    "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)": [110],
    "Grassland": [130],
    "Shrub or herbaceous cover, flooded, fresh-saline or brackish water": [180],
    "Urban": [190],
    "Shrubland": [120, 121, 122],
    "Lichens and mosses": [140],
    "Sparse vegetation (tree, shrub, herbaceous cover)": [150, 151, 152, 153],
    "Bare areas": [200, 201, 202],
    "Water": [210],
    "Permanant Ice and Snow": [220]
}

LC_names_simple_en= [
    "Forest",
    "Agriculture",
    "Grassland",
    "Wetlands",
    "Shrubland",
    "Sparse vegetation",
    "bare Areas",
    "Settlements"
]
LC_names_simple_sp = [
    "Bosque",
    "Agricultura",
    "Pastizales",
    "Humedales",
    "Matorrales",
    "Vegetación escasa",
    "Áreas desnudas",
    "Asentamientos"
]
if st.session_state.lan=="sp":
    LC_names_simple=LC_names_simple_sp
elif st.session_state.lan=="en":    
    LC_names_simple=LC_names_simple_en


values_simple = [
    [50, 60, 61, 62, 70, 71, 72, 80, 81, 82, 90, 100, 160, 170],  # Forest
    [10, 11, 12, 20, 30, 40],      # Agriculture
    [110, 130],       # Grassland
    180,  # Wetlands
    [120, 121, 122],             # Shrubland
    [140,150, 151, 152, 153],            # Sparse vegetation
    [200, 201, 202],      # Bare Areas
    190       # Settlements
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
    

st.image('images/logo.png')
with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.lan = st.radio("Select Language", ["en", "sp"], key="language_selection")
    # Display the session ID for user confirmation when debugging
    st.divider()
    st.caption(
        f"**Debug Session ID:** `{st.session_state.get('session_id', 'Loading...')}`"
        )


def rtext(id):
    return texts.loc[id, st.session_state.lan].replace("\\n", "\n")
col1, col2= st.columns(2)


with col1.container( border=False, key="image-container", height=st.session_state.height):

### 1st step: Set how to provide species input data

    st.markdown(rtext("1_ti"))
    st.markdown(rtext("1_te"))

### Choose data source

    st.markdown(rtext("1_1_ti"))
    st.markdown(rtext("1_1_te"))
    selection=[rtext("1_1_opt1"), rtext("1_1_opt2"), rtext("1_1_opt3")]

    st.session_state["data_source"] = st.selectbox(
        rtext("1_1_in"), selection, 
        index=st.session_state["data_source_index"],  
        placeholder=rtext("1_1_plac"),
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
        setattr(st.session_state, "index_poly", None),
        setattr(st.session_state, "baseyear", None)
        )
    )
    with st.expander(rtext("1_1_exp_ti"), expanded=False):
        st.markdown(rtext("1_1_exp_te"))
    if st.session_state["data_source"] is not None:
        
        if st.session_state["data_source"]==rtext("1_1_opt3"): # Upload your own polygons

            st.markdown(rtext("1_3_1_ti"))
            st.markdown(rtext("1_3_1_te"))
            with st.expander(rtext("1_3_1_exp_ti"), expanded=False):
                st.markdown(rtext("1_3_1_exp_te"))
        #Upload your own Polygon file
            poly_link= st.file_uploader(rtext("1_3_1_plac"), type=["geojson"], label_visibility="collapsed", key="point_source")
            if poly_link is not None:
                try:
                    st.session_state.polyinfo["polygons"] = geojson.load(poly_link)


                except Exception as e:
                    log_and_show(f"Error reading the GeoJSON file: {e}", exc_info=True)

#######Removed center finder since it only works with multpolygons and not normal polygons
                # # Calculate the center of the polygon
                # st.session_state.polyinfo["polygons"]
                # coordinates = st.session_state.polyinfo["polygons"]["features"][0]["geometry"]["coordinates"][0]
                # coordinates
                # flattened_coordinates = [point for sublist in coordinates for point in sublist]

                # lats = [point[1] for point in flattened_coordinates]
                # lngs = [point[0] for point in flattened_coordinates]
                # center_lat = sum(lats) / len(lats)
                # center_lng = sum(lngs) / len(lngs)

                # # Update session state with the center coordinates
                # st.session_state.center = {"lat": center_lat, "lng": center_lng}
        #Download example file
            st.download_button(
                label=rtext("1_3_1_ex_file"),
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

        if st.session_state["data_source"]==rtext("1_1_opt1"): # Upload your own points

            st.markdown(rtext("1_3_2_ti"))
            st.markdown(rtext("1_3_2_te"))
        #Upload your own point file
            obs_link = st.file_uploader(rtext("1_3_2_plac"), type=["csv"], label_visibility="collapsed", key="point_source", 
                                        on_change=lambda: st.session_state.update({"stage": "Manipulate points", "obs": None}))
            if obs_link is not None and st.session_state.obs_edit is None:
                try:
                    st.session_state.obs_edit = pd.read_csv(obs_link, sep="\t")
                    # Check if the required columns are present
                    required_columns = ["decimallongitude", "decimallatitude"]
                    if not all(col in st.session_state.obs_edit.columns for col in required_columns):
                        log_and_show(f"{rtext('1_3_2_err')}, {', '.join(required_columns)}")

                except Exception as e:
                    log_and_show(f"Error reading the CSV file: {e}", exc_info=True)
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
                label=rtext("1_3_1_ex_file"),
                data=open("points_example.csv", "rb").read(),
                file_name="points_example.csv",
                mime="text/csv"
            )

        if st.session_state["data_source"]==rtext("1_1_opt2"): # Search species in GBIF
            
            st.markdown(rtext("1_3_3_ti")) 
            st.markdown(rtext("1_3_3_te")) 
 
            name_to_species = st.text_input(rtext('1_3_3_1_plac'), placeholder="Example: Quercus sartorii",value=st.session_state["species"],  disabled=st.session_state["species"]!=None)
            with st.expander(rtext("1_3_3_1_exp_ti"), expanded=False):
                st.markdown(rtext("1_3_3_1_exp_te"))
            if name_to_species:

                if st.session_state["species"]==None: ## the GBIF check can be made before the species is confirmed. Once the species is set, this can not be changed. 

                    # Make the API call

                    response = requests.get(f"https://api.gbif.org/v1/species/match", params={"name": name_to_species})
                    response = response.json()

                    # Check if the request was successful

                    if response["matchType"] != "NONE":
                    # Parse the JSON response

                        st.write(rtext('1_3_3_1_in_te1')+" **"+str(response['scientificName'])+"** "+rtext('1_3_3_1_in_te2'))
                        if st.button(rtext('1_3_3_1_in_bu1')):
                            st.session_state["species"] = response["scientificName"]
                            st.rerun() # force streamlit to re-run page and deactivate name_to_specie form

                    else:

                        st.write(rtext('1_3_3_1_in_te3'))
            if st.session_state["species"] is not None:
                st.markdown(rtext("1_2_2_ti"))
                st.markdown(rtext("1_2_2_te"))
                with st.form(key='GBIF_parameters', enter_to_submit=False):
                    st.slider("Select a range of values", 1900, 2020, (1970, 2020), key="GBIF_year_range")
                    st.form_submit_button("Update GBIF Range", on_click=lambda: setattr(st.session_state, 'GBIF_range', st.session_state.GBIF_year_range))

            if st.session_state["GBIF_range"] is not None:

                st.session_state.GBIF_data["start_y"]=st.session_state.GBIF_range[0]
                st.session_state.GBIF_data["end_y"]=st.session_state.GBIF_range[1]
                st.markdown(rtext("1_3_3_2_ti"))
                st.markdown(rtext("1_3_3_2_te"))
                
                region_list=[rtext("1_3_3_2_op1"), rtext("1_3_3_2_op2")]
                region = st.selectbox(
                    rtext("1_3_3_2_plac"),
                    region_list,
                    index=st.session_state["region_index"],
                    placeholder="Choose your method",
                    key="region_selection",
                    on_change=lambda: (
                    setattr(st.session_state, 'region_index', region_list.index(st.session_state.region_selection)),
                    setattr(st.session_state, 'stage', "country" if st.session_state.region_selection == rtext("1_3_3_2_op2") else "bbox_draw"),
                    )
                )
                with st.expander(rtext("1_3_3_2_exp_ti"), expanded=False):
                    st.markdown(rtext("1_3_3_2_exp_te"))
                if region== rtext("1_3_3_2_op2"): 
                    st.markdown(rtext("1_3_3_3_ti2"))
                    st.markdown(rtext("1_3_3_3_te2"))
                    st.session_state.GBIF_data["bbox"] = None
                    countries = st.multiselect("Select countries", country_names, default=st.session_state.countries,key="country_selection", on_change=lambda: setattr(st.session_state, 'countries', st.session_state.country_selection))
                if region==rtext("1_3_3_2_op1"):
                    if st.session_state.obs_edit is None:
                        st.markdown(rtext("1_3_3_3_ti1"))
                        st.markdown(rtext("1_3_3_3_te1"))
                        st.session_state.countries = []
            if st.session_state.countries or st.session_state.GBIF_data["bbox"]:
                
                if st.button(rtext("1_3_3_bu")):
                    
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
                    with st.spinner(rtext("1_3_3_load")):
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
                        # st.write('data',data)
                        try:
                            # 1. Call the pipeline
                            initial_response = GBIF(data)
    
                            output_GBIF = None

                            # 2. Determine if we have a Job ID or Immediate Results
                            # NEW LOGIC: Check if it's a dict with ONLY a runId (Job Submission)
                            if isinstance(initial_response, dict) and "runId" in initial_response and len(initial_response) == 1:
                                # Case A: Server returned a Job ID wrapped in JSON (Our new standard)
                                run_id = initial_response["runId"]
                                st.info(f"Job submitted: {run_id}. Waiting for results...")
        
                                # Poll for the result
                                output_GBIF = get_output(run_id)
                                st.success("Analysis complete!")
        
                            elif isinstance(initial_response, str):
                                # Case B: Server returned a raw string Job ID (Legacy support)
                                run_id = initial_response
                                st.info(f"Job submitted: {run_id}. Waiting for results...")
                                output_GBIF = get_output(run_id)
                                st.success("Analysis complete!")
        
                            elif isinstance(initial_response, dict):
                                # Case C: Server returned immediate JSON results (Full data, not just runId)
                                output_GBIF = initial_response
                                st.success("Analysis complete (immediate)!")
        
                            else:
                                log_and_show(f"Unexpected response type from pipeline: {type(initial_response)}")
                                raise ValueError("Invalid response type")

                            # 3. Process the result (Only runs if no exception occurred above)
                            if output_GBIF is not None:
                                # Check for errors in the result structure
                                if isinstance(output_GBIF, dict) and "error" in output_GBIF:
                                    log_and_show(f"Pipeline error: {output_GBIF['error']}")
                                else:
                                    # Extract the specific code you need
                                    target_key = "GFS_IndicatorsTool>GBIF_obs.yml@51"
                                    if isinstance(output_GBIF, dict) and target_key in output_GBIF:
                                        GBIF_output_code = output_GBIF[target_key]
                
                                        # Construct the file path
                                        file_path = f"{st.session_state.biab_dir}/output/{GBIF_output_code}/GBIF_obs.csv"
                
                                        # Read the file
                                        try:
                                            with open(file_path, "r") as obs_file:
                                                obs = pd.read_csv(obs_file, sep='\t')
                    
                                            st.session_state.obs_edit = obs
                                            st.session_state.stage = "Manipulate points"
                                            st.success("Data loaded successfully!")
                                        except FileNotFoundError:
                                            log_and_show(f"Output file not found: {file_path}")
                                        except Exception as e:
                                            log_and_show(f"Error reading output file: {e}", exc_info=True)
                                    else:
                                        # This should now only happen if the pipeline returned valid JSON but missing the key
                                        log_and_show(f"Unexpected response format from pipeline. Expected key '{target_key}' not found.")
                                        # Optional: Debug print to see what we actually got
                                        # st.code(f"Received: {output_GBIF}")

                        except BiaBError as e:
                            _show_biab_error(e)
                        except Exception as e:
                            log_and_show(f"Unexpected app error: {e}", exc_info=True)
    
    if st.session_state.obs_edit is not None:
        if st.session_state.obs_edit.empty:
            log_and_warn("No observations available.")
            st.stop()
        # Calculate the center of all point observations in total
        lats = st.session_state.obs_edit["decimallatitude"].to_numpy()
        lngs = st.session_state.obs_edit["decimallongitude"].to_numpy()
        center_lat = np.mean(lats)
        center_lng = np.mean(lngs)

        # Update session state with the center coordinates
        st.session_state.center = {"lat": center_lat, "lng": center_lng}

        if st.session_state.obs is None:

            # Confirm points to be used

            st.markdown(rtext("1_3_3_4_ti"))
            st.markdown(rtext("1_3_3_4_te"))
            if st.button(rtext("1_3_3_4_bu1")):
                st.session_state.obs = st.session_state.obs_edit
                st.session_state.poly_creation = None
                st.session_state.LC = {
                    "LC_type": None,
                    "LC_class": None,
                    "index": None
                }  
                st.session_state.area_table = None
                st.session_state.cover_maps = None
                st.rerun()


            

        if st.session_state.obs is not None:
            st.markdown(rtext("1_4_ti"))
            st.markdown(rtext("1_4_te"))
            buffer_selection= [rtext("1_4_opt1"),rtext("1_4_opt2")]
            st.session_state.poly_creation = st.selectbox(
                rtext("1_4_plac"),
                buffer_selection,
                index=st.session_state.index_poly,
                on_change=lambda: (
                    setattr(st.session_state, 'index_poly', buffer_selection.index(st.session_state.index_poly_key)),
                    setattr(st.session_state, "polyinfo", {"buffer": None, "distance": None, "polygons": None}),
                    setattr(st.session_state, "stage", "polygon_clustering" if st.session_state.index_poly_key == rtext("1_4_opt2") else st.session_state.stage),
                    setattr(st.session_state, 'stage', "Manipulate points" if st.session_state.index_poly_key == rtext("1_4_opt1") else st.session_state.stage),
                ),
                key="index_poly_key"
            )
            with st.expander(rtext("1_4_exp_ti"), expanded=False):
                st.markdown(rtext("1_4_exp_te1"))
                st.markdown(rtext("1_4_exp_te2"))

        if st.session_state.poly_creation==rtext("1_4_opt1"):
            st.markdown(rtext("1_4_2_ti"))
            st.markdown(rtext("1_4_2_te"))


            st.session_state.index_poly=0

            with st.form(key='parameters', enter_to_submit=False):
                st.number_input(rtext("1_4_2_plac1"), key="buffer_input")
                st.number_input(rtext("1_4_2_plac2"), key="distance_input")
                with st.expander(rtext("1_4_2_exp_ti"), expanded=False):
                    st.markdown(rtext("1_4_2_exp_te"))
                    st.image('images/PointsToPoly-2048x422.png', caption='Polygon creation methods')

                if st.form_submit_button(rtext("1_4_2_bu1")):
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

        if st.session_state.poly_creation==rtext("1_4_opt2"):


            st.session_state.index_poly=1
            st.markdown(rtext("1_4_1_ti"))
            st.markdown(rtext("1_4_1_te"))
            st.session_state.buffer=st.number_input(rtext("1_4_2_plac1"), value=st.session_state.buffer, key="buffer_input", on_change=lambda: setattr(st.session_state, 'buffer', st.session_state.buffer_input))
            with st.expander(rtext("1_4_1_exp_ti"), expanded=False):
                st.markdown(rtext("1_4_1_exp_te"))
            st.session_state.original_polygons=None
            

            # Reset subsequent session states
            st.session_state.LC = {
                "LC_type": None,
                "LC_class": None,
                "index": None
            }
            # st.session_state.area_table = None
            # st.session_state.cover_maps = None
            if st.session_state.buffer is not None:
                setattr(st.session_state, 'buffer', st.session_state.buffer_input)

    if st.session_state.stage=="LC":
        if st.session_state["data_source"]==rtext("1_1_opt3"):
                st.markdown(rtext("1_2_ti"))
                st.markdown(rtext("1_2_te"))
                st.number_input(rtext("1_2_plac"), step=1, min_value=1900, max_value=2020, key="baseyear_selection", value=st.session_state.baseyear, on_change=lambda: (setattr(st.session_state, 'baseyear', st.session_state.baseyear_selection)))

                with st.expander(rtext("1_2_exp_ti"), expanded=False):
                    st.markdown(rtext("1_2_exp_te"))

        if st.session_state["data_source"]==rtext("1_1_opt2") or st.session_state["data_source"]==rtext("1_1_opt1"):
            st.markdown(rtext("1_2_ti"))
            st.markdown(rtext("1_2_te"))
            st.number_input(rtext("1_2_plac"), step=1, min_value=1900, max_value=2020, key="baseyear_selection", value=st.session_state.baseyear, on_change=lambda: (setattr(st.session_state, 'baseyear', st.session_state.baseyear_selection)))

            with st.expander(rtext("1_2_exp_ti"), expanded=False):
                st.markdown(rtext("1_2_exp_te"))
        
        if st.session_state.polyinfo["polygons"] is not None and st.session_state.baseyear is not None:
            st.markdown(rtext("2_ti"))
            st.markdown(rtext("2_te"))
            LC_selection = [rtext("2_opt2"), rtext("2_opt3"), rtext("2_opt4"), rtext("2_opt1")]
            st.session_state.LC_selection = st.selectbox(
                rtext("2_plac"),
                LC_selection,
                index=st.session_state.LC_index,
                placeholder=rtext("2_desc"),
                key="LC_type_key",
                on_change=lambda: (
                    setattr(st.session_state, "LC_index", LC_selection.index(st.session_state.LC_type_key)),
                    setattr(st.session_state, "LC_class_names", None),
                    setattr(st.session_state, "LC", {"LC_class": None}),


                )
            )

            
            with st.expander(rtext("3_exp_ti"), expanded=False):
                st.markdown(rtext("3_exp_te"))

            with st.expander(rtext("3_exp1_ti"), expanded=False):
                st.markdown(rtext("3_exp1_te"))

        if st.session_state.LC_selection==rtext("2_opt3"):
            st.markdown(rtext("3_2_ti"))
            st.markdown(rtext("3_2_te"))
            LC_class = st.multiselect(rtext("3_plac"), options=LC_dict, key="LC_class", default=st.session_state.LC_class_names)
            st.session_state.LC["LC_classnames"]=LC_class

            
            st.session_state.LC["LC_class"] =  [item for lc in LC_class for item in LC_dict[lc]]
            if 2020-st.session_state.baseyear < 5:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
            else:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()

        if st.session_state.LC_selection==rtext("2_opt2"):
            st.markdown(rtext("3_1_ti"))
            st.markdown(rtext("3_1_te"))
            LC_class = st.multiselect(rtext("3_plac"), options=LC_names_simple, key="LC_class", default=st.session_state.LC_class_names)
            st.session_state.LC["LC_class"] = [values_simple[LC_names_simple.index(name)] for name in LC_class]
            if 2020-st.session_state.baseyear < 5:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
            else:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()
        
        if st.session_state.LC_selection==rtext("2_opt4"):
            st.markdown(rtext("3_3_ti"))
            st.markdown(rtext("3_3_te"))

            if 2020-st.session_state.baseyear < 5:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
            else:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()


            data={"pipeline@13":st.session_state.LC["timeseries"],"pipeline@12":st.session_state.poly_directory }
            if st.session_state.info is None or st.session_state.polyinfo["polygons"] != st.session_state.poly_old :
                try:
                    # 1. Call the API
                    info_response = LC_info(data)
    
                    # 2. Extract runId
                    if isinstance(info_response, dict) and "runId" in info_response:
                        run_id = info_response["runId"]
                    elif isinstance(info_response, str):
                        run_id = info_response
                    else:
                        log_and_show("Unexpected response from LC_info.")
                        st.stop()
    
                    # 3. Poll for results
                    st.session_state.info = get_output(run_id)
                    st.session_state.poly_old = st.session_state.polyinfo["polygons"]
                except BiaBError as e:
                    _show_biab_error(e)
                    st.stop()  
            if st.session_state.info is not None:
                LC_cum=pd.read_csv(f"{st.session_state.biab_dir}/output/{st.session_state.info['GFS_IndicatorsTool>LC_info.yml@11']}/pop_lc_sorted_cum.csv")
                # Compute individual element percentages
                elements = LC_cum.iloc[:,0] 
                cum_values = LC_cum.iloc[:,1]
                
                
                percentages = np.diff([0] + cum_values) * 100
                percentages = np.insert(percentages, 0, cum_values[0] * 100) # Initialize sums for each group
                    
                
                grouped_percentages = []
                for element, percentage in zip(elements, percentages):
                    for group, group_elements in LC_dict.items():
                        if element in group_elements:
                            found = False
                            for i, (grp, perc) in enumerate(grouped_percentages):
                                if grp == group:
                                    grouped_percentages[i] = (grp, perc + percentage)
                                    found = True
                                    break
                            if not found:
                                grouped_percentages.append((group, percentage))
                            break  # Stop checking other groups once the element is matched
                cumulative_percentage = 0
                dominant_class_names = []
                for elem, perc in grouped_percentages:
                    if cumulative_percentage >= 50:
                        break
                    dominant_class_names.append(elem)
                    cumulative_percentage += perc
                # Create stacked single bar using Plotly
                fig = go.Figure()
                element_color_map = {
                    "Rainfed cropland": "#c3b091",
                    "Irrigated cropland": "#ede6b9",
                    "Mosaic cropland (>50%) / natural vegetation (<50%)": "#f0e68c",
                    "Mosaic natural vegetation (>50%) / cropland (<50%)": "#d2b48c",
                    "Tree cover, broadleaved, evergreen, closed to open (>15%)": "#1b5e20",
                    "Tree cover, broadleaved, deciduous, closed to open (>15%)": "#2e7d32",
                    "Tree cover, needleleaved, evergreen, closed to open (>15%)": "#388e3c",
                    "Tree cover, needleleaved, deciduous, closed to open (>15%)": "#4caf50",
                    "Tree cover, mixed leaf type (broadleaved and needleleaved)": "#2e8b57",
                    "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)": "#3cb371",
                    "Tree cover, flooded, fresh or brackish water": "#006400",
                    "Tree cover, flooded, saline water": "#228b22",
                    "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)": "#fbc02d",
                    "Grassland": "#fff176",
                    "Shrub or herbaceous cover, flooded, fresh-saline or brackish water": "#2196f3",
                    "Urban": "#d32f2f",
                    "Shrubland": "#8b4513",
                    "Lichens and mosses": "#c0b283",
                    "Sparse vegetation (tree, shrub, herbaceous cover)": "#d9caa3",
                    "Bare areas": "#9e9e9e",
                    "Water": "#2196f3",
                    "Permanant Ice and Snow": "#bdbdbd"
                }
                
            
                for elem, perc in grouped_percentages:

                    color = element_color_map.get(elem, "gray")
                    name = elem
                    fig.add_trace(go.Bar(
                        x=[perc], y=["Land cover class"],  # one bar
                        orientation='h',
                        name=name,
                        marker=dict(color=color),
                        hovertemplate=f"{name}: {perc:.2f}%<extra></extra>"
                    ))
                fig.add_vline(
                    x=50,
                    line=dict(color="red", width=2, dash="solid"),
                    layer="above",  # draw *behind* bars
                    annotation_position="top",
                    annotation_text="50% cutoff"
                )
                fig.update_layout(
                    barmode='stack',
                    title=rtext("3_3_plot_ti"),
                    xaxis_title=rtext("3_3_plot_xax"),
                    showlegend=False,
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                LC_class=st.multiselect(rtext("3_plac"), options=LC_dict, key="LC_class", default=dominant_class_names)
                
                st.session_state.LC["LC_class"] = [item for lc in LC_class for item in LC_dict[lc]]
                st.session_state.LC["LC_classnames"]=LC_class

                if 2020-st.session_state.baseyear < 5:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 2020-st.session_state.baseyear+1).astype(int).tolist()
                else:
                    st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2020, 5).astype(int).tolist()
    
        if st.session_state.LC_selection==rtext("2_opt1"):
            st.markdown(rtext("3_4_ti"))
            st.markdown(rtext("3_4_te"))
            st.session_state.LC["LC_class"]=["Treecover"]
            st.session_state.LC_classnames=["Treecover"]
            if 2023-st.session_state.baseyear < 5:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2023, 2023-st.session_state.baseyear+1).astype(int).tolist()
            else:
                st.session_state.LC["timeseries"] = np.linspace(st.session_state.baseyear, 2023, 5).astype(int).tolist()
        
        
    
        if st.session_state.LC["LC_class"] !=None:

            if st.button(rtext("3_bu1")):
                st.session_state.run_id = str(uuid.uuid4())
                if st.session_state.LC_selection==rtext("2_opt2"):
                    LC_class_flattened = []

                    def flatten_list(nested_list):
                        for item in nested_list:
                            if isinstance(item, list):
                                flatten_list(item)
                            else:
                                LC_class_flattened.append(item)

                    flatten_list(st.session_state.LC["LC_class"])
                    # The flattened list
                    st.session_state.LC["LC_class"] = LC_class_flattened
                setattr(st.session_state, "LC_class_index",  st.session_state.LC["LC_class"])
                if st.session_state.LC_selection==rtext("2_opt2") or st.session_state.LC_selection==rtext("2_opt3"):
                    setattr(st.session_state,"LC_class_names",  LC_class)
                with st.spinner(rtext("3_load")):
                    try:
                        timeseries = st.session_state.LC["timeseries"]
                        if st.session_state.LC_selection==rtext("2_opt2") or st.session_state.LC_selection==rtext("2_opt3") or st.session_state.LC_selection==rtext("2_opt4"):
                            data = {
                                "pipeline@197": st.session_state.poly_directory,
                                "pipeline@198": timeseries,
                                "pipeline@199": st.session_state.LC["LC_class"]
                            }
                            st.session_state.area=LC_area(data)
                        if st.session_state.LC_selection==rtext("2_opt1"):
                            data = {
                                "pipeline@197": st.session_state.poly_directory,
                                "pipeline@204": timeseries
                            }
                            st.session_state.area= TC_area(data)
                            
                        # Reset subsequent session states
                        st.session_state.area_table = None
                        st.session_state.cover_maps = None
                        
                        if "area" in st.session_state:
                            # Extract the runId string from the dictionary returned by LC_area
                            area_response = st.session_state.area
                            if isinstance(area_response, dict) and "runId" in area_response:
                                run_id = area_response["runId"]
                            elif isinstance(area_response, str):
                                run_id = area_response
                            else:
                                log_and_show("Unexpected response format from LC_area pipeline.")
                                st.stop()
                        
                            # Now pass the string run_id to get_output
                            output_area = get_output(run_id)
                        
                            area_output_code=output_area["GFS_IndicatorsTool>pop_area_by_habitat.yml@200"]
                            if st.session_state.LC_selection==rtext("2_opt1"):
                                cover_output_code=output_area["GFS_IndicatorsTool>get_TCY.yml@203"]
                                st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                            if st.session_state.LC_selection==rtext("2_opt3"):
                                st.session_state.LC_classnames= st.session_state.LC["LC_classnames"]
                                cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                                st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                            if st.session_state.LC_selection==rtext("2_opt2"):
                                st.session_state.LC_classnames=[LC_names_simple[values_simple.index(value)] for value in st.session_state.LC["LC_class"] if value in values_simple]
                                cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                                st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                            pop_area=f"/output/{area_output_code}/pop_habitat_area.tsv"
                            if st.session_state.LC_selection ==rtext("2_opt4"):
                                
                                cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
                                st.session_state.cover_maps=f"/output/{cover_output_code}/cover maps"
                                LC_class = json.load(open(f"{st.session_state.biab_dir}/output/{cover_output_code}/output.json"))["lc_classes"]
                                
                                if isinstance(LC_class, int):
                                    LC_class=[LC_class]
                                st.session_state.LC_classnames = st.session_state.LC["LC_classnames"]
                            area_file_path = f"{st.session_state.biab_dir}/output/{area_output_code}/pop_habitat_area.tsv"
                            st.session_state.area_table = pd.read_csv(area_file_path, sep='\t')
                    except BiaBError as e:
                        _show_biab_error(e)
                        st.stop()

    if st.session_state.area_table is not None:
        rel_habitat_change_table = st.session_state.area_table.copy()
        for i in range(1, st.session_state.area_table.shape[1]):  # Start from the second column (index 1)
            rel_habitat_change_table.iloc[:, i] = (st.session_state.area_table.iloc[:, i] / st.session_state.area_table.iloc[:, 1] * 100) - 100
        st.session_state.rel_habitat_change_table = rel_habitat_change_table
        st.session_state.NC= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatNC.tif"
        st.session_state.GAIN= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatGAIN.tif"
        st.session_state.LOSS= f"{st.session_state.biab_dir}{st.session_state.cover_maps}/HabitatLOSS.tif"


        st.session_state["upload"] = False
        st.session_state.default_dens=None
        st.session_state.default_nenc=None
        st.session_state.properties=None
        if st.button("View results"):
            st.switch_page("pages/Output_display.py")
    
    # add 2 empty lines for readability
    st.markdown('')
    st.markdown('')

with col2:
    if st.session_state.stage=="bbox_draw":
        
        
        mapbbox()
    if st.session_state.stage=="Manipulate points":
        edit_points()
    if st.session_state.stage=="polygon_clustering":
        polygon_clustering()
    if st.session_state.stage=="manual_polygon_creation":
        manual_polygon_addition()
    if st.session_state.stage=="LC":
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

        # Add the polygons to the map
        fg = folium.FeatureGroup(name="Polygons")
        fg.add_child(folium.GeoJson(st.session_state.polyinfo["polygons"], popup=folium.GeoJsonPopup(fields=["name"])))
        # Display the map
        st.session_state.output2 = st_folium(m, feature_group_to_add=fg, use_container_width=True)

