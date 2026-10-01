import folium
import streamlit as st
from streamlit_folium import st_folium

m = folium.Map(location=[47.37, 8.54], zoom_start=12, tiles=None)

folium.TileLayer(
    tiles="http://127.0.0.1:8080/tile/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors",
    name="Local OSM",
    max_zoom=19,
).add_to(m)
folium.LayerControl().add_to(m)

st_folium(m, width=900, height=600)