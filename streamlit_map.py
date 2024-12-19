import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium.plugins as plugins
import geojson as gj
from folium.plugins import Draw



def mapcsv():
    obs=pd.DataFrame()

    obs_file = st.file_uploader("Choose a file")
    if obs_file is not None:
        # To read file as bytes:
        bytes_data = obs_file.getvalue()
        # Can be used wherever a "file-like" object is accepted:
        obs = pd.read_csv(obs_file, sep='\t')
        st.write(obs)

        if "obs" not in st.session_state:
            st.session_state.obs= obs
        if "obs_edit" not in st.session_state:
            st.session_state.obs_edit= obs
        if "center" not in st.session_state:
            st.session_state["center"] = [ 19.8,-96.85]  # Default center for the map
        if "out" not in st.session_state:
            st.session_state.out={}
        if "index" not in st.session_state:
            st.session_state.index=None
        
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


        if st.session_state.out["last_object_clicked"] is not None:
            st.session_state.index=obs_edit.index[(obs_edit[lat_col] == st.session_state.out["last_object_clicked"]["lat"]) & 
            (obs_edit[lon_col] == st.session_state.out["last_object_clicked"]["lng"])]
        
        def remove_point(index):
            st.session_state.obs_edit=obs_edit.drop(index)

        st.button("remove_point", on_click=remove_point, args=(st.session_state.index,)) 

        csv=st.session_state.obs_edit.loc[:, [lat_col, lon_col]]
        return str([tuple(csv.columns)] + [tuple(x) for x in csv.values])
    




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
    
    return poly_file

def mapbbox():
    m = folium.Map(location=[39.949610, -75.150282], zoom_start=5)
    draw = Draw(export=True)
    draw.add_to(m)
   
    def get_bounding_box(geom):
        coords = np.array(list(gj.utils.coords(geom)))
        
        return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
    
    output = st_folium(m, width=700, height=500)
    if output["last_active_drawing"] is not None:
        geometry = output["last_active_drawing"]["geometry"]
        return get_bounding_box(geometry)
