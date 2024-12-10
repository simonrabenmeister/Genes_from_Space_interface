import streamlit as st
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import json


LC_names = [
    "Cropland, rainfed",
    "Herbaceous cover",
    "Tree or shrub cover",
    "Cropland, irrigated or post-flooding",
    "Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)",
    "Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)",
    "Tree cover, broadleaved, evergreen, closed to open (>15%)",
    "Tree cover, broadleaved, deciduous, closed to open (>15%)",
    "Tree cover, broadleaved, deciduous, closed (>40%)",
    "Tree cover, broadleaved, deciduous, open (15-40%)",
    "Tree cover, needleleaved, evergreen, closed to open (>15%)",
    "Tree cover, needleleaved, evergreen, closed (>40%)",
    "Tree cover, needleleaved, evergreen, open (15-40%)",
    "Tree cover, needleleaved, deciduous, closed to open (>15%)",
    "Tree cover, needleleaved, deciduous, closed (>40%)",
    "Tree cover, needleleaved, deciduous, open (15-40%)",
    "Tree cover, mixed leaf type (broadleaved and needleleaved)",
    "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)",
    "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)",
    "Shrubland",
    "Grassland",
    "Lichens and mosses",
    "Sparse vegetation (tree, shrub, herbaceous cover) (<15%)",
    "Tree cover, flooded, fresh or brackish water",
    "Tree cover, flooded, saline water",
    "Shrub or herbaceous cover, flooded, fresh/saline/brackish water",
    "Urban areas",
    "Bare areas",
    "Water bodies",
    "Permanent snow and ice"
]
values = [
    10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220
]
#1. TC_obs (Tree Canopy - Observations)
def TC_obs():
        csv = mapcsv()
        if csv:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            if years:
                buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            if pop_density:
                                runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                                if runtitle:
                                    st.session_state.input = {
                                        "csv": csv,
                                        "years": years,
                                        "buffer_size": float(buffer_size),
                                        "pop_distance": float(pop_distance),
                                        "ne_nc": list(map(float, ne_nc.split(','))),
                                        "pop_density": list(map(float, pop_density.split(','))),
                                        "runtitle": runtitle,
                                    }

# 2. TC_bbox (Tree Canopy - Bounding Box)
def TC_bbox():
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    if species:
        bbox = mapbbox()
        if bbox:
            years = st.multiselect("Years of interest", list(range(2000, 2024)))
            if years:
                buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            if pop_density:
                                start_year = st.text_input("Start year of the study", placeholder="Example: 1980")
                                if start_year:
                                    end_year = st.text_input("End year of the study", placeholder="Example: 2020")
                                    if end_year:
                                        runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                                        if runtitle:
                                            st.session_state.input = {
                                                "species": species,
                                                "bbox": bbox,
                                                "years": years,
                                                "buffer_size": float(buffer_size),
                                                "pop_distance": float(pop_distance),
                                                "ne_nc": list(map(float, ne_nc.split(','))),
                                                "pop_density": list(map(float, pop_density.split(','))),
                                                "start_year": float(start_year),
                                                "end_year": float(end_year),
                                                "runtitle": runtitle,
                                            }

# 3. LC_country (Land Cover - Country)
def LC_country():
    species = st.text_input("Name of the species", placeholder="Example: Species name", key="species")
    if species:
        countries = st.text_input("List of countries", placeholder="Example: Country1, Country2",  key="countries")
        if countries:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            if years:
                LC_class = st.multiselect("Land cover class types", options=LC_names, key="LC_class")
                if LC_class:
                    buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15", key="buffer_size")
                    if buffer_size:
                        pop_distance = st.text_input("Distance between populations", placeholder="Example: 25", key="pop_distance")
                        if pop_distance:
                            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01", key="ne_nc")
                            if ne_nc:
                                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000", key="pop_density")
                                if pop_density:
                                    start_year = st.text_input("Start year of the study", placeholder="Example: 1980", key="start_year")
                                    if start_year:
                                        end_year = st.text_input("End year of the study", placeholder="Example: 2020", key="end_year")
                                        if end_year:
                                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                            if runtitle:
                                                st.session_state.input = {
                                                    "species": species,
                                                    "countries": countries.split(", "),
                                                    "years": years,
                                                    "LC_class": [values[LC_names.index(name)] for name in LC_class],
                                                    "buffer_size": float(buffer_size),
                                                    "pop_distance": float(pop_distance),
                                                    "ne_nc": list(map(float, ne_nc.split(','))),
                                                    "pop_density": list(map(float, pop_density.split(','))),
                                                    "start_year": float(start_year),
                                                    "end_year": float(end_year),
                                                    "runtitle": runtitle,
                                                }

# 4. TC_polygon (Tree Canopy - Polygon)
def TC_poly():
    geojson = str(json.dumps(mapgeojson()))
    if geojson:
        years = st.multiselect("Years of interest", list(range(2000, 2024)))
        if years:
            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
            if ne_nc:
                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                if pop_density:
                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                    if runtitle:
                        st.session_state.input = {
                            "geojson": geojson,
                            "years": years,
                            "ne_nc": list(map(float, ne_nc.split(','))),
                            "pop_density": list(map(float, pop_density.split(','))),
                            "runtitle": runtitle,
                        }

# 5. LC_bbox (Land Cover - Bounding Box)
def LC_bbox():
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    if species:
        bbox = mapbbox()
        if bbox:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            if years:
                LC_class = st.multiselect("Land cover class types", options=LC_names)
                if LC_class:
                    buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                    if buffer_size:
                        pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                        if pop_distance:
                            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                            if ne_nc:
                                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                                if pop_density:
                                    start_year = st.text_input("Start year of the study", placeholder="Example: 1980")
                                    if start_year:
                                        end_year = st.text_input("End year of the study", placeholder="Example: 2020")
                                        if end_year:
                                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                                            if runtitle:
                                                st.session_state.input = {
                                                    "species": species,
                                                    "bbox": bbox,
                                                    "years": years,
                                                    "LC_class": [values[LC_names.index(name)] for name in LC_class],
                                                    "buffer_size": float(buffer_size),
                                                    "pop_distance": float(pop_distance),
                                                    "ne_nc": list(map(float, ne_nc.split(','))),
                                                    "pop_density": list(map(float, pop_density.split(','))),
                                                    "start_year": float(start_year),
                                                    "end_year": float(end_year),
                                                    "runtitle": runtitle,
                                                }

# 6. LC_obs (Land Cover - Observations)
def LC_obs():
        csv = mapcsv()
        if csv:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            if years:
                LC_class = st.multiselect("Land cover class types", options=LC_names)
                if LC_class:
                    buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                    if buffer_size:
                        pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                        if pop_distance:
                            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                            if ne_nc:
                                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                                if pop_density:
                                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                                    if runtitle:
                                        st.session_state.input = {
                                            "csv": csv,
                                            "years": years,
                                            "LC_class": [values[LC_names.index(name)] for name in LC_class],
                                            "buffer_size": float(buffer_size),
                                            "pop_distance": float(pop_distance),
                                            "ne_nc": list(map(float, ne_nc.split(','))),
                                            "pop_density": list(map(float, pop_density.split(','))),
                                            "runtitle": runtitle,
                                        }

# 7. LC_polygon (Land Cover - Polygon)
def LC_poly():
    geojson = str(json.dumps(mapgeojson()))
    if geojson:
        years = st.multiselect("Years of interest", list(range(1992, 2021)))
        if years:
            LC_class = st.multiselect("Land cover class types", options=LC_names)
            if LC_class:
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                if ne_nc:
                    pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                    if pop_density:
                        runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
                        if runtitle:
                            st.session_state.input = {
                                "geojson": geojson,
                                "years": years,
                                "LC_class": [values[LC_names.index(name)] for name in LC_class],
                                "ne_nc": list(map(float, ne_nc.split(','))),
                                "pop_density": list(map(float, pop_density.split(','))),
                                "runtitle": runtitle,
                            }
                            
def TC_country():
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    if species:
        countries = st.text_input("List of countries", placeholder="Example: Country1, Country2")
        if countries:
            years = st.multiselect("Years of interest", list(range(2000, 2024)))
            if years:
                buffer_size = st.text_input("Buffer size for population polygons", placeholder="Example: 15")
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01, 0.1, 0.5")
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            if pop_density:
                                    start_year = st.text_input("Start year of the study", placeholder="Example: 1980", key="start_year")
                                    if start_year:
                                        end_year = st.text_input("End year of the study", placeholder="Example: 2020", key="end_year")
                                        if end_year:
                                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                            if runtitle:
                                                st.session_state.input = {
                                                    "species": species,
                                                    "countries": countries.split(", "),
                                                    "years": years,
                                                    "buffer_size": float(buffer_size),
                                                    "pop_distance": float(pop_distance),
                                                    "ne_nc": list(map(float, ne_nc.split(','))),
                                                    "pop_density": list(map(float, pop_density.split(','))),
                                                    "runtitle": runtitle,
                                                    "start_year": float(start_year),
                                                    "end_year": float(end_year),
                                                }
