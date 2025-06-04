import streamlit as st

from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import folium.plugins as plugins
import csv
import geojson
import os
import requests
import time
from streamlit_plotly_events import plotly_events
import plotly.express as px


species = None
start_y = None  
end_y = None
bbox = None
country = None
buffer = None
distance = None
points_present = None
output = None
GBIF_dir = None
poly_file=None
GBIF_directory = None
poly_directory = None
LC_type = None
timeseries = None
LC_class = None
polygon_response = None 
title = None
area_table = None
pop_size_table = []
area = None
pop_area = None 
cover_maps = None
Indicator_out = None
csv_new = None


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

    response = requests.post(url, json=data, headers=headers)
    return response

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
        "pipeline@197": poly_directory,
        "pipeline@198": timeseries,
        "pipeline@199": LC_class
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response

def TC_area():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>TC_area.json/run"

    data = {
        "pipeline@197": poly_directory,
        "pipeline@204": timeseries,
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response

def Indicators():
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>Indicators.json/run"

    data = {
        "GFS_IndicatorsTool>get_Indicators_copy.yml@183|lc_classes": LC_class,
        "pipeline@189": title,
        "pipeline@201": cover_maps,
        "pipeline@202": edited_poly,
        "pipeline@203": pop_area

    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response

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
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220]



species=st.text_input("Species Name", placeholder="Example: Quercus sartorii")
st.write("You entered: ", species)
if species:
    start_y=st.number_input("Start year", value=None, step=1, min_value=1900, max_value=2021)
    st.write("You entered: ", start_y)
if start_y:
    end_y=st.number_input("End year", value=None, step=1, min_value=1900, max_value=2021)
    st.write("You entered: ", end_y)

if end_y:
    bbox = mapbbox()
    st.write("You entered: ", bbox)

if bbox:
    GBIF_response = GBIF()
    st.write("Response: ", GBIF_response.text)
    while True:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                history = requests.get(f"http://localhost/api/history").json()
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
        status=[entry["status"] for entry in history if entry["runId"] == GBIF_response.text]
        if status[0]!="running":
            break
    if status[0]=="completed":
        output_GBIF=requests.get(f"http://localhost/api/{GBIF_response.text}/outputs").json()
        output_link=output_GBIF["data>getObservations.yml@169"]
        GBIF_directory=f"/output/{output_link}/obs_data.tsv"
        st.write("Data: ",  GBIF_directory)
if GBIF_directory:
    buffer=st.number_input("Buffer", value=None)
    distance=st.number_input("Distance", value=None)

    if buffer and distance:
        polygon_response = polygon()   
        st.write("Response: ", polygon_response.text) 


        # max_retries = 3
        # for attempt in range(max_retries):
        #     try:
        #         history2 = requests.get(f"http://localhost/api/history").json()
        #         break
        #     except requests.exceptions.RequestException as e:
        #         st.write(f"Attempt {attempt + 1} failed: {e}")
        #         if attempt < max_retries - 1:
        #             time.sleep(2)
        #         else:
        #             st.write("Failed to retrieve history after multiple attempts.")
        #             history2 = None
if polygon_response:
    while True:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                history2 = requests.get(f"http://localhost/api/history").json()
                break
            except requests.exceptions.RequestException as e:
                st.write(f"Attempt {attempt + 1} failed: {e}")
        status_poly=[entry["status"] for entry in history2 if entry["runId"] == polygon_response.text]
        if status_poly[0]!="running":
            break

    if status_poly[0]=="completed":
        output_poly=requests.get(f"http://localhost/api/{polygon_response.text}/outputs").json()
        output_link_poly=output_poly["GFS_IndicatorsTool>get_pop_poly.yml@199"]
        file_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{output_link_poly}/population_polygons.geojson"
        st.write("File Path: ", file_path)

        f = open(file_path)
        poly_file=geojson.load(f)
    else:
        st.write(f"Error: {status_poly[0]}")
    mapgeojson(poly_file)
    
    LC_type=st.selectbox("Land Cover Type", ["Tree Cover", "Land Cover"], index=0)
    poly_directory=f"/output/{output_link_poly}/population_polygons.geojson"
    if LC_type=="Land Cover":
        LC_mode= st.selectbox(
        'Land classification mode',
        ('automatic (most common)', 'manual'),
        index=None)
        
        if (LC_mode=='automatic (most common)'):
            LC_class = [0]
        if (LC_mode=='manual'):
            LC_class = st.multiselect("select LC class", options=LC_names, key="LC_class")
            LC_class = [values[LC_names.index(name)] for name in LC_class]
        timeseries = st.text_input("time series", placeholder="Example: 0.1 or 0.1,0.2", key="time_series")
        if timeseries:
            try:
                timeseries = [float(num) for num in timeseries.split(",")]
            except ValueError:
                st.error('error 2')
        title=st.text_input("Title", placeholder="Example: Meles meles Simon Pahls")
        area= LC_area()

    if LC_type=="Tree Cover":
        timeseries = st.text_input("time series", placeholder="Example: 0.1 or 0.1,0.2", key="timeseries")
        title=st.text_input("Title", placeholder="Example: Meles meles Simon Pahls")
        if timeseries and title:
            try:
                timeseries = [float(num) for num in timeseries.split(",")]
            except ValueError:
                st.error('error 2')  
        area= TC_area()
        
    
if area:
    st.write("area: ", area.text)
    while True:
        max_retries = 6
        for attempt in range(max_retries):
            try:
                history = requests.get(f"http://localhost/api/history").json()
                
                break
            except requests.exceptions.RequestException as e:
                st.write(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        status=[entry["status"] for entry in history if entry["runId"] == area.text]
        print("Status: ", status)
        if status[0]!="running":
            break
    st.write("Status: ", status)    
    if status[0]=="completed":
        output_area=requests.get(f"http://localhost/api/{area.text}/outputs").json()
        st.write("Output: ",  output_area)
        output_link=output_area["GFS_IndicatorsTool>pop_area_by_habitat.yml@200"]
        file_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{output_link}/pop_habitat_area.tsv"
        st.write("File Path: ", file_path)
        area_table = pd.read_csv(file_path, sep='\t')
        st.write("Data: ", area_table)

        y2000=area_table[area_table.columns[1]]
        ne_nc=[0.1, 0.5, 0.9]
        density=[50,100]
        result = [f * d for d in density for f in ne_nc]


        pop_size_table= pd.DataFrame([y2000*d for d in result])  
        # Create new column names based on density and ne_nc values
        new_columns = [f'density:{d}, Ne:Nc:{f}' for d in density for f in ne_nc]
        pop_size_table.index = new_columns

        for i in range(0, len(pop_size_table.columns)):
            poly_file['features'][i]['properties']['pop_size']=pop_size_table[i].to_dict()
            
        edited_poly=f"/output/{output_link}/population_polygons_with_pop_size.geojson"
        with open(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/{edited_poly}", 'w') as f:
            geojson.dump(poly_file, f)



        pop_area=f"/output/{output_link}/pop_habitat_area.tsv"
        if LC_type=="Tree Cover":
            cover_link=output_area["GFS_IndicatorsTool>get_TCY.yml@203"]
        if LC_type=="Land Cover":
            cover_link=output_area["GFS_IndicatorsTool>get_LCY.yml@195"]
        cover_maps=f"/output/{cover_link}/cover maps"
        st.write("Cover Link: ", cover_link)


if title:
    LC_class = "10"
    Indicators = Indicators()
    st.write("Response: ", Indicators.text) 
    while True: 
        max_retries = 6
        for attempt in range(max_retries):
            try:
                history = requests.get(f"http://localhost/api/history").json()
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
        status=[entry["status"] for entry in history if entry["runId"] == Indicators.text]
        if status[0]!="running":
            break
    st.write("Status: ", status)
    if status[0]=="completed":  
        Indicator_out= requests.get(f"http://localhost/api/{Indicators.text}/outputs").json()["GFS_IndicatorsTool>get_Indicators_copy.yml@183"]
    NEs = pd.read_csv(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{Indicator_out}/NE.tsv", sep='\t')
    st.write("NEs: ", NEs)


    csv_new=area_table.melt(id_vars='pop', var_name='Year', value_name='Value')
    st.write("You uploaded: ", csv_new)





    ################################################################
    import streamlit as st
    import plotly.express as px
    import pandas as pd
    from streamlit_map import mapgeojson
    from streamlit_folium import st_folium
    import geojson as gj
    import leafmap.foliumap as leafmap
    import ipywidgets as widgets
    from ipyleaflet import Map, GeoJSON
    import numpy as np
    import folium

    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = None

    #Create example dataset
    df = csv_new

    new_data = {
        'Year': [],
        'Value': [],
        'pop': []
    }
    # Remove 'y' from year entries
    df['Year'] = df['Year'].apply(lambda x: int(x[1:]) if isinstance(x, str) and x.startswith('y') else x)
    for pop in df['pop'].unique():
        pop_df = df[df['pop'] == pop]
        for i in range(len(pop_df) - 1):
            num = int(30 / len(pop_df))
            # Generate 10 points between start and end year, excluding the start year to avoid duplicates
            years = np.linspace(int(pop_df.iloc[i]['Year']), int(pop_df.iloc[i + 1]['Year']), num, endpoint=False)
            values = np.linspace(pop_df.iloc[i]['Value'], pop_df.iloc[i + 1]['Value'], num, endpoint=False)
            for year, value in zip(years, values):
                new_data['Year'].append(int(year))
                new_data['Value'].append(value)
                new_data['pop'].append(pop)







    # Load GeoJSON data
    # Replace with actual path


    # Streamlit app layout
    st.title("Interactive Map with Clickable Polygons")

    # Initialize folium map
    m = folium.Map(location=[40, -100], zoom_start=4)

    # Function to style polygons
    def style_function(feature):
        pop_color_map = {
            "pop_1": "blue",
            "pop_2": "green",
            "pop_3": "red"
        }
        pop_value = feature["properties"]["pop"]
        return {"fillColor": pop_color_map.get(pop_value, "gray"), "color": "black", "weight": 1, "fillOpacity": 0.5}

    # Function to highlight clicked polygon
    def highlight_function(feature):
        return {"fillColor": "red", "color": "black", "weight": 2, "fillOpacity": 0.7}

    # Add GeoJSON layer with click interaction
    geojson_layer = folium.GeoJson(
        poly_file,
        name="Polygons",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=["pop"]),  # Replace with relevant field
    )
    geojson_layer.add_to(m)

    # Display map in Streamlit
    map_data = st_folium(m, height=600, width=700)

    # Capture clicked feature (last clicked polygon)
    if map_data and "last_active_drawing" in map_data:
        clicked_poly = map_data["last_active_drawing"]
        clicked_point= map_data["last_object_clicked"]
        st.session_state.selected_data = clicked_poly["properties"]["pop"]

    # Convert the new data to a DataFrame
    new_df = pd.DataFrame(new_data) 
    # Create line plot
    fig = px.line(new_df, x='Year', y='Value', color='pop')
    fig.update_layout(clickmode='select')

    # Update traces to reduce opacity for pop_1 and pop_

    if st.session_state.selected_data:
        for trace in fig.data:
            if trace.name == st.session_state.selected_data:
                trace.update(opacity=1.0)
            else:
                trace.update(opacity=0.2)
            fig.update_traces(mode="lines+markers", marker=dict(opacity=0))
    fig.update_traces(mode="lines+markers", marker=dict(opacity=0))


    # Display plot in Streamlit
    event = st.plotly_chart(fig, key="habitat", on_select="rerun")

    # Access the selected data
    if event:
        selected_data = event.selection
        if selected_data["points"]:
            st.session_state.selected_data = selected_data["points"][0]["legendgroup"]


    # m.to_streamlit(height=700)

    # m.add_geojson(poly_file, layer_name="US Regions", fill_colors=["yellow", "green","red"])
    # m.edit_vector(poly_file)


    # m.to_streamlit(height=700)

    # st.write("Hello")
    # if st.button("save"):
    #     m.save_draw_features("/Users/simonrabenmeister/Desktop/Genes_from_Space/Genes_from_Space_interface/Test files/population_polygons_switzerland_copy.geojson")