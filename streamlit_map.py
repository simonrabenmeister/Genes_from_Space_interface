import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium.plugins as plugins
import geojson as gj


def mapcsv():
    obs=pd.DataFrame()

    obs_file = st.file_uploader("Choose a file")
    if obs_file is not None:
        # To read file as bytes:
        bytes_data = obs_file.getvalue()
        # Can be used wherever a "file-like" object is accepted:
        obs = pd.read_csv(obs_file, sep='\t')


        if "obs" not in st.session_state:
            st.session_state.obs= obs
        if "obs_edit" not in st.session_state:
            st.session_state.obs_edit= obs
        obs_edit=st.session_state.obs_edit
        if "center" not in st.session_state:
            st.session_state["center"] = [ 19.8,-96.85]  # Default center for the map
        if "out" not in st.session_state:
            st.session_state.out={}
        
        if "zoom" not in st.session_state:
            st.session_state["zoom"] = 8  # Default zoom level

        lat_col = "decimal_latitude"
        lon_col = "decimal_longitude"
        obs_edit=st.session_state.obs_edit

        def render_map():
            fg = folium.FeatureGroup(name="Markers")
            m = folium.Map(
                location=st.session_state["center"], 
                zoom_start=st.session_state["zoom"]
            )
            for i, row in obs_edit.iterrows():
                fg.add_child(folium.Marker(
                    location=[row[lat_col], row[lon_col]],
                    tooltip="Click to select",
                    icon=plugins.BeautifyIcon(icon="circle")
                ))
            st.session_state.out = st_folium(
                m,
                center=st.session_state["center"],
                zoom=st.session_state["zoom"],
                key="out",
                feature_group_to_add=fg,
                height=400,
                width=700,
            )
        render_map()

        index=obs_edit.index[(obs_edit[lat_col] == st.session_state.out["last_object_clicked"]["lat"]) & 
                                  (obs_edit[lon_col] == st.session_state.out["last_object_clicked"]["lng"])]


        if st.button("remove point"):
            st.session_state.obs_edit=obs_edit.drop(index)
            return str([tuple(obs_edit.columns)] + [tuple(x) for x in obs_edit.values])




def mapgeojson():

    poly=pd.DataFrame()

    poly_file = st.file_uploader("Choose a file")
    if poly_file is not None:
        # read geojson:
        poly_file = gj.load(poly_file)

        if "center" not in st.session_state:
            st.session_state["center"] = [ 19.8,-96.85]  # Default center for the map
        if "zoom" not in st.session_state:
            st.session_state["zoom"] = 8  # Default zoom level

        m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
        fg = folium.FeatureGroup(name="Markers")
        fg.add_child(folium.GeoJson(poly_file))
        


        st_folium(
                m,
                center=st.session_state["center"],
                zoom=st.session_state["zoom"],
                key="new",
                feature_group_to_add=fg,
                height=400,
                width=700,
                
            )
          