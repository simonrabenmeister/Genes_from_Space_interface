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
    _show_biab_error,
    polygon_bounds,
    compute_fit_zoom_from_bounds,
    load_shapefile_zip
)
import glasbey
from logging_config import log_and_show, log_and_warn
import uuid
import os
import plotly.graph_objects as go
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
from functions import manual_polygon_addition, read_occurrence_file, compute_fit_zoom
import csv
import io
st.set_page_config(page_title="Genes From Space", page_icon="🌍", layout="wide")

# !! Hide a page
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
if "obs_final" not in st.session_state:
    st.session_state.obs_final = None
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
if "selection" not in st.session_state:
    st.session_state.selection = None  # Default selection for species
if "species_type" not in st.session_state:
    st.session_state.species_type = None  # Default species type
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
if "text" not in st.session_state:
    st.session_state.text = None  # Default text for species information
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
if "obs_link" not in st.session_state:
    st.session_state.obs_link = None    
if "polygon_addition" not in st.session_state:
    st.session_state.polygon_addition = None
st.session_state.run_dir= os.path.join(f"{st.session_state.biab_dir}/userdata/interface_polygons/", st.session_state.run_id)
height_source=streamlit_js_eval(js_expressions='screen.height', key = 'SCR')
if height_source is not None:
    st.session_state.height=int(height_source*0.6)
if "data_source" not in st.session_state:
    st.session_state.data_source = None  # Default data source index
if "scroll_image_container" not in st.session_state:
    st.session_state.scroll_image_container = False
if "obs_link" not in st.session_state:
    st.session_state.obs_link = None  # Default observation link
##Load necessary functions, files etc
texts = pd.read_csv("texts.csv").set_index("id")
country_names = pd.read_csv("countries.txt", header=None)[0].to_numpy()  # Assuming the file has no header

LC_dict = {
    "Cropland": [10, 11, 12],
    "Cropland, irrigated or post-flooding": [20],
    "Tree cover, broadleaved, evergreen": [50],
    "Tree cover, broadleaved, deciduous": [60, 61, 62],
    "Tree cover, needleleaved, evergreen": [70, 71, 72],
    "Tree cover, needleleaved, deciduous": [80, 81, 82],
    "Tree cover, mixed leaf type (broadleaved and needleleaved)": [90],
    "Shrubland": [120, 121, 122],
    "Grassland": [130],
    "Sparse vegetation (tree, shrub, herbaceous cover)": [150, 151, 152, 153],
    "Tree cover, flooded, fresh or brackish water": [160],
    "Tree cover, flooded, saline water": [170],
    "Shrub or herbaceous cover, flooded, fresh/saline/brakish water": [180],
    "Urban": [190],
    "Bare areas": [140, 200, 201, 202],
    "Water": [210],
    "Permanant Ice and Snow": [220],

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
            padding-top: 0rem;
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

    st.session_state.lan = st.radio("Select Language", ["en", "sp"], key="language_selection")
    # Display the session ID for user confirmation when debugging
    st.divider()
    st.caption(
        f"**Debug Session ID:** `{st.session_state.get('session_id', 'Loading...')}`"
        )

def rtext(id):
    return texts.loc[id, st.session_state.lan].replace("\\n", "\n")


def render_scroll_image_container():
    components.html(
        f"""
        <script>
            function scrollContainer(dummy) {{
                var containers = window.parent.document.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]');
                containers.forEach(function(c) {{
                    if (c.innerText.includes("")) {{}}  // placeholder, see note below
                }});
                // Fallback: scroll all bordered containers with overflow
                var scrollables = window.parent.document.querySelectorAll('div[style*="overflow"]');
                scrollables.forEach(function(el) {{
                    el.scrollTop = el.scrollHeight;
                }});
            }}
            scrollContainer({st.session_state.height});
        </script>
        """,
        height=0,
    )
col1, col2= st.columns(2)

with col1.container( border=False, key="container1", height=st.session_state.height):
### 1st step: Set how to provide species input data

    st.markdown(rtext("1_ti"))
    st.markdown(rtext("1_te"))

### Choose data source

    st.markdown(rtext("1_1_ti"))
    st.markdown(rtext("1_1_te"))
    selection=[rtext("1_1_opt1"), rtext("1_1_opt2"), rtext("1_1_opt3")]
    options=["Get species observation points from GBIF", "Upload your own species observation points", "Upload your own polygons of population distribution"]

    st.session_state["data_source"] = st.selectbox("Which data source would you like to use?", options, index=None, key="data_source_key",
            on_change=lambda: (
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
            setattr(st.session_state, "baseyear", None),
            setattr(st.session_state, "stage", "start"),
            )
        )

    
    if  st.session_state["data_source"]== "Get species observation points from GBIF":
        st.session_state.selection=["Dendrocoptes medius", "Tetrao urogallus", "Nasalis larvatus"]
        st.session_state.text = "The GBIF method will source species observation points from the Global Biodiversity Information Facility (GBIF) database. By providing the Species name and a range of years, the system will automatically retrieve the relevant observation points for that species within the specified timeframe."
    if st.session_state["data_source"]== "Upload your own polygons of population distribution":
        st.session_state.selection=["Zea perennis", "Persea cinerascens"]
        st.session_state.obs_final=None
        st.session_state.text = "The polygon method allows you to upload your own polygons representing the population distribution of a species. You can either upload a GeoJSON file containing the polygons, upload a .shp file or draw them directly on the map. This method is useful when you have specific geographic areas of interest for your species."
    if st.session_state["data_source"]=="Upload your own species observation points":
        st.session_state.selection=[ "Diceros bicornis"]
        st.session_state.text = "The point method allows you to upload your own species observation points in CSV or TSV format. This method is useful when you have specific observation data for your species that you want to analyze."

    st.session_state.selection
    if st.session_state.selection is not None:
        st.markdown(st.session_state.text)
        st.session_state["species_type"] = st.selectbox(
            rtext("1_1_in"), st.session_state.selection, 
            placeholder=rtext("1_1_plac"),
            index=None,
            key="data_type_key",
            on_change=lambda: (
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
            setattr(st.session_state, "baseyear", None),
            setattr(st.session_state, "stage", "Manipulate points"),
            )
        )

    if st.session_state["species_type"] is not None:

        if st.session_state["species_type"] == "Diceros bicornis":
            st.markdown("#### Black rhinoceros (Diceros bicornis), South Africa")
            st.image("images/diceros_bicornis.jpg", width=400)
            st.markdown(
                "- Status: Black rhinoceros is categorized as Critically Endangered on the IUCN Red List (IUCN, 2006). "
                "About a third of the population in South Africa is in protected areas or private reserves (Brooks, 2001). "
                "Declining population productivity has been attributed to negative habitat changes and a reduction in carrying capacity.\n"
                "- Habitat: Savanna and shrubland are the major habitat types identified for the species."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/Diceros_bicornis_SA.csv"

        elif st.session_state["species_type"] == "Persea cinerascens":
            st.markdown("#### Wild avocado (Persea cinerascens), Mexico")
            st.image(
                "images/persea_cinerascens.jpg",
                width=400,
            )
            st.markdown(
                "- Importance: the wild relatives of modern-day crops (crop wild relatives) harbor an important proportion of "
                "crops' genetic diversity (Maxted et al., 2006). In Mexico, crop wild relatives are threatened mainly by LULC "
                "change and several species (spp.) are endangered, some critically (Goettsch et al., 2021).\n"
                "- Habitat: a wild avocado growing among the trees composing cloud forests, Mexico's most biodiverse terrestrial "
                "ecosystem type per unit area (Conabio, 2023; Rojas-Soto et al., 2012). Its habitat is suspected to have decreased "
                "or disappeared due to rapid land use change. It inhabits remote locations that are challenging to visit."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/Pcinerascens_Observations4326.geojson"

        elif st.session_state["species_type"] == "Tetrao urogallus":
            st.markdown("#### Western capercaillie (Tetrao urogallus), Switzerland")
            st.image("images/Western_Capercaillie.jpg", width=400)
            st.markdown(
                "- Status: nationally threatened in Switzerland with a declining trend. The species is found in 5 separated "
                "populations, and one of the main causes of the decline is the loss and fragmentation of suitable habitat.\n"
                "- Characteristics: home range < 5 km², population density 5-10 individuals/km².\n"
                "- Habitat: coniferous and mixed forests."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/Tetrao_urogallus_CH_GBIF.csv"

        elif st.session_state["species_type"] == "Dendrocoptes medius":
            st.image("images/dendrocopets_medius.jpg", width=400)
            st.markdown("#### Middle spotted woodpecker (Dendrocoptes medius), Switzerland")
            st.markdown(
                "- Habitat: mature deciduous forest, preferably mixed oak forest with rough bark and dead wood.\n"
                "- Importance and status: populations have declined in several regions of Switzerland, and habitat loss is the "
                "main threat in the country. Small and isolated populations are also more vulnerable to population fluctuations "
                "and local extinction."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/Dendrocoptes_medius_CH_GBIF.csv"

        elif st.session_state["species_type"] == "Zea perennis":
            st.markdown("#### Perennial teosinte (Zea perennis), Mexico")
            st.image(
                "images/zea_perennis.jpg",
                caption="https://acsess.onlinelibrary.wiley.com/doi/10.2135/cropsci2016.10.0855",
                width=400,
            )
            st.markdown(
                "- Importance: the wild relatives of modern-day crops (crop wild relatives) harbor an important proportion of "
                "crops' genetic diversity (Maxted et al., 2006). In Mexico, crop wild relatives are threatened mainly by LULC "
                "change and several species (spp.) are endangered, some critically (Goettsch et al., 2021).\n"
                "- Habitat: this species has only been recorded in two locations in Western Mexico (González et al., 2018), "
                "although species distribution models suggest it may occur in other localities within the region, where genetic "
                "differentiation is expected due to environmental and historical differences (Tobón-Niedfeldt et al., 2022). "
                "Based on DNA data, the Ne of both documented Z. perennis populations is below 500 (Rivera-Rodríguez et al., 2023)."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/ZeaPerennisSDMWGS4326.geojson"

        elif st.session_state["species_type"] == "Nasalis larvatus":
            st.markdown("#### Proboscis monkey (Nasalis larvatus), Borneo")
            st.image("images/nasalis_larvatus.jpg", width=400)
            st.markdown("- Status: the species is listed as Endangered. It has undergone extensive population reductions across its "
                "range, and ongoing hunting and habitat destruction continue to threaten most populations.\n"
                "- Habitat: riparian-riverine forests and coastal lowland forest, including mangroves, peat swamp, and "
                "freshwater swamp forest (Boonratana, 2000)."
            )
            obs_link = "/home/ubuntu/Genes_from_Space_interface/Example_files/Nasalis_larvatus_Borneo_GBIF.csv"
        if st.session_state["data_source"]=="Upload your own polygons of population distribution": # Upload your own polygons

            if st.session_state.polyinfo["polygons"] is None or st.session_state.obs_link != obs_link:
                st.session_state.obs_link = obs_link
                try:
                    with open(obs_link, "r", encoding="utf-8") as polygon_file:
                        st.session_state.polyinfo["polygons"] = geojson.load(polygon_file)
                    st.session_state.original_polygons = st.session_state.polyinfo["polygons"]
                    colors = glasbey.create_palette(
                        palette_size=len(st.session_state.original_polygons["features"]),
                        colorblind_safe=True,
                        cvd_severity=100
                    )
                    for i, feature in enumerate(st.session_state.original_polygons["features"]):
                        feature["properties"]["style"] = {}
                        feature["properties"]["style"]["color"] = colors[i]
                except Exception as e:
                    log_and_show(f"Error reading the GeoJSON file: {e}", exc_info=True)

                st.session_state.stage = "LC"

            if st.session_state.polyinfo["polygons"] is not None:
                if st.session_state.polyinfo["polygons"] is not None:
                    lat_min, lat_max, lng_min, lng_max = polygon_bounds(st.session_state.polyinfo["polygons"])

                    # Center on the bounding box of all polygons
                    center_lat = (lat_min + lat_max) / 2
                    center_lng = (lng_min + lng_max) / 2
                    st.session_state.center = {"lat": center_lat, "lng": center_lng}

                    # Zoom level that fits every polygon on screen
                    st.session_state.zoom = compute_fit_zoom_from_bounds(
                        lat_min, lat_max, lng_min, lng_max,
                        map_width_px=st.session_state.get("map_width", 800),
                        map_height_px=st.session_state.get("height", 500),
                    )
                run = os.path.join(st.session_state.run_dir, "updated_polygons.geojson")
                os.makedirs(os.path.dirname(run), exist_ok=True)  # Ensure the directory exists
                with open(run, "w") as f:
                    geojson.dump(st.session_state.polyinfo["polygons"], f)
                st.session_state.poly_directory = os.path.join(
                    "/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson"
                )
                
            if st.session_state.polyinfo["polygons"] is not None:
                st.markdown("If you want to add more polygons to the map, click the button below. You will be redirected to a new page where you can draw polygons on the map.")
                if st.button("add polygons to map"):
                    st.session_state.stage = "manual_polygon_creation"
                    st.session_state.polygon_addition = st.session_state.original_polygons
                    st.rerun()
        if st.session_state["data_source"]=="Get species observation points from GBIF" or st.session_state["data_source"]=="Upload your own species observation points": # Upload your own points
            

            if obs_link is not None and st.session_state.obs is None:

                st.session_state.obs = pd.read_csv(obs_link, sep=None, engine='python')  # Use 'python' engine to auto-detect separator


            if st.session_state.obs is not None:
                
                # Calculate the center of all point observations in total
                lats = st.session_state.obs["decimallatitude"].to_numpy()
                lngs = st.session_state.obs["decimallongitude"].to_numpy()
                center_lat = np.mean(lats)
                center_lng = np.mean(lngs)

                # Update session state with the center coordinates
                st.session_state.center = {"lat": center_lat, "lng": center_lng}
                
                # Update session state with a zoom level that fits all points on screen
                st.session_state.zoom = compute_fit_zoom(
                    lats, lngs,
                    map_width_px=st.session_state.get("map_width", 800),
                    map_height_px=st.session_state.get("height", 500),
                    )


                if st.session_state.obs is None:

                    # Confirm points to be used

                    st.markdown(rtext("1_3_3_4_ti"))
                    st.markdown(rtext("1_3_3_4_te"))

            

        if st.session_state.obs_final is not None:

            
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
                    setattr(st.session_state, "original_polygons", None),
                    setattr(st.session_state, "buffer", None),
                    setattr(st.session_state, "distance", None),
                    setattr(st.session_state, "stage","polygon_clustering"),
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
                st.number_input(rtext("1_4_2_plac1"),min_value=0.5, index=None, key="buffer_input")
                st.number_input(rtext("1_4_2_plac2"), key="distance_input")
                with st.expander(rtext("1_4_2_exp_ti"), expanded=False):
                    st.markdown(rtext("1_4_2_exp_te"))
                    st.image('images/PointsToPoly-2048x422.png', caption='Polygon creation methods')

                if st.form_submit_button(rtext("1_4_2_bu1")):

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
                    st.session_state.stage="polygon_clustering"
                    
                    
            
            
            
            if st.session_state.original_polygons is not None:
                st.write("If you are satisfied with the polygons, Press Confirm Polygons. If you want to add manually drawn Polygons to the map, Press Add Polygons to Map.")
                bu1, bu2 = st.columns(2)
                with bu1:
                    if st.button(rtext("1_4_2_bu2")):
                        st.session_state.polyinfo["polygons"] = st.session_state.original_polygons
                        st.session_state.stage = "LC"
                        st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
                        st.write(f"Saving polygons to: {st.session_state.poly_directory}")
                        os.makedirs(os.path.dirname(f"{st.session_state.biab_dir}{st.session_state.poly_directory}"), exist_ok=True)
                        with open(f"{st.session_state.biab_dir}{st.session_state.poly_directory}", "w") as f:
                            geojson.dump(st.session_state.polyinfo["polygons"], f)
                        st.success("Polygons saved successfully.")
                        del st.session_state.polygon_addition
                        st.rerun()

                with bu2:
                    if st.button("add polygons to map"):
                        st.session_state.stage = "manual_polygon_creation"
                        st.session_state.polygon_addition = st.session_state.original_polygons
                        st.rerun()
                
        if st.session_state.poly_creation==rtext("1_4_opt2"):
            st.session_state.index_poly=1
            st.markdown(rtext("1_4_1_ti"))
            st.markdown(rtext("1_4_1_te"))
            st.session_state.original_polygons=None
            

            # Reset subsequent session states
            st.session_state.LC = {
                "LC_type": None,
                "LC_class": None,
                "index": None
            }
            # st.session_state.area_table = None
            # st.session_state.cover_maps = None


    if st.session_state.stage=="LC":
        if st.session_state["data_source"]=="Upload your own polygons of population distribution":
                st.markdown(rtext("1_2_ti"))
                st.markdown(rtext("1_2_te"))
                st.number_input(rtext("1_2_plac"), step=1, min_value=2003, max_value=2025, key="baseyear_selection", value=st.session_state.baseyear, on_change=lambda: (setattr(st.session_state, 'baseyear', st.session_state.baseyear_selection)))

                with st.expander(rtext("1_2_exp_ti"), expanded=False):
                    st.markdown(rtext("1_2_exp_te"))

        if st.session_state["data_source"]==rtext("1_1_opt2") or st.session_state["data_source"]==rtext("1_1_opt1"):
            st.markdown(rtext("1_2_ti"))
            st.markdown(rtext("1_2_te"))
            st.number_input(rtext("1_2_plac"), step=1, min_value=2003, max_value=2020, key="baseyear_selection", value=st.session_state.baseyear, on_change=lambda: (setattr(st.session_state, 'baseyear', st.session_state.baseyear_selection)))

            with st.expander(rtext("1_2_exp_ti"), expanded=False):
                st.markdown(rtext("1_2_exp_te"))
        
        if st.session_state.polyinfo["polygons"] is not None and st.session_state.baseyear is not None:
            st.markdown(rtext("2_ti"))
            st.markdown(rtext("2_te"))
            LC_selection = [ rtext("2_opt4"), rtext("2_opt2"), rtext("2_opt1")]#removed rtext("2_opt1") since get_TCY is not working properly.
            
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

            lc_table = pd.DataFrame({
                "Class": LC_names_simple,
                "Include": [None for name in LC_names_simple],
            })

            edited_lc_table = st.data_editor(
                lc_table,
                column_config={
                    "Class": st.column_config.TextColumn(disabled=True),
                    "Include": st.column_config.CheckboxColumn(default=False),
                },
                width="content",
                hide_index=True,
                key="LC_class_editor",
            )

            # Get selected class names, then map back to underlying values
            
            if edited_lc_table["Include"].any():
                edited_lc_table["Include"] = edited_lc_table["Include"].astype(bool)

                LC_class = edited_lc_table.loc[edited_lc_table["Include"] == True, "Class"].tolist()
                st.session_state.LC["LC_class"] = [values_simple[LC_names_simple.index(name)] for name in LC_class]

                # Persist current selection so next rerun starts from it, not the original default
                st.session_state.LC["LC_class_names_current"] = LC_class
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
                    "Cropland": "#ffff64",
                    "Cropland, irrigated or post-flooding": "#aaf0f0",
                    "Tree cover, broadleaved, evergreen": "#006400",
                    "Tree cover, broadleaved, deciduous": "#00a000",
                    "Tree cover, needleleaved, evergreen": "#003c00",
                    "Tree cover, needleleaved, deciduous": "#285000",
                    "Tree cover, mixed leaf type (broadleaved and needleleaved)": "#788200",
                    "Shrubland": "#966400",
                    "Grassland": "#ffb400",
                    "Sparse vegetation (tree, shrub, herbaceous cover)": "#ffebaf",
                    "Tree cover, flooded, fresh or brakish water": "#00785a",
                    "Tree cover, flooded, saline water": "#009678",
                    "Shrub or herbaceous cover, flooded, fresh/saline/brakish water": "#00dc82",
                    "Urban": "#c31400",
                    "Bare areas": "#fff5d7",
                    "Water": "#0046c8",
                    "Permanant Ice and Snow": "#ffffff",
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
                    annotation_text="50%"
                )
                fig.update_layout(
                    barmode='stack',
                    title=rtext("3_3_plot_ti"),
                    xaxis_title=rtext("3_3_plot_xax"),
                    showlegend=False,
                    height=300
                )
                int_plot=st.plotly_chart(fig, width="stretch", on_select="rerun", selection_mode="points", )
                points = int_plot["selection"]["points"]
                class_selection = [p["curve_number"] for p in points]
                st.session_state.LC_class=[grouped_percentages[i][0] for i in class_selection]

                if st.session_state.LC_class:
                    table_data = [
                        {"Land cover class": lc, "Codes": ", ".join(str(c) for c in LC_dict[lc])}
                        for lc in st.session_state.LC_class
                    ]
                    st.table(table_data)
                else:
                    st.info("Please select land cover classes from the plot above to see their corresponding codes.") 
                
                
                st.session_state.LC["LC_class"] = [item for lc in st.session_state.LC_class for item in LC_dict[lc]]
                st.session_state.LC["LC_classnames"]=st.session_state.LC_class


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
        
        
    
        if st.session_state.LC["LC_class"] is not None and st.session_state.LC["LC_class"] != []:

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
            st.switch_page("pages/Results.py")
    
    # add 2 empty lines for readability
    st.markdown('')
    st.markdown('')

if st.session_state.get("scroll_image_container"):
    render_scroll_image_container()
    st.session_state.scroll_image_container = False

with col2.container( border=False, key="container", height=st.session_state.height):
    if st.session_state.stage=="bbox_draw":
        
        
        mapbbox()
    if st.session_state.stage=="Manipulate points" and st.session_state.obs is not None:
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
        st.session_state.output2 = st_folium(m, feature_group_to_add=fg, width="stretch")

