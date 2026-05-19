import streamlit as st
import pandas as pd
import requests
import time
import numpy as np
import geojson
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection, shape
from shapely.ops import unary_union
import seaborn as sns
import glasbey
import geopandas as gpd
import os

texts = pd.read_csv("texts.csv").set_index("id")
def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")

def clean_geometry(geom):
    """Remove linestrings from geometry collections, keeping only polygon parts."""
    if geom.is_empty:
        return geom
    
    if geom.geom_type == 'GeometryCollection':
        # Extract only polygon and multipolygon geometries
        polys = [g for g in geom.geoms if g.geom_type in ['Polygon', 'MultiPolygon']]
        if polys:
            return unary_union(polys)
        return geom
    elif geom.geom_type == 'Polygon':
        return MultiPolygon([geom])
    elif geom.geom_type == 'MultiPolygon':
        return geom
    
    return geom

if "polygons" not in st.session_state:
    st.session_state.polygons = None

def get_output(response_code):
    while True:
        max_retries = 12
        history = None  # Initialize history variable
        for attempt in range(max_retries):
            try:
                history = requests.get(f"{st.session_state.api_link}api/history").json()
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
        
        output_bbiab= requests.get(f"{st.session_state.api_link}api/{response_code}/outputs").json()
        return output_bbiab
    
def GBIF(data):
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>GBIF_API.json/run"

    headers = {"Content-Type": "application/json"}
    return requests.post(url, json=data, headers=headers)

def LC_info(data):
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>LC_info.json/run"

    headers = {"Content-Type": "application/json"}

    return requests.post(url, json=data, headers=headers)

def LC_area(data):
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>LC_area.json/run"

    headers = {"Content-Type": "application/json"}

    return requests.post(url, json=data, headers=headers)


def TC_area(data):
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>TC_area.json/run"


    headers = {"Content-Type": "application/json"}

    return requests.post(url, json=data, headers=headers)

def Sensitivity(data):
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>sensitivity_analysis.json/run"

    headers = {"Content-Type": "application/json"}

    return requests.post(url, json=data, headers=headers)

@st.fragment
def edit_points():
    lat_col = "decimallatitude"
    lon_col = "decimallongitude"
    # Use edited version if it exists, otherwise fall back to original
    if st.session_state.get("obs_edit") is not None:
        obs = st.session_state.obs_edit
    else:
        obs = st.session_state.obs_original
        obs = obs.drop_duplicates(subset=[lat_col, lon_col]).reset_index(drop=True)
        st.session_state.obs_edit = obs.copy()



    obs_edit = st.session_state.obs_edit
    # Remove duplicate points based on latitude and longitude
    
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

    # Add the observations to the map
    fg = folium.FeatureGroup(name="Markers")
    for i, row in obs_edit.iterrows():
        corr=[row["decimallatitude"], row["decimallongitude"]]
        folium.CircleMarker(
            location=corr,
            radius=6,
            color="red" if st.session_state.index is not None and i in st.session_state.index else "green" if row.get("source") == "user_defined" else "blue",
            fill_opacity=1,
            fill=True,
            fill_color='lightblue'
        ).add_to(fg)
    draw = Draw(export=False, draw_options={
        'polyline': False,
        'polygon': True,
        'circle': False,
        'rectangle': True,
        'marker': False,
        'circlemarker': False
    }, edit_options={
        'edit': True,
        'remove': True
    })
    draw.add_to(m)
    st.session_state.output = st_folium(m, feature_group_to_add=fg, use_container_width=True)      
#Get the index of the clicked point
    if "all_drawings" in st.session_state.output and st.session_state.output["all_drawings"] != None:
        selected_indices = set()
        for drawing in st.session_state.output["all_drawings"]:
            geometry_data = drawing.get("geometry") if isinstance(drawing, dict) else None
            if geometry_data is None and isinstance(drawing, dict) and "type" in drawing and "coordinates" in drawing:
                geometry_data = drawing
            if geometry_data is None:
                continue

            try:
                drawn_geom = shape(geometry_data)
            except Exception:
                continue

            for i, row in obs_edit.iterrows():
                point = Point(row[lon_col], row[lat_col])
                if drawn_geom.contains(point) or drawn_geom.touches(point):
                    selected_indices.add(i)

        if selected_indices and st.session_state.index is not None:
            st.session_state.index = pd.Index(st.session_state.index).union(selected_indices)
        elif  st.session_state.index is None:
            st.session_state.index = pd.Index(list(selected_indices))
        if "all_drawings" in st.session_state and st.session_state.output["all_drawings"] != st.session_state.all_drawings:
            st.session_state["all_drawings"] = st.session_state.output["all_drawings"]
            st.rerun(scope="fragment")

    if "last_object_clicked" in st.session_state.output and st.session_state.output["last_object_clicked"] is not None:
        
        clicked_index = obs_edit.index[(obs_edit[lat_col] == st.session_state.output["last_object_clicked"]["lat"]) & 
        (obs_edit[lon_col] == st.session_state.output["last_object_clicked"]["lng"])]
        if st.session_state.index is not None:
            st.session_state.index = pd.Index(st.session_state.index).union(clicked_index)
        else:
            st.session_state.index = clicked_index

        if (
            "last_object_clicked" in st.session_state.output
            and st.session_state.output["last_object_clicked"] != st.session_state["last_object_clicked"]
        ):
            st.session_state["last_object_clicked"] = st.session_state.output["last_object_clicked"]
            st.rerun(scope="fragment")


    def remove_point(index):
        st.session_state.obs_edit=obs_edit.drop(index)
        st.session_state.index=None

    b1, b2 = st.columns([3, 1])
    with b1:
        if st.session_state.index is not None and not st.session_state.index.empty:
            st.button(rtext("1_3_3_4_bu2"), on_click=remove_point, args=(st.session_state.index,)) 
    with b2:

        if st.button("reset points"):
            st.session_state.obs_edit=st.session_state.obs_original
            st.session_state.obs_csv=None
            st.rerun(scope="fragment")





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

    with st.expander("advanced options"):
        st.session_state.index 
        def load_csv():
            try:
                st.session_state.obs_csv = pd.read_csv(st.session_state.csv_link, sep="\t")
                # Check if the required columns are present
                required_columns = ["decimallongitude", "decimallatitude"]
                if not all(col in st.session_state.obs_csv.columns for col in required_columns):
                    st.error(f"{rtext('1_3_2_err')}, {', '.join(required_columns)}")

            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
            if st.session_state.obs_csv is not None:
                st.session_state.obs_csv = st.session_state.obs_csv.assign(source="user_defined")
                st.session_state.obs_edit= pd.concat([st.session_state.obs_edit, st.session_state.obs_csv], ignore_index=True).drop_duplicates(subset=["decimallatitude", "decimallongitude"]).reset_index(drop=True)
            
            
        st.file_uploader(rtext("1_3_3_4_bu3"), key="csv_link",type=["csv"], on_change=lambda: load_csv())

@st.fragment
def polygon_clustering():
    if st.session_state.polyinfo["polygons"] is not None:
        st.session_state.original_polygons = st.session_state.polyinfo["polygons"]
    # Create a dummy DataFrame for point data
    points_df = pd.DataFrame(st.session_state.obs)
    # Convert the DataFrame to a GeoDataFrame
    points_gdf = gpd.GeoDataFrame(
        points_df,
        geometry=gpd.points_from_xy(points_df["decimallongitude"], points_df["decimallatitude"]),
        crs="EPSG:4326"
    )
    obs = st.session_state.obs
    
    if st.session_state.buffer is None and st.session_state.poly_creation != rtext("1_4_opt2"):
        # Display the points without edit functionality
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

        # Add the observations to the map
        fg = folium.FeatureGroup(name="Markers")
        for i, row in obs.iterrows():
            corr = [row["decimallatitude"], row["decimallongitude"]]
            folium.CircleMarker(
            location=corr,
            radius=6,
            color="blue",
            fill_opacity=1,
            fill=True,
            fill_color='lightblue'
            ).add_to(fg)

        st.session_state.output = st_folium(m, feature_group_to_add=fg, use_container_width=True)
    if st.session_state.poly_creation == rtext("1_4_opt1"):
        if st.session_state.buffer is not None and st.session_state.distance:
            st.session_state.polyinfo["polygons"] = None

            # Define the buffer radius in kilometers
            radius = st.session_state.buffer # Example: 10 km

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
            pop_distance = st.session_state.distance* 1000  # Convert maximum distance to meters
            # Assign population clusters
            circles_gdf["pop"] = ["pop_" + str(cluster) for cluster in fcluster(linkage_matrix, t=pop_distance, criterion="distance")]

            # Melt all circles from the same population into a MultiPolygon
            melted_clusters = circles_gdf.dissolve(by="pop").reset_index()
            # Resolve overlaps by assigning the overlap to the population with the lower number

            for i, row1 in melted_clusters.iterrows():
                for j, row2 in melted_clusters.iterrows():
                    if i >= j:
                        continue
                    if melted_clusters.iloc[i]["geometry"].intersects(melted_clusters.iloc[j]["geometry"]):
                        intersection = melted_clusters.iloc[i]["geometry"].intersection(melted_clusters.iloc[j]["geometry"])
                        if not intersection.is_empty:
                            # Assign the overlap to the population with the lower number
                            if int(i) < int(j):
                                melted_clusters.at[i, "geometry"] = melted_clusters.iloc[i]["geometry"].union(intersection)
                                melted_clusters.at[j, "geometry"] = melted_clusters.iloc[j]["geometry"].difference(intersection)
                            else:
                                melted_clusters.at[j, "geometry"] = melted_clusters.iloc[j]["geometry"].union(intersection)
                                melted_clusters.at[i, "geometry"] = melted_clusters.iloc[i]["geometry"].difference(intersection)
            # Create a feature collection from melted_clusters
            
            # Clean geometries to remove any linestrings from geometry collections
            melted_clusters["geometry"] = melted_clusters["geometry"].apply(clean_geometry)
            
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
            fg2= folium.FeatureGroup(name="Markers")
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons,  popup=folium.GeoJsonPopup(fields=["name"])))
            st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True)       


    if st.session_state.poly_creation == rtext("1_4_opt2"):
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
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
            'polyline': False,
            'polygon': True,
            'circle': False,
            'rectangle': True,
            'marker': False,
            'circlemarker': False
        }, edit_options={
            'edit': True,
            'remove': True
        })
        draw.add_to(m)
        fg2 = folium.FeatureGroup(name="Markers")
        if st.session_state.original_polygons is not None:
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True, height=st.session_state.height)

        obs['geometry'] = obs.apply(lambda row: Point((row["decimallongitude"], row["decimallatitude"])), axis=1)
        geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
        new_df = geo_df.set_crs(epsg=4326)
        new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)

        if st.session_state.output["all_drawings"] != [] and st.session_state.output["last_active_drawing"] is not None and st.session_state.buffer is not None :

            size=st.session_state.buffer*1000
            if st.button("Group observations by polygon"):

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
                    poly
                    feature = geojson.Feature(geometry=poly["geometry"], properties={"name": f"Pop {i+1}", "style": {"color": color}, "population_density": None})
                    features.append(feature)
                st.session_state.original_polygons = geojson.FeatureCollection(features)
                
                st.rerun(scope="fragment")
    
    if st.session_state.original_polygons is not None:
        st.write(f"{rtext('1_4_2_info')} {len(st.session_state.original_polygons['features'])}")

        if st.button(rtext("1_4_2_bu2")):
            
            st.session_state.polyinfo["polygons"]= st.session_state.original_polygons
            st.session_state.polyinfo["polygons"]
            
            
            st.session_state.zoom=st.session_state.output["zoom"]
            st.session_state.center=st.session_state.output["center"]
            st.session_state.stage = "LC"
            st.session_state.biab_dir
            st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
            os.makedirs(os.path.dirname(f"{st.session_state.biab_dir }{st.session_state.poly_directory}"), exist_ok=True)
            with open(f"{st.session_state.biab_dir }{st.session_state.poly_directory}", "w") as f:
                geojson.dump(st.session_state.polyinfo["polygons"], f)
            st.success("Polygons saved successfully.")
            del st.session_state.original_polygons
            st.rerun()





@st.fragment
def convert_df():
    polygons =   st.session_state.polyinfo["polygons"]
    if st.session_state.polygons["features"][0]["properties"]["population_density"] is None:
        for i in range(0, len(st.session_state.polygons["features"])):
            st.session_state.polygons["features"][i]["properties"].update({"population_density": "", "nenc": "", "size": ""})
    # Initialize folium map
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lon"]], zoom_start=2)

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
        st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
        os.makedirs(os.path.dirname(st.session_state.poly_directory), exist_ok=True)
        with open(st.session_state.poly_directory, "w") as f:
            geojson.dump(st.session_state.polygons, f)
        st.success("Polygons saved successfully.")
        st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
        st.rerun()
@st.fragment
def mapbbox():
    # Create the map
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)

    # Add the Draw tool to the map
    draw = Draw(
        export=False,
        draw_options={
            'polyline': False,  # Disable polyline
            'polygon': False,   # Disable polygon
            'circle': False,    # Disable circle
            'rectangle': True,  # Enable rectangle
            'marker': False,    # Disable marker
            'circlemarker': False  # Disable circle marker
        },
        edit_options={
            'edit': False,   # Enable editing of drawn shapes
            'remove': False  # Enable deleting of drawn shapes
        }
    )
    draw.add_to(m)

    # If GBIF data contains a bounding box, draw it on the map
    if st.session_state.GBIF_data["bbox"] is not None:
        bbox = st.session_state.GBIF_data["bbox"]
        rectangle = folium.Rectangle(
            bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
            color="blue",
            fill=True,
            fill_opacity=0.2
        )
        rectangle.add_to(m)

    # Display the map
    output = st_folium(m, use_container_width=True)

    # Get the bounding box of the last clicked polygon
    if output["last_active_drawing"] is not None:
        geometry = output["last_active_drawing"]["geometry"]

        # Update the bounding box in GBIF data
        def get_bounding_box(geom):
            coords = np.array(list(geojson.utils.coords(geom)))
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]

        st.session_state.GBIF_data["bbox"] = [float(coord) for coord in get_bounding_box(geometry)]

        # Update map center and zoom
        st.session_state.zoom = output["zoom"]
        st.session_state.center = output["center"]

        # Trigger a rerun to refresh the map with the new shape
        st.rerun()
