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

from logging_config import (
    get_logger,
    sanitize_headers,
    sanitize_json,
    safe_response_preview,
    truncate_text,
)

logger = get_logger(__name__)

texts = pd.read_csv("texts.csv").set_index("id")

def rtext(id):
    return texts.loc[id, st.session_state.lan].replace("\\n", "\n")

def _sid():
    """Get the current session ID for logging."""
    return st.session_state.get("session_id", "Unknown")

# ============================================================
# Error Handling
# ============================================================

class BiaBError(Exception):
    """Custom exception for Bon-in-a-Box errors with source classification."""
    def __init__(self, source, message, detail=None):
        self.source = source      # "connection", "server", or "pipeline"
        self.message = message
        self.detail = detail
        super().__init__(message)

def _handle_biab_response(response, pipeline_name):
    """
    Inspect an HTTP response from BiaB.
    Handles both JSON responses and plain-text run IDs.
    """
    logger.debug("Response for pipeline '%s'", pipeline_name)
    logger.debug("  Status code: %s", response.status_code)
    logger.debug("  Headers: %s", sanitize_headers(response.headers))
    logger.debug("  Body preview: %s", safe_response_preview(response))
    logger.debug("  Content-Type: %s", response.headers.get("Content-Type", "Unknown"))

    if response.status_code >= 400:
        try:
            body = response.json()
            detail = body.get("message", body.get("error", str(body)))
        except Exception:
            detail = response.text[:500] if response.text else f"HTTP {response.status_code}"

        logger.error("Server error for pipeline '%s' (HTTP %s): %s",
                     pipeline_name, response.status_code, truncate_text(detail))
        raise BiaBError(
            source="server",
            message=f"Server error (Bon-in-a-Box) — pipeline '{pipeline_name}' returned HTTP {response.status_code}",
            detail=detail
        )

    # Try to parse as JSON first
    try:
        json_data = response.json()
        logger.debug("Parsed JSON successfully: %s", sanitize_json(json_data))
        return json_data
    except ValueError as e:
        logger.debug("JSON parsing failed: %s", e)
        # If JSON fails, check if it's a plain text run ID
        text = response.text.strip()
        logger.debug("Raw text response: %r", truncate_text(text))

        # Heuristic: If the text looks like a run ID (alphanumeric, dashes, underscores)
        # and doesn't look like an error message, treat it as a successful run ID.
        if text and not text.startswith("Error") and not text.startswith("Traceback"):
            logger.debug("Treating as run ID: %s", text)
            # Return a standardized JSON object that get_output expects
            return {"runId": text}

        # If it's not a valid run ID, raise an error
        logger.error("Unexpected response format for pipeline '%s'", pipeline_name)
        raise BiaBError(
            source="server",
            message=f"Server error (Bon-in-a-Box) — pipeline '{pipeline_name}' returned unexpected format",
            detail=text[:500]
        )

def _call_biab_pipeline(pipeline_name, data):
    """
    Post to a BiaB pipeline endpoint with robust error handling.
    Returns parsed JSON on success. Raises BiaBError on failure.
    """
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>{pipeline_name}.json/run"
    headers = {"Content-Type": "application/json"}

    logger.debug("Calling pipeline: %s", pipeline_name)
    logger.debug("  URL: %s", url)
    logger.debug("  Request data: %s", sanitize_json(data))

    try:
        response = requests.post(url, json=data, headers=headers, timeout=120)
        logger.debug("Request sent, waiting for response...")
    except requests.exceptions.ConnectionError as e:
        logger.exception("Connection error calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — could not reach the Bon-in-a-Box server",
            detail=f"URL: {url}\nError: {str(e)}"
        )
    except requests.exceptions.Timeout as e:
        logger.exception("Timeout calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — request to Bon-in-a-Box timed out",
            detail=f"URL: {url}\nError: {str(e)}"
        )
    except requests.exceptions.RequestException as e:
        logger.exception("Request failed calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — request to Bon-in-a-Box failed",
            detail=str(e)
        )

    return _handle_biab_response(response, pipeline_name)

def _show_biab_error(error):
    """Display a BiaBError to the user with clear source labeling."""
    # Presentation layer: the originating error was already logged at the
    # point of detection, so log only at DEBUG here to avoid double-logging.
    logger.debug("Showing BiaBError to user (source=%s): %s", error.source, error.message)
    logger.debug("  Detail: %s", truncate_text(error.detail))

    if error.source == "connection":
        st.error(f"🔌 {error.message}")
    elif error.source == "server":
        st.error(f"🖥️ {error.message}")
        if error.detail:
            with st.expander("Server details"):
                st.code(error.detail)
    elif error.source == "pipeline":
        st.error(f"⚙️ {error.message}")
        if error.detail:
            with st.expander("Pipeline error details"):
                st.code(error.detail)

# ============================================================
# Pipeline Functions
# ============================================================

def GBIF(data):
    return _call_biab_pipeline("GBIF_API", data)

def LC_info(data):
    return _call_biab_pipeline("LC_info", data)

def LC_area(data):
    return _call_biab_pipeline("LC_area", data)

def TC_area(data):
    return _call_biab_pipeline("TC_area", data)

def Sensitivity(data):
    return _call_biab_pipeline("sensitivity_analysis", data)

def get_output(response_code):
    """
    Poll BiaB for job completion. Returns output JSON on success.
    Raises BiaBError on connection, server, or pipeline failure.
    """
    logger.debug("Starting get_output for runId: %s", response_code)

    max_retries = 12
    retry_delay = 2  # seconds
    history = None

    # 1. Fetch History with Retry Logic
    for attempt in range(max_retries):
        logger.debug("Attempt %d/%d to fetch history...", attempt + 1, max_retries)
        try:
            history = requests.get(f"{st.session_state.api_link}api/history", timeout=30).json()
            logger.debug("History fetched. Found %d entries.", len(history))
            break
        except requests.exceptions.RequestException as e:
            logger.warning("History fetch failed (attempt %d): %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.exception("Could not reach Bon-in-a-Box to check job status")
                raise BiaBError(
                    source="connection",
                    message="Connection error — could not reach Bon-in-a-Box to check job status",
                    detail=str(e)
                )
        except Exception as e:
            logger.warning("Unexpected error fetching history (attempt %d): %s", attempt + 1, e)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.exception("Invalid response when checking job status")
                raise BiaBError(
                    source="server",
                    message="Server error (Bon-in-a-Box) — invalid response when checking job status",
                    detail=str(e)
                )

    if history is None:
        logger.error("Failed to retrieve history after %d attempts", max_retries)
        raise BiaBError(
            source="server",
            message="Server error (Bon-in-a-Box) — failed to retrieve history after multiple attempts",
            detail=None
        )

    # 2. Find Job in History
    matching = [entry for entry in history if entry.get("runId") == response_code]
    if not matching:
        logger.error("Job '%s' not found in history", response_code)
        raise BiaBError(
            source="server",
            message=f"Server error (Bon-in-a-Box) — job '{response_code}' not found in history",
            detail=None
        )

    logger.debug("Job found. Initial status: %s", matching[0].get("status"))

    status = matching[0].get("status", "unknown")

    # 3. Poll Until Complete
    poll_count = 0
    while status == "running":
        poll_count += 1
        logger.debug("Poll %d: status 'running', waiting %ds...", poll_count, retry_delay)
        time.sleep(retry_delay)
        try:
            history = requests.get(f"{st.session_state.api_link}api/history", timeout=30).json()
            matching = [entry for entry in history if entry.get("runId") == response_code]
            if matching:
                status = matching[0].get("status", "unknown")
                logger.debug("Poll %d: status updated to '%s'", poll_count, status)
            else:
                logger.error("Poll %d: job '%s' disappeared from history", poll_count, response_code)
                raise BiaBError(
                    source="server",
                    message=f"Server error (Bon-in-a-Box) — job '{response_code}' disappeared from history",
                    detail=None
                )
        except requests.exceptions.RequestException as e:
            logger.exception("Poll %d: connection error while polling", poll_count)
            raise BiaBError(
                source="connection",
                message="Connection error — lost contact with Bon-in-a-Box while waiting for results",
                detail=str(e)
            )

    # 4. Handle Final Status
    logger.debug("Final status: %s", status)
    if status == "completed":
        logger.debug("Fetching outputs...")
        try:
            output = requests.get(f"{st.session_state.api_link}api/{response_code}/outputs", timeout=60).json()
            logger.debug("Outputs fetched. Keys: %s",
                         list(output.keys()) if isinstance(output, dict) else "not a dict")
            return output
        except requests.exceptions.RequestException as e:
            logger.exception("Error fetching outputs")
            raise BiaBError(
                source="connection",
                message="Connection error — could not retrieve pipeline outputs",
                detail=str(e)
            )
        except Exception as e:
            logger.exception("Error parsing outputs")
            raise BiaBError(
                source="server",
                message="Server error (Bon-in-a-Box) — pipeline outputs returned invalid data",
                detail=str(e)
            )
    else:
        # Status is 'failed', 'error', etc.
        logger.error("Job '%s' failed with status: %s", response_code, status)
        raise BiaBError(
            source="pipeline",
            message=f"Pipeline error (Bon-in-a-Box) — job ended with status: {status}",
            detail=f"runId: {response_code}"
        )

# ============================================================
# UI & Helper Functions
# ============================================================

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
    
    # Get the index of the clicked point
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
        elif st.session_state.index is None:
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
        st.session_state.obs_edit = obs_edit.drop(index)
        st.session_state.index = None

    b1, b2 = st.columns([3, 1])
    with b1:
        if st.session_state.index is not None and not st.session_state.index.empty:
            st.button(rtext("1_3_3_4_bu2"), on_click=remove_point, args=(st.session_state.index,), key="btn_remove_point") 
    with b2:
        if st.button("reset points", key="btn_reset_points"):
            st.session_state.obs_edit = st.session_state.obs_original
            st.session_state.obs_csv = None
            st.rerun(scope="fragment")

    st.markdown(rtext("1_3_3_4_te"))
    # Confirm points to be used
    if st.session_state.obs is None or not st.session_state.obs.equals(st.session_state.obs_edit):
        if st.button(rtext("1_3_3_4_bu1"), key="btn_confirm_points"):
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
                st.session_state.obs_edit = pd.concat([st.session_state.obs_edit, st.session_state.obs_csv], ignore_index=True).drop_duplicates(subset=["decimallatitude", "decimallongitude"]).reset_index(drop=True)
            
        st.file_uploader(rtext("1_3_3_4_bu3"), key="csv_link", type=["csv"], on_change=lambda: load_csv())

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
            # Assign population clusters
            pop_distance = st.session_state.distance * 1000
            # Melt all circles from the same population into a MultiPolygon
            circles_gdf["pop"] = ["pop_" + str(cluster) for cluster in fcluster(linkage_matrix, t=pop_distance, criterion="distance")]
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
                corr = [row["decimallatitude"], row["decimallongitude"]]
                folium.CircleMarker(
                    location=corr,
                    radius=6,
                    color="blue",
                    fill_opacity=1,
                    fill=True,
                    fill_color='lightblue'
                ).add_to(fg)
            fg2 = folium.FeatureGroup(name="Markers")
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
            st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True)       

    if st.session_state.poly_creation == rtext("1_4_opt2"):
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
        fg = folium.FeatureGroup(name="Markers")
        for i, row in obs.iterrows():
            corr = [row["decimallatitude"], row["decimallongitude"]]
            folium.CircleMarker(
                location=corr,
                radius=6,
                color="blue",
                fill_opacity=1,
                fill=True,
                # Add the Draw tool to the map
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
        fg2 = folium.FeatureGroup(name="Markers")
        if st.session_state.original_polygons is not None:
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True, height=st.session_state.height)

        obs['geometry'] = obs.apply(lambda row: Point((row["decimallongitude"], row["decimallatitude"])), axis=1)
        geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
        new_df = geo_df.set_crs(epsg=4326)
        new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)

        if st.session_state.output["all_drawings"] != [] and st.session_state.output["last_active_drawing"] is not None and st.session_state.buffer is not None:
            size = st.session_state.buffer * 1000
            if st.button("Group observations by polygon"):
                
                # Group the circles into clusters depending on drawn polygons
                circles = new_df['geometry'].buffer(size)
                obs['circles'] = circles.to_crs(epsg=4326)
                clusters = pd.DataFrame()
                for i in range(0, len(st.session_state.output["all_drawings"])):
                    polygon_coords = st.session_state.output["all_drawings"][i]["geometry"]["coordinates"][0]
                    polygon = Polygon(polygon_coords)
                    obs[f"Pop{i+1}"] = obs.apply(lambda row: polygon.contains(Point(row["decimallongitude"], row["decimallatitude"])), axis=1)
                    if obs[f"Pop{i+1}"].any():
                        polys = obs[obs[f"Pop{i+1}"]]['circles']
                        clusters = pd.concat([clusters, gpd.GeoDataFrame(geometry=[unary_union(polys)])], ignore_index=True)

                for i, row1 in clusters.iterrows():
                    for j, row2 in clusters.iterrows():
                        if i >= j:
                            continue
                        # Assign the overlap to the population with the lower number
                        if clusters.iloc[i]["geometry"].intersects(clusters.iloc[j]["geometry"]):
                            intersection = clusters.iloc[i]["geometry"].intersection(clusters.iloc[j]["geometry"])
                            if not intersection.is_empty:
                                if int(i) < int(j):
                                    clusters.iloc[i]["geometry"] = clusters.iloc[i]["geometry"].union(intersection)
                                    clusters.iloc[j]["geometry"] = clusters.iloc[j]["geometry"].difference(intersection)
                                else:
                                    clusters.iloc[j]["geometry"] = clusters.iloc[j]["geometry"].union(intersection)
                                    clusters.iloc[i]["geometry"] = clusters.iloc[i]["geometry"].difference(intersection)
                # Create a color palette for the clusters
                colors = glasbey.create_palette(palette_size=len(clusters), colorblind_safe=True, cvd_severity=100)
                sns.palplot(colors)
                # Create features to plot
                features = []
                for i, poly in clusters.iterrows():
                    color = colors[i % len(colors)]
                    feature = geojson.Feature(geometry=poly["geometry"], properties={"name": f"Pop {i+1}", "style": {"color": color}, "population_density": None})
                    features.append(feature)
                st.session_state.original_polygons = geojson.FeatureCollection(features)
                st.rerun(scope="fragment")
    
    if st.session_state.original_polygons is not None:
        st.write(f"{rtext('1_4_2_info')} {len(st.session_state.original_polygons['features'])}")
        st.session_state.zoom = st.session_state.output["zoom"]
        st.write("You can edit the polygons by clicking on them, or add new polygons using the drawing tool. if you are happy with your pupulation selection,click on  button to save the polygons and proceed to the next step.")
        bu1, bu2 = st.columns(2)
        with bu1:
            if st.button(rtext("1_4_2_bu2")):
                st.session_state.polyinfo["polygons"] = st.session_state.original_polygons
                st.session_state.stage = "LC"
                st.session_state.biab_dir
                st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
                os.makedirs(os.path.dirname(f"{st.session_state.biab_dir}{st.session_state.poly_directory}"), exist_ok=True)
                with open(f"{st.session_state.biab_dir}{st.session_state.poly_directory}", "w") as f:
                    geojson.dump(st.session_state.polyinfo["polygons"], f)
                st.success("Polygons saved successfully.")
                del st.session_state.original_polygons
                st.rerun()
        with bu2:
            if st.button("add polygons to map"):
                st.session_state.stage = "manual_polygon_creation"
                st.session_state.polygon_addition = st.session_state.original_polygons
                st.rerun()

@st.fragment
def manual_polygon_addition():
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
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
    if st.session_state.polygon_addition is not None:
        fg2.add_child(folium.GeoJson(st.session_state.polygon_addition, popup=folium.GeoJsonPopup(fields=["name"])))
    st.session_state.output = st_folium(m, feature_group_to_add=[fg2], key="add_polygons_map", use_container_width=True, height=st.session_state.height)
    
    if st.button("confirm polygons"):
        # Append new drawings with placeholder properties
        for i, drawing in enumerate(st.session_state.output["all_drawings"]):
            next_index = len(st.session_state.polygon_addition["features"])
            drawing["properties"] = {
                "name": f"Pop {next_index + 1}",
                "style": {"color": "gray"}
            }
            st.session_state.polygon_addition["features"].append(drawing)

        # Reassign colors to all features
        colors = glasbey.create_palette(
            palette_size=len(st.session_state.polygon_addition["features"]),
            colorblind_safe=True,
            cvd_severity=100
        )
        for i, feature in enumerate(st.session_state.polygon_addition["features"]):
            feature["properties"]["style"]["color"] = colors[i]
        st.rerun(scope="fragment")
    
    if st.button(rtext("1_4_2_bu2")):
        st.session_state.polyinfo["polygons"] = st.session_state.polygon_addition
        st.session_state.stage = "LC"
        st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
        os.makedirs(os.path.dirname(st.session_state.poly_directory), exist_ok=True)
        with open(st.session_state.poly_directory, "w") as f:
            geojson.dump(st.session_state.polyinfo["polygons"], f)
        st.success("Polygons saved successfully.")
        del st.session_state.polygon_addition
        del st.session_state.original_polygons
        st.rerun()

@st.fragment
def convert_df():
    polygons = st.session_state.polyinfo["polygons"]
    if st.session_state.polygons["features"][0]["properties"]["population_density"] is None:
        for i in range(0, len(st.session_state.polygons["features"])):
            # Initialize folium map
            st.session_state.polygons["features"][i]["properties"].update({"population_density": "", "nenc": "", "size": ""})
    
    # Add the polygons to the map
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lon"]], zoom_start=2)
    fg = folium.FeatureGroup(name="Polygons")
    # Display the map
    fg.add_child(folium.GeoJson(polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density", "nenc", "size"])))
    st.session_state.output2 = st_folium(m, feature_group_to_add=fg, use_container_width=True)

    with st.form(key='polygon', enter_to_submit=False):
        properties = pd.DataFrame(
            [{"Name": poly["properties"]["name"]} for poly in st.session_state.polygons["features"]]
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

        default_nenc = st.text_input("Default Ne:Nc", placeholder="Example: 0.1,0.5,0.9", key="nenc")
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
            st.session_state.polygons["features"][i]["properties"]["size"] = str(edited_df["size"][i])
        st.session_state.edited_df = edited_df
        
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

    # Add the Draw tool to the map
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
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