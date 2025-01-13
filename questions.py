import streamlit as st
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import json
import pycountry


LC_names = [
    "AUTOMATIC: Don't want to specify / don't know (the tool will identify most common classes)",
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
    0, 10, 11, 12, 20, 30, 40, 50, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220
]
import streamlit as st

def species_name_info():
    st.markdown('###### Name of species')
    st.markdown('The species name is used by the tool to retrieve species observation coordinates from GBIF. Please ensure the name entered matches the scientific name in the [GBIF database](https://www.gbif.org/).')

def list_of_countries_info():
    st.markdown('###### Countries of interest')
    st.markdown('Choose one or more countries from which to retrieve species observations from GBIF. ')

def start_year_info():
    st.markdown('###### Period of species observation')
    st.markdown('Specify the start year and end year to define the time range for retrieving species observations from GBIF.')

def buffer_size_info():
    st.markdown('###### Distances for population definition')
    st.markdown('Using coordinates of species observations, the tool generates polygons representing the spatial distribution of populations. These polygons are determined based on two distances: the observation distance and the population distance, which you need to specify below in kilometers.')

    with st.expander("**-> What do these distances represent?**", expanded=False):
        st.markdown('''
        The species observation coordinates are first converted into circles, representing the local areas where the species is expected to occur. These circles are defined using the **observation distance**, which corresponds to the radius of the circles. This distance accounts for the potential margin of error associated with the observation coordinates.
        \nCircles that are geographically close to one another are merged into population polygons. This merging is based on the **population distance**, a threshold that defines the maximum distance within which individuals of the same species are expected to share genetic similarity. Distances beyond this threshold indicate a separation in different populations. 
        ''')
        st.image("images/distances_def.png")

def ne_nc_ratio_info():
    st.markdown('###### Parameters for population size estimation')
    st.markdown('The surface area of each population polygon is used to estimate the population size (census size, Nc) based on a specified population density. This estimate is then converted into an effective population size (Ne) using a specified Ne:Nc ratio. You can provide multiple alternative values for both population density and the Ne:Nc ratio below, separated by a comma.')

    with st.expander("**-> What do these parameters represent?**", expanded=False):
        st.markdown('''More info to be added here, with one figure.  
          ''')

def land_cover_class_types_info():
    st.markdown('######  Landcover classes for suitable habitat identification')
    st.markdown('The ESA Landcover dataset includes 23 classifiers representing various land use or vegetation types. You can specify below which of these categories constitute suitable habitat for the species being studied. Alternatively, **you can choose the option for the tool to automatically identify the most common landcover classes**, without the need for manual selection.')

    with st.expander("**Which landcover classes are described?**", expanded=False):
        st.markdown('''
        To be filled with figure of hierarhical list of lc classes. 
        ''')

def years_of_interest_info():
    st.markdown('######  Years of interest for habitat change')
    st.markdown('Choose the years of interest below to extract habitat change data, assess the potential size of suitable habitat over time, estimate population size, and compute the genetic diversity indicators. Note that the years typically begin after the species observation period specified above.')

def upload_tsv_file_info():
    st.markdown('######  Upload a species observation coordinates')
    st.markdown('''Click below to upload a tab-separated document containing the geographic coordinates of species occurrences.
                Once uploaded, the coordinates will be displayed on an interactive map. You can click on a point and use the "Remove" button to delete specific coordinates if needed. ''')

    with st.expander("**How should the document be formatted before upload?**", expanded=False):
        st.markdown('''
        The uploaded document must be in TSV (Tab-separated values) format. It should include columns labeled decimal_longitude and decimal_latitude for the geographic coordinates. Additionally, the coordinate system must be World Geodetic System 1984 (WGS 84), which is commonly used in GPS (EPSG:4326).
        ''')

def bbox_info():
    st.markdown('######  Draw the bounding box of the study area')
    st.markdown('Use the interactive map below to define the boundaries of the area of interest.')

def upload_geojson_file_info():
    st.markdown('######  Upload polygons of populations distribution')
    st.markdown('Click below to upload a geojson document containing the polygons defining the spatial distribution of populations.')

    with st.expander("**-> How should the geojson document be formatted before upload?**", expanded=False):
        st.markdown('''
        The uploaded document must be in GeoJSON format and can include multiple polygons representing the spatial distribution of the studied populations. Each polygon must have an attribute named “pop” that contains a unique identifier for each population (e.g., "pop_1," "pop_2," "pop_3," etc.). The coordinate system must be World Geodetic System 1984 (WGS 84), commonly used in GPS (EPSG:4326).
        ''')



def title_of_run_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        A descriptive title for the pipeline run. 
        This helps differentiate between multiple runs. 
        We suggest that Species name and Land cover type are mentioned.
        ''')

#1. TC_obs (Tree Canopy - Observations) ok
def TC_obs():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    upload_tsv_file_info()
    csv = mapcsv()
    if csv:
        buffer_size_info()
        buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
        pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
        if buffer_size and pop_distance:
                ne_nc_ratio_info()
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                if ne_nc and pop_density:
                        years_of_interest_info()       
                        years = st.multiselect("Years of interest", list(range(2000, 2023)))
                        if years: 
                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                            title_of_run_info()
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
                                Finished = True
                                return Finished


# 2. TC_bbox (Tree Canopy - Bounding Box) ok
def TC_bbox():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    species_name_info()
    species = st.text_input("Name of the species", placeholder="Example: Quercus sartorii")
    if species:
        bbox_info()
        bbox = mapbbox()
        if bbox:            
            start_year_info()
            start_year = st.text_input("Start year", placeholder="Example: 1980", key="start_year")
            end_year = st.text_input("End year", placeholder="Example: 2020", key="end_year")
            if start_year and end_year:
                buffer_size_info()
                buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
                pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
                if buffer_size and pop_distance:
                        ne_nc_ratio_info()
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                        pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                        if ne_nc and pop_density:
                                years_of_interest_info()       
                                years = st.multiselect("Years of interest", list(range(2000, 2023)))
                                if years: 
                                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                    title_of_run_info()
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
                                            Finished = True
                                            return Finished

# 3. LC_country (Land Cover - Country) ok
def LC_country():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    species_name_info()
    species = st.text_input("Name of the species", placeholder="Example: Quercus sartorii")
    if species:
        list_of_countries_info()
        country_names = [country.name for country in pycountry.countries]
        countries = st.multiselect("Select countries", country_names)
        if countries:
            start_year_info()
            start_year = st.text_input("Start year", placeholder="Example: 1980", key="start_year")
            end_year = st.text_input("End year", placeholder="Example: 2020", key="end_year")
            if start_year and end_year:
                buffer_size_info()
                buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
                pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
                if buffer_size and pop_distance:
                        ne_nc_ratio_info()
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                        pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                        if ne_nc and pop_density:
                            land_cover_class_types_info()
                            LC_class = st.multiselect("Select Land cover class(es)", options=LC_names, key="LC_class")
                            if LC_class:
                                years_of_interest_info()       
                                years = st.multiselect("Years of interest", list(range(1992, 2021)))
                                if years: 
                                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                    title_of_run_info()
                                    if runtitle:
                                        st.session_state.input = {
                                            "species": species,
                                            "countries": countries,
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
                                        Finished = True
                                        return Finished

# 4. TC_polygon (Tree Canopy - Polygon) ok
def TC_poly():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    upload_geojson_file_info()
    geojson = str(json.dumps(mapgeojson()))
    if geojson:
                ne_nc_ratio_info()
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                if ne_nc and pop_density:
                        years_of_interest_info()       
                        years = st.multiselect("Years of interest", list(range(2000, 2023)))
                        if years: 
                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                            title_of_run_info()
                            if runtitle:
                                st.session_state.input = {
                                    "geojson": geojson,
                                    "years": years,
                                    "ne_nc": list(map(float, ne_nc.split(','))),
                                    "pop_density": list(map(float, pop_density.split(','))),
                                    "runtitle": runtitle,
                                }
                                Finished = True
                                return Finished

# 5. LC_bbox (Land Cover - Bounding Box) ok
def LC_bbox():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    species_name_info()
    species = st.text_input("Name of the species", placeholder="Example: Quercus sartorii")
    if species:
        bbox_info()
        bbox = mapbbox()
        if bbox:            
            start_year_info()
            start_year = st.text_input("Start year", placeholder="Example: 1980", key="start_year")
            end_year = st.text_input("End year", placeholder="Example: 2020", key="end_year")
            if start_year and end_year:
                buffer_size_info()
                buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
                pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
                if buffer_size and pop_distance:
                        ne_nc_ratio_info()
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                        pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                        if ne_nc and pop_density:
                            land_cover_class_types_info()
                            LC_class = st.multiselect("Select Land cover class(es)", options=LC_names, key="LC_class")
                            if LC_class:
                                years_of_interest_info()       
                                years = st.multiselect("Years of interest", list(range(1992, 2021)))
                                if years: 
                                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                    title_of_run_info()
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
                                                Finished = True
                                                return Finished

# 6. LC_obs (Land Cover - Observations) ok

def LC_obs():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    upload_tsv_file_info()
    csv = mapcsv()    
    if csv:
        buffer_size_info()
        buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
        pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
        if buffer_size and pop_distance:
                ne_nc_ratio_info()
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                if ne_nc and pop_density:
                    land_cover_class_types_info()
                    LC_class = st.multiselect("Select Land cover class(es)", options=LC_names, key="LC_class")
                    if LC_class:
                        years_of_interest_info()       
                        years = st.multiselect("Years of interest", list(range(1992, 2021)))
                        if years: 
                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                            title_of_run_info()
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
                                    Finished = True
                                    return Finished

# 7. LC_polygon (Land Cover - Polygon) ok
def LC_poly():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    upload_geojson_file_info()
    geojson = str(json.dumps(mapgeojson()))
    if geojson:
                ne_nc_ratio_info()
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                if ne_nc and pop_density:
                    land_cover_class_types_info()
                    LC_class = st.multiselect("Select Land cover class(es)", options=LC_names, key="LC_class")
                    if LC_class:
                        years_of_interest_info()       
                        years = st.multiselect("Years of interest", list(range(1992, 2021)))
                        if years: 
                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                            title_of_run_info()
                            if runtitle:
                                st.session_state.input = {
                                "geojson": geojson,
                                "years": years,
                                "LC_class": [values[LC_names.index(name)] for name in LC_class],
                                "ne_nc": list(map(float, ne_nc.split(','))),
                                "pop_density": list(map(float, pop_density.split(','))),
                                "runtitle": runtitle,
                                }
                                Finished = True
                                return Finished

# 8. TC_country (Tree Canopy - Country) ok
def TC_country():
    st.divider()
    st.markdown('##### Step 3: Set run-specific parameters')
    Finished = False
    species_name_info()
    species = st.text_input("Name of the species", placeholder="Example: Quercus sartorii")
    if species:
        list_of_countries_info()
        country_names = [country.name for country in pycountry.countries]
        countries = st.multiselect("Select countries", country_names)
        if countries:
            start_year_info()
            start_year = st.text_input("Start year", placeholder="Example: 1980", key="start_year")
            end_year = st.text_input("End year", placeholder="Example: 2020", key="end_year")
            if start_year and end_year:
                buffer_size_info()
                buffer_size = st.text_input("Observation distance [km]", placeholder="Example: 1", key="buffer_size")
                pop_distance = st.text_input("Population distance [km]", placeholder="Example: 50", key="pop_distance")
                if buffer_size and pop_distance:
                        ne_nc_ratio_info()
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.1", key="ne_nc")
                        pop_density = st.text_input("Population density [individuals per km2]", placeholder="Example: 50, 100, 1000", key="pop_density")
                        if ne_nc and pop_density:
                                years_of_interest_info()       
                                years = st.multiselect("Years of interest", list(range(2000, 2023)))
                                if years: 
                                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title", key="runtitle")
                                    title_of_run_info()
                                    if runtitle:
                                            st.session_state.input = {
                                                "species": species,
                                                "countries": countries,
                                                "years": years,
                                                "buffer_size": float(buffer_size),
                                                "pop_distance": float(pop_distance),
                                                "ne_nc": list(map(float, ne_nc.split(','))),
                                                "pop_density": list(map(float, pop_density.split(','))),
                                                "runtitle": runtitle,
                                                "start_year": float(start_year),
                                                "end_year": float(end_year),
                                            }
                                            Finished = True
                                            return Finished

