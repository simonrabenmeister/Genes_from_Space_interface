import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
import numpy as np
import geojson

m = folium.Map(location=[39.949610, -75.150282], zoom_start=5)
draw = Draw(export=True)
draw.add_to(m)

output = st_folium(m, width=700, height=500)

geometry = output["last_active_drawing"]["geometry"]

def get_bounding_box(geometry):
    coords = np.array(list(geojson.utils.coords(geometry)))
    return coords[:,0].min(), coords[:,0].max(), coords[:,1].min(), coords[:,1].max()

st.write(get_bounding_box(geometry))
