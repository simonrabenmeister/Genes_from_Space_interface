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
        obs = pd.read_csv(obs_file)


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



        m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
        fg = folium.FeatureGroup(name="Markers")

        if "last_object_clicked" in st.session_state.out:
            if st.button("remove point"):
                index=obs.index[obs["decimal_latitude"]==st.session_state.out["last_object_clicked"]["lat"]]
                obs_edit=obs_edit.drop([index[0]])
                st.session_state.obs_edit=obs_edit

            


        for i, row in obs_edit.iterrows():
            fg.add_child(folium.Marker(
                location=[row[0], row[1]],
                tooltip="Click to select",
                icon=plugins.BeautifyIcon(icon="circle")
            ))   
        st.session_state.out=st_folium(
            m,
            center=st.session_state["center"],
            zoom=st.session_state["zoom"],
            key="new",
            feature_group_to_add=fg,
            height=400,
            width=700,
            
        )
        index=obs.index[obs["decimal_latitude"]==st.session_state.out["last_object_clicked"]["lat"]]
        st.write("removed Point with index", index[0])
        st.write(obs_edit)

        if st.button("Commit"):
           csv_string=str([tuple(obs_edit.columns)] + [tuple(x) for x in obs_edit.values])
           st.write(csv_string)



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
          
            



mapgeojson()