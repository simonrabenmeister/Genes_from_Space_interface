import os
import numpy as np
import pandas as pd
import geopandas as gpd
import geojson
import glasbey
import seaborn as sns
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection, shape
from shapely.ops import unary_union
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
import streamlit as st
import tempfile
import zipfile
import requests
import time
import csv
import io
import json
import altair as alt
from logging_config import (
    get_logger,
    sanitize_headers,
    sanitize_json,
    safe_response_preview,
    truncate_text,
)
import math
import pyogrio

logger = get_logger(__name__)

texts = pd.read_csv("texts.csv").set_index("id")

def rtext(id):
    return texts.loc[id, st.session_state.lan].replace("\\n", "\n")

def _sid():
    """Get the current session ID for logging."""
    return st.session_state.get("session_id", "Unknown")

# Define a function to read/parse the input file regardless of format
def read_occurrence_file(uploaded_file):
    """Read an occurrence table as CSV or TSV, detecting the delimiter from content."""
    raw = uploaded_file.getvalue().decode("utf-8-sig")
    try:
        dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",\t;")
        sep = dialect.delimiter
    except csv.Error:
        sep = ","  # single-column / ambiguous file
    return pd.read_csv(io.StringIO(raw), sep=sep)

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
        obs_edit = st.session_state.obs_edit
    else:
        obs_edit = st.session_state.obs
        st.session_state.obs_original = st.session_state.obs
        obs_edit = obs_edit.drop_duplicates(subset=[lat_col, lon_col]).reset_index(drop=True)
        st.session_state.obs_edit = obs_edit.copy()


    
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

    b1, b2, b3 = st.columns([1, 1, 1])
    st.markdown(rtext("1_3_3_4_ti"))
    st.markdown(rtext("1_3_3_4_te"))
    # st.write(obs_edit["dataset_name"].unique())

    # Get unique dataset key / name pairs
    # unique_datasets = obs_edit[["datasetkey", "dataset_name"]].drop_duplicates()

    # # Build the GBIF dataset link for each
    # unique_datasets["gbif_link"] = "https://www.gbif.org/dataset/" + unique_datasets["datasetkey"]

    # for _, row in unique_datasets.iterrows():
    #     st.write(f"{row['dataset_name']}: {row['gbif_link']}")
    with b1:
        if st.session_state.index is not None and not st.session_state.index.empty:
            st.button(rtext("1_3_3_4_bu2"), on_click=remove_point, args=(st.session_state.index,), key="btn_remove_point") 
    with b2:
        if st.session_state.index is not None and not st.session_state.index.empty:
            if st.button("undo selection", key="btn_undo_selection"):
                st.session_state.index = None
                st.rerun(scope="fragment")
    with b3:

        if len(st.session_state.obs_original) != len(st.session_state.obs_edit):
            if st.button("reset points", key="btn_reset_points"):
                st.session_state.obs_edit = st.session_state.obs_original
                st.session_state.obs_csv = None
                st.rerun(scope="fragment")

    # Confirm points to be used
    st.markdown(rtext("1_3_3_4.2_te"))
    if st.button(rtext("1_3_3_4_bu1"), key="btn_confirm_points"):
        st.session_state.stage="polygon_clustering"
        st.session_state.obs_final = st.session_state.obs_edit
        st.session_state.poly_creation = None
        st.session_state.LC = {
            "LC_type": None,
            "LC_class": None,
            "index": None
        }  
        st.session_state.area_table = None
        st.session_state.cover_maps = None
        st.rerun()
    # Show a histogram of GBIF observations grouped by occurrence year.


def resolve_overlaps(ordered_geoms):
    """
    Given a list of (possibly overlapping) shapely geometries in a fixed
    order, return a same-length list of geometries where each one has had
    the union of all *earlier* geometries in the list subtracted from it.
 
    This is deterministic (result never depends on iteration order of a
    nested loop) and guarantees no two output geometries overlap, which
    is what actually eliminates the slivers / double-covered artifacts
    the pairwise intersect-then-union-then-difference approach produced.
    """
    claimed = None
    resolved = []
    for geom in ordered_geoms:
        geom = geom.buffer(0)  # fix self-intersections first
        if claimed is not None:
            geom = geom.difference(claimed)
        resolved.append(geom)
        claimed = geom if claimed is None else unary_union([claimed, geom])
    return resolved
 
 
def build_colored_features(geoms, names):
    """Zip geometries + names into glasbey-colored geojson Features."""
    colors = glasbey.create_palette(
        palette_size=max(len(geoms), 1), colorblind_safe=True, cvd_severity=100
    )
    features = []
    for i, (geom, name) in enumerate(zip(geoms, names)):
        features.append(
            geojson.Feature(
                geometry=geom,
                properties={"name": name, "style": {"color": colors[i % len(colors)]}},
            )
        )
    return features
 
 
@st.fragment
def polygon_clustering():
    if st.session_state.polyinfo["polygons"] is not None:
        st.session_state.original_polygons = st.session_state.polyinfo["polygons"]
 
    # Create a GeoDataFrame from the point data
    points_df = pd.DataFrame(st.session_state.obs_final)
    points_gdf = gpd.GeoDataFrame(
        points_df,
        geometry=gpd.points_from_xy(points_df["decimallongitude"], points_df["decimallatitude"]),
        crs="EPSG:4326",
    )
    obs = st.session_state.obs_final
 
    # =====================================================================
    # Option 1: automatic clustering by buffer radius + linkage distance
    # =====================================================================
    if st.session_state.poly_creation == rtext("1_4_opt1"):
 
        if st.session_state.buffer is not None and st.session_state.distance:
 
            current_params = (len(points_gdf), st.session_state.buffer, st.session_state.distance)

            needs_compute = (
                st.session_state.get("_poly_params_computed") != current_params
                or st.session_state.get("original_polygons") is None
            )
 
            if needs_compute:
                # --- only runs when buffer/distance/reset actually changed ---
                st.session_state.polyinfo["polygons"] = None
                radius_m = st.session_state.buffer * 1000
                dist_m = st.session_state.distance * 1000
 
                metric = points_gdf.to_crs(epsg=3857)
                circles_gdf = metric.copy()
                circles_gdf["geometry"] = metric.geometry.buffer(radius_m)
 
                coords = np.column_stack([metric.geometry.x, metric.geometry.y])
                linkage_matrix = linkage(pdist(coords), method="average")
                labels = fcluster(linkage_matrix, t=dist_m, criterion="distance")
                circles_gdf["pop"] = ["pop_" + str(c) for c in labels]
 
                melted_clusters = circles_gdf.dissolve(by="pop").reset_index()
                # fixed, stable order -> deterministic result
                melted_clusters = melted_clusters.sort_values("pop").reset_index(drop=True)
 
                resolved = resolve_overlaps(list(melted_clusters["geometry"]))
                melted_clusters["geometry"] = resolved
 
                # drop empties/slivers left over from differencing
                melted_clusters["geometry"] = melted_clusters.geometry.apply(lambda g: g.buffer(0))
                melted_clusters = melted_clusters[~melted_clusters.geometry.is_empty]
                melted_clusters = melted_clusters[melted_clusters.geometry.area > 0]
                melted_clusters = melted_clusters.set_geometry("geometry", crs=3857).to_crs(epsg=4326)
                melted_clusters = melted_clusters.reset_index(drop=True)
 
                features = build_colored_features(melted_clusters["geometry"], melted_clusters["pop"])
 
                st.session_state.original_polygons = geojson.FeatureCollection(features)
                st.session_state._poly_params_computed = current_params
 
                st.rerun()  # fires once per new buffer/distance submission (or reset)
 
            # This runs on every pass (including the rerun above), using
            # whatever original_polygons currently holds.
            m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]],   zoom_start=st.session_state.zoom)
 
            fg = folium.FeatureGroup(name="Points")
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
 
            fg2 = folium.FeatureGroup(name="Cluster polygons")
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
            st.session_state.output = st_folium(m, feature_group_to_add=[fg2], use_container_width=True)
 
    # =====================================================================
    # Option 2: manually drawn polygons used to group points into clusters
    # =====================================================================
    if st.session_state.poly_creation == rtext("1_4_opt2"):
        m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=st.session_state.zoom)
        fg = folium.FeatureGroup(name="Points")
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
        fg2 = folium.FeatureGroup(name="Drawn polygons")
        if st.session_state.original_polygons is not None:
            fg2.add_child(folium.GeoJson(st.session_state.original_polygons, popup=folium.GeoJsonPopup(fields=["name"])))
        st.session_state.output = st_folium(m, feature_group_to_add=[fg, fg2], use_container_width=True, height=st.session_state.height)
        st.markdown(rtext("1_4_1_1_te"))
        obs['geometry'] = obs.apply(lambda row: Point((row["decimallongitude"], row["decimallatitude"])), axis=1)
        geo_df = gpd.GeoDataFrame(obs, geometry=obs.geometry)
        new_df = geo_df.set_crs(epsg=4326)
        new_df['geometry'] = new_df['geometry'].to_crs(epsg=3857)
        st.session_state.buffer = st.number_input(rtext("1_4_2_plac1"), value=st.session_state.buffer, key="buffer_input", min_value=0.5, on_change=lambda: setattr(st.session_state, 'buffer', st.session_state.buffer_input))
        with st.expander(rtext("1_4_1_exp_ti"), expanded=False):
            st.markdown(rtext("1_4_1_exp_te"))
        if st.session_state.buffer is not None:
            setattr(st.session_state, 'buffer', st.session_state.buffer_input)
        if st.session_state.output["all_drawings"] != [] and st.session_state.output["last_active_drawing"] is not None and st.session_state.buffer is not None:
            size = st.session_state.buffer * 1000
            bu1, bu2 = st.columns(2)
            with bu1:
                if st.button("Group observations by polygon"):
 
                    # Group the circles into clusters depending on drawn polygons
                    circles = new_df['geometry'].buffer(size)
                    obs['circles'] = circles.to_crs(epsg=4326)
                    cluster_geoms = []
                    cluster_names = []
                    for i in range(0, len(st.session_state.output["all_drawings"])):
                        polygon_coords = st.session_state.output["all_drawings"][i]["geometry"]["coordinates"][0]
                        polygon = Polygon(polygon_coords)
                        obs[f"Pop{i+1}"] = obs.apply(lambda row: polygon.contains(Point(row["decimallongitude"], row["decimallatitude"])), axis=1)
                        if obs[f"Pop{i+1}"].any():
                            polys = obs[obs[f"Pop{i+1}"]]['circles']
                            cluster_geoms.append(unary_union(polys))
                            cluster_names.append(f"Pop {i+1}")
 
                    # Deterministic overlap resolution (fixed draw order),
                    # same helper used by the automatic clustering path.
                    resolved = resolve_overlaps(cluster_geoms)
                    clusters = gpd.GeoDataFrame({"name": cluster_names, "geometry": resolved})
                    clusters["geometry"] = clusters.geometry.apply(lambda g: g.buffer(0))
                    clusters = clusters[~clusters.geometry.is_empty]
                    clusters = clusters[clusters.geometry.area > 0].reset_index(drop=True)
 
                    features = build_colored_features(clusters["geometry"], clusters["name"])
                    st.session_state.original_polygons = geojson.FeatureCollection(features)
                    st.rerun(scope="fragment")
            if st.session_state.original_polygons is not None:
                with bu2:
                    if st.button(rtext("1_4_2_bu2")):
                        st.session_state.polyinfo["polygons"] = st.session_state.original_polygons
                        st.session_state.original_polygons = st.session_state.polyinfo["polygons"]
                        st.session_state.stage = "LC"
                        st.session_state.biab_dir
                        st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
                        os.makedirs(os.path.dirname(f"{st.session_state.biab_dir}{st.session_state.poly_directory}"), exist_ok=True)
                        with open(f"{st.session_state.biab_dir}{st.session_state.poly_directory}", "w") as f:
                            geojson.dump(st.session_state.polyinfo["polygons"], f)
                        st.success("Polygons saved successfully.")
                        del st.session_state.original_polygons
                        st.rerun()
                st.write("If you are satisfied with the polygons, Press Confirm Polygons. If you want to add manually drawn Polygons to the map, Press Add Polygons to Map.")
                if st.button("add polygons to map"):
                    st.session_state.stage = "manual_polygon_creation"
                    st.session_state.polygon_addition = st.session_state.original_polygons
                    st.rerun()
 
    if st.session_state.original_polygons is not None:
        st.write(f"{rtext('1_4_2_info')} {len(st.session_state.original_polygons['features'])}")

 

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
    bu1, bu2 = st.columns(2)
    st.markdown("Draw additional polygons on the map and press 'add drawn polygons to map' to add them to the existing polygons. Press 'Confirm Polygons' to save all polygons."
    )

    with bu1:
        if st.button("add drawn polygons to map"):
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
    with bu2:
        if st.button(rtext("1_4_2_bu2")):
            st.session_state.polyinfo["polygons"] = st.session_state.polygon_addition
            st.session_state.stage = "LC"
            st.session_state.poly_directory = os.path.join(f"/userdata/interface_polygons/", st.session_state.run_id, "updated_polygons.geojson")
            st.write(f"Saving polygons to: {st.session_state.poly_directory}")
            os.makedirs(os.path.dirname(f"{st.session_state.biab_dir}{st.session_state.poly_directory}"), exist_ok=True)
            with open(f"{st.session_state.biab_dir}{st.session_state.poly_directory}", "w") as f:
                geojson.dump(st.session_state.polyinfo["polygons"], f)
            st.success("Polygons saved successfully.")
            del st.session_state.polygon_addition
            st.rerun()

@st.fragment
def convert_df():
    polygons = st.session_state.polyinfo["polygons"]
    if st.session_state.polygons["features"][0]["properties"]["population_density"] is None:
        for i in range(0, len(st.session_state.polygons["features"])):
            # Initialize folium map
            st.session_state.polygons["features"][i]["properties"].update({"population_density": "", "nenc": "", "size": ""})
    
    # Add the polygons to the map
    m = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lon"]], zoom_start=st.session_state.zoom)
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


        # Trigger a rerun to refresh the map with the new shape
        st.rerun()




def compute_fit_zoom_from_bounds(lat_min, lat_max, lng_min, lng_max,
                                  map_width_px=800, map_height_px=500,
                                  padding=1.15, max_zoom=18, min_zoom=1):
    """
    Largest integer zoom level at which a Leaflet-style map (256px tiles)
    of size map_width_px x map_height_px can show the given lat/lng
    bounding box without clipping.
    """
    if lat_min == lat_max and lng_min == lng_max:
        return max_zoom

    def lat_rad(lat):
        sin = math.sin(lat * math.pi / 180)
        rad_x2 = math.log((1 + sin) / (1 - sin)) / 2
        return max(min(rad_x2, math.pi), -math.pi) / 2

    lat_fraction = (lat_rad(lat_max) - lat_rad(lat_min)) / math.pi

    lng_diff = lng_max - lng_min
    lng_fraction = (lng_diff if lng_diff >= 0 else lng_diff + 360) / 360

    world_dim = 256  # tile size in px at zoom 0

    def zoom_for_fraction(map_px, fraction):
        if fraction <= 0:
            return max_zoom
        return math.floor(math.log((map_px / padding) / world_dim / fraction, 2))

    lat_zoom = zoom_for_fraction(map_height_px, lat_fraction)
    lng_zoom = zoom_for_fraction(map_width_px, lng_fraction)

    return int(max(min_zoom, min(lat_zoom, lng_zoom, max_zoom)))


def compute_fit_zoom(lats, lngs, map_width_px=800, map_height_px=500,
                      padding=1.15, max_zoom=18, min_zoom=1):
    """Point-array convenience wrapper around compute_fit_zoom_from_bounds."""
    lat_min, lat_max = float(np.min(lats)), float(np.max(lats))
    lng_min, lng_max = float(np.min(lngs)), float(np.max(lngs))
    return compute_fit_zoom_from_bounds(
        lat_min, lat_max, lng_min, lng_max,
        map_width_px=map_width_px, map_height_px=map_height_px,
        padding=padding, max_zoom=max_zoom, min_zoom=min_zoom,
    )


def polygon_bounds(feature_collection):
    """
    Return (lat_min, lat_max, lng_min, lng_max) covering every geometry
    in a GeoJSON FeatureCollection (dict or geojson.FeatureCollection).
    Raises ValueError if the collection has no features.
    """
    features = feature_collection["features"]
    if not features:
        raise ValueError("polygon_bounds: FeatureCollection has no features")

    lng_min = lat_min = float("inf")
    lng_max = lat_max = float("-inf")
    for feature in features:
        geom = shape(feature["geometry"])
        minx, miny, maxx, maxy = geom.bounds  # (lng_min, lat_min, lng_max, lat_max)
        lng_min = min(lng_min, minx)
        lng_max = max(lng_max, maxx)
        lat_min = min(lat_min, miny)
        lat_max = max(lat_max, maxy)
    return lat_min, lat_max, lng_min, lng_max


def load_shapefile_zip(poly_link):
    """
    poly_link: an uploaded .zip file (e.g. from st.file_uploader) containing
    a shapefile's .shp/.shx/.dbf/.prj components — possibly nested inside a
    subfolder within the zip (searched recursively). Returns a
    geojson.FeatureCollection in EPSG:4326, reusing existing 'name'/'style'
    color attributes when present. Rebuilds a missing/corrupt .shx if needed.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(poly_link.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp_dir)

        shp_path = None
        for root, _, files in os.walk(tmp_dir):
            for fname in files:
                if fname.lower().endswith(".shp"):
                    shp_path = os.path.join(root, fname)
                    break
            if shp_path:
                break
        if shp_path is None:
            raise ValueError("No .shp file found inside the uploaded zip.")

        # Allow GDAL to rebuild a missing/corrupt .shx instead of erroring out
        pyogrio.set_gdal_config_options({"SHAPE_RESTORE_SHX": "YES"})
        gdf = gpd.read_file(shp_path)

    if gdf.crs is None:
        st.warning("Shapefile has no .prj / CRS defined — assuming EPSG:4326.")
        gdf = gdf.set_crs(epsg=4326)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    if "name" not in gdf.columns:
        gdf["name"] = [f"Pop {i+1}" for i in range(len(gdf))]

    def existing_color(row):
        val = row.get("style")
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict) and "color" in parsed:
                    return parsed["color"]
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    colors = glasbey.create_palette(
        palette_size=max(len(gdf), 1), colorblind_safe=True, cvd_severity=100
    )

    features = []
    for i, row in gdf.iterrows():
        color = existing_color(row) or colors[i % len(colors)]
        features.append(
            geojson.Feature(
                geometry=row["geometry"].__geo_interface__,
                properties={"name": row["name"], "style": {"color": color}},
            )
        )
    return geojson.FeatureCollection(features)
