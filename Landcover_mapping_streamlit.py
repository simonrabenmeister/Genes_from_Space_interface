import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import geojson
import numpy as np
import requests
import pandas as pd
import time
import folium.plugins as plugins
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import glasbey
import seaborn as sns
import plotly.express as px

end_y=None
bbox_input=None
species=None
country=None
area_table=None
pop_size_table=None
LC_class=None
region=None
Indicator=None
st.set_page_config(layout="wide")
long_text = "Lorem ipsum. " * 1000
col1, col2= st.columns(2)

if "stage" not in st.session_state:
    st.session_state.stage="start"
if "bbox" not in st.session_state:
    st.session_state.bbox=None
if "country" not in st.session_state:
    st.session_state.country=None

if "output" not in st.session_state:
    st.session_state.output=None
if "last_object_clicked" not in st.session_state:
    st.session_state.last_object_clicked=None
if "poly_directory" not in st.session_state:
    st.session_state.poly_directory=None

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

#################### Functions ####################

def get_output(response_code):
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
        output_bbiab= requests.get(f"http://localhost/api/{response_code}/outputs").json()
        return output_bbiab
    
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

    return requests.post(url, json=data, headers=headers)

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

@st.fragment
def edit_points():

    obs = st.session_state.obs

    if "index" not in st.session_state:
        st.session_state.index=None


#Set the columns for the latitude and longitude
    lat_col = "decimal_latitude"
    lon_col = "decimal_longitude"
    obs = obs.drop_duplicates(subset=[lat_col, lon_col]).reset_index(drop=True)
    if "obs_edit" not in st.session_state:
        st.session_state.obs_edit=obs
    obs_edit=st.session_state.obs_edit
    # Remove duplicate points based on latitude and longitude
    
    m = folium.Map(location=[0, 0], zoom_start=2)
    st.write(st.session_state.index)

    # Add the observations to the map
    fg = folium.FeatureGroup(name="Markers")
    for i, row in obs_edit.iterrows():
        corr=[row["decimal_latitude"], row["decimal_longitude"]]
        folium.CircleMarker(
            location=corr,
            radius=6,
            color="red" if st.session_state.index is not None and i in st.session_state.index else "blue",
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
        st.session_state.output = st_folium(m, width=700, height=500, feature_group_to_add=fg, use_container_width=True)       
    else:
        fg2 = folium.FeatureGroup(name="Markers")
        fg2.add_child(folium.GeoJson(st.session_state.polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density"])))
        st.session_state.output = st_folium(m, width=700, height=500, feature_group_to_add=[fg, fg2], use_container_width=True)

#Get the index of the clicked point
    if "last_object_clicked" in st.session_state.output and st.session_state.output["last_object_clicked"] is not None:
        st.session_state.index=obs_edit.index[(obs_edit[lat_col] == st.session_state.output["last_object_clicked"]["lat"]) & 
        (obs_edit[lon_col] == st.session_state.output["last_object_clicked"]["lng"])]

        def remove_point(index):
            st.session_state.obs_edit=obs_edit.drop(index)

        #Remove the point if the remove button is clicked
        st.button("remove point", on_click=remove_point, args=(st.session_state.index,)) 
        st.session_state.obs=obs_edit
    # Create circle object for points
    if st.button("Remove Polygons"):
        del st.session_state["polygons"]
        size = None
        st.rerun(scope="fragment")
    
    if (
        "last_object_clicked" in st.session_state.output
        and st.session_state.output["last_object_clicked"] != st.session_state["last_object_clicked"]
    ):
        st.session_state["last_object_clicked"] = st.session_state.output["last_object_clicked"]
        st.rerun(scope="fragment")
    obs['geometry'] = obs.apply(lambda row: Point((row["decimal_longitude"], row["decimal_latitude"])), axis=1)
    geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
    new_df = geo_df.set_crs(epsg=4326)
    new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)
    with st.form(key='buffer', enter_to_submit=False):
        size = st.number_input("Buffer", value=None)
        if  st.form_submit_button("Draw Polygon"):
            if size is None:
                st.error("Please enter a buffer size")
            elif st.session_state.output["all_drawings"] ==[]:
                st.error("Please draw a polygon on the map")
            else:
                circles = new_df['geometry'].buffer(size)
                obs['circles'] = circles.to_crs(epsg=4326)
                # Group the circles into clusters depending on drawn polygons
                clusters = pd.DataFrame()
                for i in range(0, len(st.session_state.output["all_drawings"])):
                    polygon_coords = st.session_state.output["all_drawings"][i]["geometry"]["coordinates"][0]
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
                    feature = geojson.Feature(geometry=poly, properties={"name": f"Pop {i+1}", "style": {"color": color}, "population_density": None})
                    features.append(feature)

                st.session_state.polygons  = geojson.FeatureCollection(features)
                st.rerun(scope="fragment")
    if "polygons" in st.session_state:  
        if st.button("Confirm and Proceed"):
            st.session_state.stage="Indicators"
            st.rerun()

        
@st.fragment
def convert_df():
    polygons =   st.session_state.polygons
    if st.session_state.polygons["features"][0]["properties"]["population_density"] is None:
        for i in range(0, len(st.session_state.polygons["features"])):
            st.session_state.polygons["features"][i]["properties"].update({"population_density": "", "nenc": "", "size": ""})
    # Initialize folium map
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add the polygons to the map
    fg = folium.FeatureGroup(name="Polygons")
    fg.add_child(folium.GeoJson(polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density", "nenc", "size"])))
    # Display the map
    st.session_state.output2 = st_folium(m, width=700, height=500, feature_group_to_add=fg, use_container_width=True)

    with st.form(key='polygon', enter_to_submit=False):
        properties = pd.DataFrame(
            [
                {"Name": poly["properties"]["name"]}
                for poly in st.session_state.polygons["features"]
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
            st.session_state.polygons["features"][i]["properties"]["population_density"] = str(edited_df["Population_Density"][i])
            st.session_state.polygons["features"][i]["properties"]["nenc"] = str(edited_df["nenc"][i])
            st.session_state.polygons["features"][i]["properties"]["size"] =str(edited_df["size"][i])
        st.session_state.edited_df=edited_df
        
    if st.button("Confirm:"):
        with open("/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/userdata/interface_polygons/updated_polygons.geojson", "w") as f:
            geojson.dump(st.session_state.polygons, f)
        st.success("Polygons saved successfully.")
        st.session_state.poly_directory = "/userdata/interface_polygons/updated_polygons.geojson"
        st.rerun()



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
    output = st_folium(m,use_container_width=True)
    #get the bounding box of the last clicked polygon
    if output["last_active_drawing"] is not None:
        geometry=output["last_active_drawing"]["geometry"]
        st.session_state.bbox =  get_bounding_box(geometry)
    if st.button("Confirm Bounding Box"):
        st.rerun()

with st.sidebar:
    colheight = st.slider(
        "When do you start?",0, 2000, 1000
    )
with col1.container( border=True, key="image-container", height=colheight):

    st.title("Genes from Space Tool")
    point_source = st.selectbox("Select a tool", [ "Upload your own point observations", "Source points from GBIF"], index=None,  placeholder="Select Point source")
    if point_source=="Upload your own point observations":
        st.write("Upload your own point observations")

    if point_source=="Source points from GBIF":
        st.write("Source points from GBIF")
        with st.form(key='GBIF', enter_to_submit=False):

            species=st.text_input("Species Name", placeholder="Example: Quercus sartorii")
            start_y=st.number_input("Start year", value=None, step=1, min_value=1900, max_value=2021)
            end_y=st.number_input("End year", value=None, step=1, min_value=1900, max_value=2021)
            region=st.radio("Area of interest selection", ["Map selection", "Country"])
            if st.form_submit_button("Submit"):
                if region=="Country":
                    st.session_state.stage="country"
                    st.session_state.bbox=None
                if region=="Map selection":
                    st.session_state.stage="bbox_draw"
                    st.session_state.country=None
    
    if end_y and region == "Country": 
        countries = st.multiselect("Select countries", country_names)
        bbox=[]
        st.write("Selected countries: ", country)
        if countries:
            if st.button("Fetch Points"):
                st.session_state.stage="Manipulate points"
    if end_y and region=="Map selection":
        if st.session_state.bbox is None:
            st.info("Draw a bounding box on the map to select the area of interest or enter the bbox bellow")
        bbox_input = st.text_input("Bounding Box",placeholder="[5.831977, 45.721522, 10.763195, 47.901613]", value=st.session_state.bbox)
        if bbox_input:
            try:
                st.session_state.bbox = list(map(float, bbox_input.strip("[]").split(",")))
            except ValueError:
                st.error("Invalid bounding box format. Please enter in the format: [min_lon, min_lat, max_lon, max_lat]")
        if st.session_state.bbox is not None:
            if st.button("Fetch Points"):
                st.session_state.stage="Manipulate points"
        if st.session_state.stage=="Manipulate points":

            with st.spinner("Wait for it..."): 
                bbox = st.session_state.bbox
                country=st.session_state.country
                GBIF_response = GBIF()
                output_GBIF = get_output(GBIF_response.text)
                GBIF_output_code=output_GBIF["data>getObservations.yml@169"]
                GBIF_directory=f"/output/{GBIF_output_code}/obs_data.tsv"
                obs_file = open(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{GBIF_output_code}/obs_data.tsv")
                obs = pd.read_csv(obs_file, sep='\t')
                st.session_state.obs = obs
    if st.session_state.poly_directory is not None:
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
                            area=LC_area()
                            st.write("Response: ", st.session_state.area.text)
                        if LC_type=="Tree Cover":
                            area=TC_area()
                            st.write("Response: ", st.session_state.area.text)
    if "area" in st.session_state:
        output_area=get_output(st.session_state.area.text)

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
            st.session_state.polygons['features'][i]['properties']['size']=pop_size_table[i].to_dict()
            

    if pop_size_table is not None:
        with st.form(key='title', enter_to_submit=False):
            title=st.text_input("Title", placeholder="Example: Meles meles Simon Pahls")
            if st.form_submit_button("Submit"):

                edited_poly=st.session_state.poly_directory
                Indicator = Indicators()
                st.write("Response: ", Indicator.text)
            if Indicator:
                output_indicators=get_output(Indicator.text)
                st.write("Response: ", output_indicators)
                if "GFS_IndicatorsTool>get_Indicators_copy.yml@183" in output_indicators:
                    st.write("Response: ", output_indicators["GFS_IndicatorsTool>get_Indicators_copy.yml@183"])
                    st.session_state.indicator_code = output_indicators["GFS_IndicatorsTool>get_Indicators_copy.yml@183"]
                    st.session_state.stage = "Habitat Area"

                    # Load rel_habitat_change.tsv file
                    rel_habitat_change_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{st.session_state.indicator_code}/rel_habitat_change.tsv"
                    NE_path = f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{st.session_state.indicator_code}/NE.tsv"
                    try:
                        rel_habitat_change_table = pd.read_csv(rel_habitat_change_path, sep='\t')
                        st.write("Relative Habitat Change Data: ", rel_habitat_change_table)
                        NE_table = pd.read_csv(NE_path, sep='\t')
                        st.write("NEs Data: ", NE_table)
                    except FileNotFoundError:
                        st.error(f"File not found: {rel_habitat_change_path}")
                else:
                    st.error("Error: No response code found in the output.")



with col2:
    if st.session_state.stage=="bbox_draw":
        mapbbox()
    if st.session_state.stage=="Manipulate points":
        edit_points()
    if st.session_state.stage=="Indicators":
        convert_df()

    subcol1, subcol2 = st.columns(2)
    if area_table is not None:
        # Plot for rel_habitat_change_table
        df = pd.DataFrame(rel_habitat_change_table)

        # Melt to long format
        df_long = df.melt(id_vars="name", var_name="year", value_name="habitat_area")

        # Clean year column
        df_long["year"] = df_long["year"].str.replace("y", "").astype(int)

        # Plot using Plotly
        fig = px.line(
            df_long,
            x="year",
            y="habitat_area",
            color="name",
            markers=True,
            title="Habitat Area Change Over Time",
            labels={"habitat_area": "Habitat Area", "year": "Year", "name": "Population"}
        )

        # Emphasize pop1 with a thicker line
        for trace in fig.data:
            if trace.name == "pop1":
                trace.line.width = 4
            else:
                trace.line.width = 2

        # Display in Streamlit


        # Plot for area_table
        area_df = pd.DataFrame(area_table)

        # Melt to long format
        area_df_long = area_df.melt(id_vars=area_df.columns[0], var_name="year", value_name="area")

        # Clean year column
        area_df_long["year"] = area_df_long["year"].str.replace("y", "").astype(int)

        # Plot using Plotly
        area_fig = px.line(
            area_df_long,
            x="year",
            y="area",
            color=area_df.columns[0],
            markers=True,
            title="Area Trends Over Time",
            labels={"area": "Area", "year": "Year", area_df.columns[0]: "Category"}
        )

        with subcol1:
            st.plotly_chart(fig, use_container_width=True)
        with subcol2:
            st.plotly_chart(area_fig, use_container_width=True)

    # Create a map centered around a specific location
    # Ceate a dictionary of maps with different shapes or markers
    # Add a marker to the Default Ma
    # Create a dropdown to select the map to display
    # Display the selected ma
    # if "obs" in st.session_state:
    #     obs_edit=st.session_state.obs_edit
    #     fg = folium.FeatureGroup(name="Markers")
    #     #add the observations to the map
    #     for i, row in obs_edit.iterrows():
    #         fg.add_child(folium.Marker(
    #             location=[row["decimal_latitude"], row["decimal_longitude"]],
    #             tooltip="Click to select",
    #             icon=plugins.BeautifyIcon(icon="circle")
    #         ))
    #     fg.add_to(maps["obs_map"])
    #     st.session_state.m=maps["obs_map"]

    # if st.session_state.m is not None:
    #     st.session_state.output_map = st_folium(
    #         st.session_state.m,
    #         key="out",
    #         use_container_width=True
    #     )
    # if "obs" in st.session_state:
    #     st.session_state.m=maps["polygons"]
    #     obs = st.session_state.obs
    #     st.write(obs)

    #     # Add the observations to the map
    #     fg = folium.FeatureGroup(name="Markers")
    #     for i, row in obs.iterrows():
    #         folium.CircleMarker(
    #             location=[row["decimal_latitude"], row["decimal_longitude"]],
    #             radius=6,
    #             color='blue',
    #             fill_opacity=1,
    #             fill=True,
    #             fill_color='lightblue'
    #         ).add_to(fg)
    #     if "polygons" in st.session_state:
    #         fg.add_child(folium.GeoJson(st.session_state.polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density"])))    

    #     fg.add_to(maps["polygons"])
    #     # Add the Draw tool to the map
    #     draw = Draw(export=False, draw_options={
    #         'polyline': True,
    #         'polygon': True,
    #         'circle': True,
    #         'rectangle': True,
    #         'marker': True,
    #         'circlemarker': True
    #     }, edit_options={
    #         'edit': True,
    #         'remove': True
    #     })
    #     draw.add_to(maps["polygons"])

    #     # Display the map
    #     # Create circle object for points
    #     obs['geometry'] = obs.apply(lambda row: Point((row["decimal_longitude"], row["decimal_latitude"])), axis=1)
    #     geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
    #     new_df = geo_df.set_crs(epsg=4326)
    #     new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)
    #     with st.form(key='buffer', enter_to_submit=False):
    #         size = st.number_input("Buffer", value=None)
    #         if  st.form_submit_button("Draw Polygon"):
    #             circles = new_df['geometry'].buffer(size)
    #             obs['circles'] = circles.to_crs(epsg=4326)
    #             # Group the circles into clusters depending on drawn polygons
    #             clusters = pd.DataFrame()