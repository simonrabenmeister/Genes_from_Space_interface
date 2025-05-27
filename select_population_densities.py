import streamlit as st
import folium
from streamlit_folium import st_folium

# Initialize Streamlit App
st.title("Select Population Densities")

# Check if confirmed polygons are available
if "confirmed_polygons" not in st.session_state:
    st.write("Please create and confirm polygons first.")
    st.stop()

# Load confirmed polygons
polygons = st.session_state.confirmed_polygons

# Initialize folium map
m = folium.Map(location=[0, 0], zoom_start=2)

# Add the polygons to the map
fg = folium.FeatureGroup(name="Polygons")
fg.add_child(folium.GeoJson(polygons, popup=folium.GeoJsonPopup(fields=["name", "population_density"])))
fg.add_to(m)

# Display the map
output = st_folium(m, width=700, height=500)

# Check if user clicked on a polygon
if output["last_active_drawing"]:
    selected_coords = output["last_active_drawing"]["geometry"]["coordinates"]
    for poly in polygons["features"]:
        if poly["geometry"]["coordinates"] == selected_coords:
            st.session_state.selected_polygon = poly["properties"]["name"]
            break

# If a polygon is selected, allow editing
if st.session_state.selected_polygon:
    selected_polygon = next(
        (poly for poly in polygons["features"]
         if poly["properties"]["name"] == st.session_state.selected_polygon),
        None
    )

    if selected_polygon:
        st.write(f"### Editing: {selected_polygon['properties']['name']}")

        new_density = st.number_input(
            "Population Density:",
            value=selected_polygon["properties"]["population_density"],
            step=1
        )

        if st.button("Update Population Density"):
            selected_polygon["properties"]["population_density"] = new_density
            st.success(f"Updated {selected_polygon['properties']['name']} to {new_density}")

# Save the updated polygons
if st.button("Save Polygons"):
    with open("/Users/simonrabenmeister/Desktop/Genes_from_Space/Genes_from_Space_interface/updated_polygons.geojson", "w") as f:
        geojson.dump(polygons, f)
    st.success("Polygons saved successfully.")
