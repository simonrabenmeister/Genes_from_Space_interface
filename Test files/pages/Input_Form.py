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
from matplotlib import cm
import json
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform


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
end_y=None
bbox_input=None
species=None
country=None
area_table=None
pop_size_table=None
LC_class=None
region=None
Indicator=None


if "stage" not in st.session_state:
    st.session_state["stage"] = "start"
if "text_stage" not in st.session_state:
    st.session_state.text_stage=0
if "bbox" not in st.session_state:
    st.session_state.bbox=None
if "country" not in st.session_state:
    st.session_state.country=None
if "out" not in st.session_state:
    st.session_state.out=None
if "output" not in st.session_state:
    st.session_state.output=None
if "last_object_clicked" not in st.session_state:
    st.session_state.last_object_clicked=None
if "poly_directory" not in st.session_state:
    st.session_state.poly_directory=None
if "name" not in st.session_state:
    st.session_state.name=None
if "height" not in st.session_state:
    st.session_state.height=1000
if "zoom" not in st.session_state:
    st.session_state.zoom=2
if "center" not in st.session_state:
    st.session_state.center={"lat": 0, "lng": 0}
if "buffer" not in st.session_state:
    st.session_state.buffer=None
if "index" not in st.session_state:
    st.session_state.index=None
if "start_y" not in st.session_state:
    st.session_state.start_y=None
    # Load texts
texts = pd.read_csv("texts.csv").set_index("id")


# Load countries
country_names = pd.read_csv("countries.txt", header=None)[0].to_numpy()  # Assuming the file has no header


# function to render text
def rtext(id):
        return texts.loc[id,lan].replace("\\n","\n")

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
    url = "http://localhost/pipeline/GenesFromSpace>ToolComponents>Interface>GBIF_API.json/run"
    data = {
        "pipeline@24": species,
        "pipeline@25": st.session_state.country,
        "pipeline@26": [st.session_state.start_y],
        "pipeline@27": [st.session_state.end_y],
        "pipeline@28": [0.1],  # Example value for coordinate precision
        "pipeline@29": [0.1],  # Example value for coordinate uncertainty
        "pipeline@30": st.session_state.bbox
    }
    headers = {"Content-Type": "application/json"}
    data
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

    obs = st.session_state.obs_edit

#Set the columns for the latitude and longitude
    lat_col = "decimallatitude"
    lon_col = "decimallongitude"

    obs = obs.drop_duplicates(subset=[lat_col, lon_col]).reset_index(drop=True)
    obs_edit = obs.copy()
    # Remove duplicate points based on latitude and longitude
    
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

    # Add the observations to the map
    fg = folium.FeatureGroup(name="Markers")
    for i, row in obs_edit.iterrows():
        corr=[row["decimallatitude"], row["decimallongitude"]]
        folium.CircleMarker(
            location=corr,
            radius=6,
            color="red" if st.session_state.index is not None and i in st.session_state.index else "blue",
            fill_opacity=1,
            fill=True,
            fill_color='lightblue'
        ).add_to(fg)


    st.session_state.output = st_folium(m, feature_group_to_add=fg, use_container_width=True)      
#Get the index of the clicked point
    if "last_object_clicked" in st.session_state.output and st.session_state.output["last_object_clicked"] is not None:
        st.session_state.index=obs_edit.index[(obs_edit[lat_col] == st.session_state.output["last_object_clicked"]["lat"]) & 
        (obs_edit[lon_col] == st.session_state.output["last_object_clicked"]["lng"])]

        def remove_point(index):
            st.session_state.obs_edit=obs_edit.drop(index)

        #Remove the point if the remove button is clicked
        st.button("remove point", on_click=remove_point, args=(st.session_state.index,)) 

        if (
            "last_object_clicked" in st.session_state.output
            and st.session_state.output["last_object_clicked"] != st.session_state["last_object_clicked"]
        ):
            st.session_state["last_object_clicked"] = st.session_state.output["last_object_clicked"]
            st.rerun(scope="fragment")
    
    if st.button("Save points"):
        if "polygons" in st.session_state:
            del st.session_state["polygons"]
        st.session_state.obs=obs_edit
        st.session_state.stage="polygon_clustering"
        st.session_state.zoom=st.session_state.output["zoom"]
        st.session_state.center=st.session_state.output["center"]
        st.rerun()


@st.fragment
def polygon_clustering():
    # Create a dummy DataFrame for point data

    points_df = pd.DataFrame(st.session_state.obs)

    # Convert the DataFrame to a GeoDataFrame
    points_gdf = gpd.GeoDataFrame(
        points_df,
        geometry=gpd.points_from_xy(points_df["decimallongitude"], points_df["decimallatitude"]),
        crs="EPSG:4326"
    )

    with st.form(key='parameters', enter_to_submit=False):
        st.session_state.buffer=st.number_input("Buffer", value=None)
        st.session_state.distance=st.number_input("Distance", value=None)
        if st.form_submit_button("Submit"):
            if "polygons" in st.session_state:
                del st.session_state["polygons"]

            # Define the buffer radius in kilometers
            radius = st.session_state.buffer  # Example: 10 km

            # Create circular buffers around each point
            circles_gdf = points_gdf.copy()
            circles_gdf["geometry"] = points_gdf["geometry"].to_crs(epsg=3857).buffer(radius*1000).to_crs(epsg=4326)


            # Project geometries to a metric CRS for accurate distance calculations
            points_gdf_metric = points_gdf.to_crs(epsg=3857)

            # Calculate the distance matrix between points in meters
            distances = points_gdf_metric.geometry.apply(
                lambda geom: points_gdf_metric.geometry.distance(geom)
            ).to_numpy()

            # Perform hierarchical clustering
            linkage_matrix = linkage(squareform(distances), method="average")
            pop_distance = st.session_state.distance * 1000  # Convert maximum distance to meters
            # Assign population clusters
            circles_gdf["pop"] = ["pop_" + str(cluster) for cluster in fcluster(linkage_matrix, t=pop_distance, criterion="distance")]

            # Melt all circles from the same population into a MultiPolygon
            melted_clusters = circles_gdf.dissolve(by="pop").reset_index()
            # Resolve overlaps by assigning the overlap to the population with the lower number

            for i, row1 in melted_clusters.iterrows():
                for j, row2 in melted_clusters.iterrows():
                    if i >= j:
                        continue
                    if row1["geometry"].intersects(row2["geometry"]):
                        intersection = row1["geometry"].intersection(row2["geometry"])
                        if not intersection.is_empty:
                            # Assign the overlap to the population with the lower number
                            if int(row1["pop"].split("_")[1]) < int(row2["pop"].split("_")[1]):
                                melted_clusters.at[i, "geometry"] = row1["geometry"].union(intersection)
                                melted_clusters.at[j, "geometry"] = row2["geometry"].difference(intersection)
                            else:
                                melted_clusters.at[j, "geometry"] = row2["geometry"].union(intersection)
                                melted_clusters.at[i, "geometry"] = row1["geometry"].difference(intersection)
            # Create a feature collection from melted_clusters
            # Generate a color palette for the clusters
            colors = glasbey.create_palette(palette_size=len(melted_clusters), colorblind_safe=True, cvd_severity=100)

            features = []
            for i, row in melted_clusters.iterrows():
                color = colors[i % len(colors)]
                feature = geojson.Feature(
                geometry=row["geometry"],
                properties={"name": row["pop"], "style": {"color": color}}
                )
                features.append(feature)

            st.session_state.original_polygons = geojson.FeatureCollection(features)

    obs = st.session_state.obs

    if "index" not in st.session_state:
        st.session_state.index=None
    
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

    # Add the observations to the map
    fg = folium.FeatureGroup(name="Markers")
    for i, row in obs.iterrows():
        corr=[row["decimallatitude"], row["decimallongitude"]]
        folium.CircleMarker(
            location=corr,
            radius=6,
            color="blue",
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
    if "polygons" not in st.session_state and st.session_state.buffer is not None:
        fg2= folium.FeatureGroup(name="Markers")
        fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True)       
    elif "polygons" in st.session_state:
        fg2 = folium.FeatureGroup(name="Markers")
        fg2.add_child(folium.GeoJson(st.session_state.polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True)
        # Create circle object for points
    if (
        "last_object_clicked" in st.session_state.output
        and st.session_state.output["last_object_clicked"] != st.session_state["last_object_clicked"]
    ):
        st.session_state["last_object_clicked"] = st.session_state.output["last_object_clicked"]
        st.rerun(scope="fragment")
    obs['geometry'] = obs.apply(lambda row: Point((row["decimallongitude"], row["decimallatitude"])), axis=1)
    geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
    new_df = geo_df.set_crs(epsg=4326)
    new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)





    if st.session_state.output["all_drawings"] != [] and st.session_state.output["last_active_drawing"] is not None:
        size=st.session_state.buffer*1000
        if st.button("Group Polygons"):

            circles = new_df['geometry'].buffer(size)
            obs['circles'] = circles.to_crs(epsg=4326)
            
            # Group the circles into clusters depending on drawn polygons
            clusters = pd.DataFrame()
            for i in range(0, len(st.session_state.output["all_drawings"])):
                polygon_coords = st.session_state.output["all_drawings"][i]["geometry"]["coordinates"][0]
                polygon = Polygon(polygon_coords)
                obs[f"Pop{i+1}"] = obs.apply(lambda row: polygon.contains(Point(row["decimallongitude"], row["decimallatitude"])), axis=1)
                if obs[f"Pop{i+1}"].any():  # Skip if the polygon does not contain any observations
                    polys = obs[obs[f"Pop{i+1}"]]['circles']
                    clusters = pd.concat([clusters, gpd.GeoDataFrame(geometry=[unary_union(polys)])], ignore_index=True)

            for i, row1 in clusters.iterrows():
                for j, row2 in clusters.iterrows():
                    if i >= j:
                        continue
                    if clusters.iloc[i]["geometry"].intersects(clusters.iloc[j]["geometry"]):
                        intersection = clusters.iloc[i]["geometry"].intersection(clusters.iloc[j]["geometry"])
                        if not intersection.is_empty:
                            # Assign the overlap to the population with the lower number
                            if int(i) < int(j):
                                clusters.iloc[i]["geometry"] = clusters.iloc[i]["geometry"].union(intersection)
                                clusters.iloc[j]["geometry"] = clusters.iloc[j]["geometry"].difference(intersection)
                            else:
                                clusters.iloc[j]["geometry"] = clusters.iloc[j]["geometry"].union(intersection)
                                clusters.iloc[i]["geometry"]= clusters.iloc[i]["geometry"].difference(intersection)
            # Create a color palette for the clusters
                colors = glasbey.create_palette(palette_size=len(clusters), colorblind_safe=True, cvd_severity=100)
                sns.palplot(colors)

            # Create features to plot
            features = []
            for i, poly in clusters.iterrows():
                color = colors[i % len(colors)]

                feature = geojson.Feature(geometry=poly["geometry"], properties={"name": f"Pop {i+1}", "style": {"color": color}, "population_density": None})
                features.append(feature)

            st.session_state.polygons = geojson.FeatureCollection(features)
            st.rerun(scope="fragment")
    if "polygons" in st.session_state:  
        
        if st.button("reset polygons"):
            del st.session_state["polygons"]
            st.rerun(scope="fragment")
    if "polygons" in st.session_state or "original_polygons" in st.session_state:
        if st.button("Confirm and Proceed"):
            if "polygons" not in st.session_state:
                st.session_state.polygons = st.session_state.original_polygons

            st.session_state.zoom=st.session_state.output["zoom"]
            st.session_state.center=st.session_state.output["center"]
            st.session_state.stage = "LC"
            with open("/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/userdata/interface_polygons/updated_polygons.geojson", "w") as f:
                geojson.dump(st.session_state.polygons, f)
            st.success("Polygons saved successfully.")
            st.session_state.poly_directory = "/userdata/interface_polygons/updated_polygons.geojson"
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
    st.session_state.output2 = st_folium(m, feature_group_to_add=fg, use_container_width=True)

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
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
    # draw = Draw(export=False,   draw_options={
    #     'polyline': False,  # Disable polyline
    #     'polygon': False,    # Enable polygon
    #     'circle': False,    # Disable circle
    #     'rectangle': True,  # Enable rectangle
    #     'marker': False,     # Enable marker
    #     'circlemarker': False  # Disable circle marker
    # },
    # edit_options={
    #     'edit': True,   # Enable editing of drawn shapes
    #     'remove': True  # Enable deleting of drawn shapes
    # }
    # )
    # draw.add_to(m)
    Draw(export=True).add_to(m)
    def get_bounding_box(geom):
        coords = np.array(list(geojson.utils.coords(geom)))
        
        return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
    #display the map
    output = st_folium(m,use_container_width=True)
    #get the bounding box of the last clicked polygon
    if output["last_active_drawing"] is not None:
        geometry=output["last_active_drawing"]["geometry"]
        st.session_state.bbox =  get_bounding_box(geometry)

        st.session_state.zoom=output["zoom"]
        st.session_state.center=output["center"]
        st.rerun()

col1, col2= st.columns(2)
with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.height = st.slider(
            "Page Height",0, 2000, st.session_state.height
        )
        lan = st.radio("Select Language", ["en"], index=0)

with col1.container( border=True, key="image-container", height=st.session_state.height):

    st.title("Genes from Space Tool")



    point_source = st.selectbox("Select a tool", [ "Upload your own point observations", "Source points from GBIF", "Upload your own Polygons"], index=None,  placeholder="Select Point source")
    if point_source=="Upload your own point observations":
        st.write("Upload your own point observations")

    if point_source=="Source points from GBIF":
        st.write("Source points from GBIF")
        with st.form(key='GBIF', enter_to_submit=False):

            species=st.text_input("Species Name", placeholder="Example: Quercus sartorii")
            st.session_state.start_y=st.number_input("Start year", value=st.session_state.start_y, step=1, min_value=1900, max_value=2021)
            st.session_state.end_y=st.number_input("End year", value=None, step=1, min_value=1900, max_value=2021)
            region=st.radio("Area of interest selection", ["Map selection", "Country"])
            if st.form_submit_button("Submit"):
                if region=="Country":
                    st.session_state.stage="country"
                    st.session_state.bbox=None
                if region=="Map selection":
                    st.session_state.stage="bbox_draw"
                    st.session_state.country=None
    
        if st.session_state.end_y and region == "Country": 
            countries = st.multiselect("Select countries", country_names)
            bbox=[]
            st.write("Selected countries: ", countries)
            if countries:
                if st.button("Fetch Points"):
                    st.session_state.stage="Manipulate points"
                    st.session_state.bbox=None
                    st.session_state.country=countries
        if st.session_state.end_y and region=="Map selection":
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
                GBIF_response
                output_GBIF = get_output(GBIF_response.text)
                output_GBIF
                GBIF_output_code=output_GBIF["GFS_IndicatorsTool>GBIF_obs.yml@23"]
                GBIF_directory=f"/output/{GBIF_output_code}/obs_data.tsv"
                obs_file = open(f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/output/{GBIF_output_code}/GBIF_obs.csv")
                obs = pd.read_csv(obs_file, sep='\t')
                st.session_state.obs = obs

    if point_source=="Upload your own point observations":
        obs_link = st.file_uploader("Upload your own point observations", type=["csv", "tsv"], on_change=lambda: st.session_state.update(stage="Manipulate points"))
        st.session_state.obs = pd.read_csv(obs_link, sep="\t")

    if point_source=="Upload your own Polygons":
        poly_link= st.file_uploader("Upload your own polygons", type=["geojson"], on_change=lambda: st.session_state.update(stage="LC"))
        if poly_link:
            st.session_state.polygons = geojson.load(poly_link)
    if st.session_state.stage == "LC":
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


        rel_habitat_change_table = area_table.copy()
        for i in range(1, area_table.shape[1]):  # Start from the second column (index 1)
            rel_habitat_change_table.iloc[:, i] = (area_table.iloc[:, i] / area_table.iloc[:, 1] * 100) - 100



        rel_habitat_change_table = area_table.copy()
        for i in range(1, area_table.shape[1]):  # Start from the second column (index 1)
            rel_habitat_change_table.iloc[:, i] = (area_table.iloc[:, i] / area_table.iloc[:, 1] * 100) - 100


        NC= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/{cover_maps}/HabitatNC.tif"
        GAIN= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines{cover_maps}/HabitatGAIN.tif"
        LOSS= f"/Users/simonrabenmeister/Desktop/Genes_from_Space/bon-in-a-box-pipelines/{cover_maps}/HabitatLOSS.tif"

        if st.button("See results"):
            st.session_state.geojson_data = json.dumps({
            "pop_polygons": st.session_state.polygons,
            "area_table": area_table.to_dict(),
            "rel_habitat_change_table": rel_habitat_change_table.to_dict(),
            "NC": NC,
            "GAIN": GAIN,
            "LOSS": LOSS

            })
            st.switch_page("pages/2_Output_display.py")
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

    


        st.session_state.pop_polygons = geojson_data["pop_polygons"]
        st.session_state.NE= pd.DataFrame(geojson_data["NE"])
        st.session_state.area_table = pd.DataFrame(geojson_data["area_table"])
        st.session_state.rel_habitat_change_table  = pd.DataFrame(geojson_data["rel_habitat_change_table"])
        st.session_state.editable_df = pd.DataFrame(geojson_data["editable_df"])
        st.session_state.NC = geojson_data["NC"]
        st.session_state.GAIN = geojson_data["GAIN"]
        st.session_state.LOSS = geojson_data["LOSS"]
        st.session_state.properties = pd.DataFrame(geojson_data["properties"])



