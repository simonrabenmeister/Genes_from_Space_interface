import streamlit as st

from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import pandas as pd
import folium
from streamlit_folium import st_folium
import geojson
import requests
import time
from streamlit_plotly_events import plotly_events
import geopandas as gpd
from folium.plugins import Draw
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import glasbey
import seaborn as sns
import numpy as np
from streamlit_map import *
import plotly.express as px
import folium.plugins as plugins




start_y=None
end_y=None  
species=None
buffer=None
distance=None
GBIF_directory=None
obs=None
bbox=None
area=None
country=None
default_nenc=None
poly_directory=None
area_table=None
pop_size_table=None
title=None
Indicator=None
NEs=None
    
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



def GBIF():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>GBIF.json/run"

    data = {
        "pipeline@170": species,
        "pipeline@171": country,
        "pipeline@172": start_y,
        "pipeline@173": end_y,
        "pipeline@174": bbox
    }
    headers = {"Content-Type": "application/json"}

    st.session_state.GBIF = requests.post(url, json=data, headers=headers)

def polygon():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>get_polygon.json/run"

    data = {
        "pipeline@201": GBIF_directory,
        "pipeline@202": buffer,
        "pipeline@203": distance,
        "pipeline@204": []

    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response

def LC_area():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>LC_area.json/run"

    data = {
        "pipeline@197": st.session_state.poly_directory,
        "pipeline@198": timeseries,
        "pipeline@199": LC_class
    }
    headers = {"Content-Type": "application/json"}

    st.session_state.area = requests.post(url, json=data, headers=headers)


def TC_area():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>TC_area.json/run"

    data = {
        "pipeline@197": poly_directory,
        "pipeline@204": timeseries,
    }
    headers = {"Content-Type": "application/json"}

    st.session_state.area = requests.post(url, json=data, headers=headers)


def Indicators():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>Indicators.json/run"

    data = {
        "GFS_IndicatorsTool>get_Indicators_copy.yml@183|lc_classes": ",".join(map(str, LC_class)),
        "pipeline@189": title,
        "pipeline@201": cover_maps,
        "pipeline@202": edited_poly,
        "pipeline@203": pop_area
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response

def get_output(response_code):
    st.write("Response code: ", response_code)
    while True:
        max_retries = 12
        history = None  # Initialize history variable
        for attempt in range(max_retries):
            try:
                history = requests.get(f"http://localhost/api/history").json()
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
        if history is None:
            st.error("Failed to retrieve history after multiple attempts.")
            return None
        status = [entry["status"] for entry in history if entry["runId"] == response_code]
        if status[0] != "running":
            break
    if status[0] == "completed":
        output_GBIF = requests.get(f"http://localhost/api/{response_code}/outputs").json()
        return output_GBIF
    



@st.fragment
def mapgeojson(poly_file):
##Upload the polygon file
        #Get the center of the Polygon for Map display
        def get_bounding_box(geom):
            coords = np.array(list(geojson.utils.coords(geom)))
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
        bbox=get_bounding_box(poly_file)
        #st.write (bbox)
        y=bbox[2]-(bbox[2]-bbox[0])/2
        x=bbox[3]-(bbox[3]-bbox[1])/2
        #st.write (x,y)

        #set Map center to the center of the polygon
        if "center" not in st.session_state:
            st.session_state["center"] = [x,y]  # Default center for the map
        #set Map zoom level
        if "zoom" not in st.session_state:
            st.session_state["zoom"] = 6 # Default zoom level

        # if poly_file != st.session_state.poly: #reset if new file is uploaded
        #     st.session_state.poly=poly_file
        #     st.session_state["center"] = [x,y]
        #     st.session_state["zoom"] = 6

##Create the map
        m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
        fg = folium.FeatureGroup(name="Markers")
        fg.add_child(folium.GeoJson(poly_file))

        ##Display the map
        st_folium(
                m,
                center=st.session_state["center"],
                zoom=st.session_state["zoom"],
                key="new",
                feature_group_to_add=fg,
                height=400,
                width=700,
                
            )
    

@st.fragment
def mapbbox():
    #create the map
    m = folium.Map(location=[0,0], zoom_start=2)
    draw = Draw(export=False,   draw_options={
        'polyline': False,  # Disable polyline
        'polygon': False,    # Enable polygon
        'circle': False,    # Disable circle
        'rectangle': True,  # Enable rectangle
        'marker': False,     # Enable marker
        'circlemarker': False  # Disable circle marker
    },
    edit_options={
        'edit': False,   # Enable editing of drawn shapes
        'remove': True  # Enable deleting of drawn shapes
    })
    draw.add_to(m)
    
    def get_bounding_box(geom):
        coords = np.array(list(geojson.utils.coords(geom)))
        
        return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
    #display the map
    output = st_folium(m, width=700, height=500)
    #get the bounding box of the last clicked polygon
    if output["last_active_drawing"] is not None:
        geometry=output["last_active_drawing"]["geometry"]
        st.session_state.bbox =  get_bounding_box(geometry)


with st.form(key='my_form', enter_to_submit=False):

    species=st.text_input("Species Name", placeholder="Example: Quercus sartorii")
    start_y=st.number_input("Start year", value=None, step=1, min_value=1900, max_value=2021)
    end_y=st.number_input("End year", value=None, step=1, min_value=1900, max_value=2021)
    time.sleep(1)
    st.form_submit_button("Submit")


if end_y:
    mapbbox()

    if st.button("Confirm Bounding Box"):
        with st.spinner("Wait for it..."): 
            bbox = st.session_state.bbox
            GBIF()
            GBIF_response = st.session_state.GBIF
            output_GBIF = get_output(GBIF_response.text)
            GBIF_output_code=output_GBIF["data>getObservations.yml@169"]
            GBIF_directory=f"/output/{GBIF_output_code}/obs_data.tsv"
            st.write("Data: ",  GBIF_directory)
            obs_file = open(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{GBIF_output_code}/obs_data.tsv")
            obs = pd.read_csv(obs_file, sep='\t')
            st.session_state.obs = obs

@st.fragment
def load_polygons():

    obs = st.session_state.obs

    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add the observations to the map
    fg = folium.FeatureGroup(name="Markers")
    for i, row in obs.iterrows():
        folium.CircleMarker(
            location=[row["decimal_latitude"], row["decimal_longitude"]],
            radius=6,
            color='blue',
            fill_opacity=1,
            fill=True,
            fill_color='lightblue'
        ).add_to(fg)

    # Add the Draw tool to the map
    draw = Draw(export=False, draw_options={
        'polyline': True,
        'polygon': True,
        'circle': True,
        'rectangle': True,
        'marker': True,
        'circlemarker': True
    }, edit_options={
        'edit': True,
        'remove': True
    })
    draw.add_to(m)

    # Display the map
    if "polygons" not in st.session_state:
        output = st_folium(m, width=700, height=500, feature_group_to_add=fg)       
    else:
        fg2 = folium.FeatureGroup(name="Markers")
        fg2.add_child(folium.GeoJson(st.session_state.polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density"])))
        output = st_folium(m, width=700, height=500, feature_group_to_add=[fg, fg2])
    # Create circle object for points
    if st.button("Remove Polygons"):
        del st.session_state["polygons"]
        size = None
        st.rerun(scope="fragment")

    obs['geometry'] = obs.apply(lambda row: Point((row["decimal_longitude"], row["decimal_latitude"])), axis=1)
    geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
    new_df = geo_df.set_crs(epsg=4326)
    new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)
    with st.form(key='buffer', enter_to_submit=False):
        size = st.number_input("Buffer", value=None)
        if  st.form_submit_button("Draw Polygon"):
            circles = new_df['geometry'].buffer(size)
            obs['circles'] = circles.to_crs(epsg=4326)
            # Group the circles into clusters depending on drawn polygons
            clusters = pd.DataFrame()
            for i in range(0, len(output["all_drawings"])):
                polygon_coords = output["all_drawings"][i]["geometry"]["coordinates"][0]
                polygon = Polygon(polygon_coords)
                obs[f"Pop{i+1}"] = obs.apply(lambda row: polygon.contains(Point(row["decimal_longitude"], row["decimal_latitude"])), axis=1)
                polys = obs[obs[f"Pop{i+1}"]]['circles']
                clusters[i] = gpd.GeoSeries(unary_union(polys))

            # Create a color palette for the clusters
            colors = glasbey.create_palette(palette_size=len(clusters.iloc[0]), colorblind_safe=True, cvd_severity=100)
            sns.palplot(colors)

            # Create features to plot
            features = []
            for i, poly in enumerate(clusters.iloc[0]):
                color = colors[i % len(colors)]
                feature = geojson.Feature(geometry=poly, properties={"name": f"Pop {i+1}", "style": {"color": color}, "population_density": ""})
                features.append(feature)

            st.session_state.polygons  = geojson.FeatureCollection(features)
            st.rerun(scope="fragment")
    if "polygons" in st.session_state:  
        if st.button("Confirm and Proceed"):
            st.rerun()
    

if  "obs" in st.session_state:   
    load_polygons()


@st.fragment
def convert_df():
    polygons = st.session_state.confirmed_polygons
    with st.form(key='polygon', enter_to_submit=False):
        properties = pd.DataFrame(
            [
                {"Name": poly["properties"]["name"]}
                for poly in st.session_state.confirmed_polygons["features"]
            ]
        )
        properties["Population_Density"] = [0] * len(properties)
        properties["nenc"] = [0] * len(properties)
        properties["size"] = [0] * len(properties)

        default_dens = st.text_input("Default density", placeholder="Example: 50 or 50,100,1000", key="pop_density")
        if default_dens:
            try:
                dens = [float(num) for num in default_dens.split(",")]

            except ValueError:
                st.error("wrong entry, try again")
                st.stop()

        default_nenc= st.text_input("Default Ne:Nc", placeholder="Example: 0.1,0.5,0.9", key="nenc")
        if default_nenc:
            try:
                nenc = [float(num) for num in default_nenc.split(",")]
            except ValueError:
                st.error("wrong entry, try again")
                st.stop()
        
        properties = properties.assign(Population_Density=default_dens)
        properties = properties.assign(nenc=default_nenc)
        properties = properties.assign(size=10)
        st.form_submit_button("Submit")

    if default_dens: 
        edited_df = st.data_editor(properties)
        for i in range(0, len(edited_df)):
            st.session_state.confirmed_polygons["features"][i]["properties"]["population_density"] = str(edited_df["Population_Density"][i])
            st.session_state.confirmed_polygons["features"][i]["properties"]["nenc"] = str(edited_df["nenc"][i])
            st.session_state.confirmed_polygons["features"][i]["properties"]["size"] =str(edited_df["size"][i])
        st.session_state.edited_df=edited_df

        # Initialize folium map
        m = folium.Map(location=[0, 0], zoom_start=2)

        # Add the polygons to the map
        fg = folium.FeatureGroup(name="Polygons")
        fg.add_child(folium.GeoJson(polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density", "nenc", "size"])))
        # Display the map
        st.session_state.output2 = st_folium(m, width=700, height=500, feature_group_to_add=fg)
        return st.session_state.confirmed_polygons

if "polygons" in st.session_state:
    st.session_state.confirmed_polygons = st.session_state.polygons
    convert_df()
    if st.button("Save Polygons"):
        with open("/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/userdata/interface_polygons/updated_polygons.geojson", "w") as f:
            geojson.dump(st.session_state.confirmed_polygons, f)
        st.success("Polygons saved successfully.")
        st.session_state.poly_directory = "/userdata/interface_polygons/updated_polygons.geojson"
        poly_directory = st.session_state.poly_directory

if "poly_directory" in st.session_state:
    LC_type=st.selectbox("Land Cover Type", ["Tree Cover", "manual Land Cover", "automatic Land Cover"], index=None)  
    if LC_type:
        with st.form(key='areas', enter_to_submit=False):
            
            if LC_type=="manual Land Cover":
                LC_class = st.multiselect("select LC class", options=LC_names, key="LC_class")
                LC_class = [values[LC_names.index(name)] for name in LC_class]
                timeseries = st.text_input("time series", placeholder="Example: 2000, 2010, 2020", key="time_series")

            if LC_type=="automatic Land Cover":
                LC_class = [0]
            
            if LC_type=="Tree Cover":
                
                LC_class="Treecover"
            timeseries = st.text_input("time series", placeholder="Example: 2000, 2010, 2020", key="timeseries")
            if st.form_submit_button("Submit"):
                try:
                    timeseries = [float(num) for num in timeseries.split(",")]
                except ValueError:
                    st.error('error 2') 
                if timeseries:
                    if LC_type=="manual Land Cover" or LC_type=="automatic Land Cover":
                        LC_area()
                        st.write("Response: ", st.session_state.area.text)
                    if LC_type=="Tree Cover":
                        TC_area()
                        st.write("Response: ", st.session_state.area.text)

            



if "area" in st.session_state:
 
    output_area=get_output(st.session_state.area.text)
    area_output_code=output_area["GFS_IndicatorsTool>pop_area_by_habitat.yml@200"]
    if LC_type=="Tree Cover":
        cover_output_code=output_area["GFS_IndicatorsTool>get_TCY.yml@203"]
    if LC_type=="manual Land Cover" or LC_type=="automatic Land Cover":
        cover_output_code=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
    cover_maps=f"/output/{cover_output_code}/cover maps"
    pop_area=f"/output/{area_output_code}/pop_habitat_area.tsv"

    area_file_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{area_output_code}/pop_habitat_area.tsv"
    st.write("File Path: ", area_file_path)
    area_table = pd.read_csv(area_file_path, sep='\t')
    st.write("Data: ", area_table)

if area_table is not None:
    y2000=area_table[area_table.columns[1]]
    ne_nc = [float(n) for n in st.session_state.edited_df["nenc"].str.split(',').explode()]
    density = [float(d) for d in st.session_state.edited_df["Population_Density"].str.split(',').explode()]
    y2000
    ne_nc
    density
    result = [f * d for d in density for f in ne_nc]


    pop_size_table= pd.DataFrame([y2000*d for d in result])  
    # Create new column names based on density and ne_nc values
    new_columns = [f'density:{d}, Ne:Nc:{f}' for d in density for f in ne_nc]
    pop_size_table.index = new_columns

    for i in range(0, len(pop_size_table.columns)):
        st.session_state.confirmed_polygons['features'][i]['properties']['size']=pop_size_table[i].to_dict()
        

if pop_size_table is not None:
    with st.form(key='title', enter_to_submit=False):
        title=st.text_input("Title", placeholder="Example: Meles meles Simon Pahls")
        if st.form_submit_button("Submit"):

            edited_poly=st.session_state.poly_directory
            Indicator = Indicators()


# if Indicator:
#             output_Indicators = get_output(Indicator.text)
#             st.write(output_Indicators)
#             Indicator_output_code=output_Indicators["GFS_IndicatorsTool>get_Indicators_copy.yml@183"]
#             st.write("Output Code: ", Indicator_output_code)
#             NEs = pd.read_csv(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{Indicator_output_code}/NE.tsv", sep='\t')
#             rel_habitat_change= pd.read_csv(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{Indicator_output_code}/rel_habitat_change.tsv", sep='\t')

#             st.write("NEs: ", NEs)
#             st.write("rel_habitat_change: ", rel_habitat_change)
# fig = px.line(NEs, x=NEs.index, y="NEs", color="pop_expanded.name",
#                  title="NEs per Population",
#                  labels={"NEs": "NEs Value", "index": "Sample Index"})

# # Show in Streamlit
# st.plotly_chart(fig)            




















# if buffer and distance:
#     polygon_file_path = "/Users/simonrabenmeister/Desktop/Genes_from_Space/Genes_from_Space_interface/Test files/population_polygons_switzerland.geojson"
#     st.write("You entered: ", polygon_file_path)
# if "poly" not in st.session_state:
#     f = open(polygon_file_path)
#     st.session_state_poly=geojson.load(f)




