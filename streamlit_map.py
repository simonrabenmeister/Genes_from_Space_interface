import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium.plugins as plugins



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


    if "zoom" not in st.session_state:
        st.session_state["zoom"] = 8  # Default zoom level



    m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"], crs = 'EPSG4326')
    fg = folium.FeatureGroup(name="Markers")


    if st.button("remove point"):
        index=obs.index[obs["Lon"]==st.session_state.out["last_object_clicked"]["lat"]]
        obs_edit=obs_edit.drop([index[0]])
        st.session_state.obs_edit=obs_edit

        


    for i, row in obs_edit.iterrows():
        fg.add_child(folium.Marker(
            location=[row[1], row[2]],
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
    index=obs.index[obs["Lon"]==st.session_state.out["last_object_clicked"]["lat"]]
    st.write("removed Point with index", index[0])
    st.write(obs_edit)



