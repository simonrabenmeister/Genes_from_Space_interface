import streamlit as st
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import json
import pycountry


LC_names = [
    "Most common land cover",
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
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The Name of the Species is used by the tool to source point data from GBIF. 
        The name has to be in Latin and spelled as in the GBIF Database. 
        We suggest that you check your species of interest on [GBIF](https://www.gbif.org/) and copy the Species name from there.
        ''')

def list_of_countries_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The selection you made uses Countries to define the area of interest. 
        It takes either one or multiple countries. 
        Make sure that the country names are spelled correctly and separated by a comma in the case of multiple ones.
        ''')

def years_of_interest_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        A list of years for which Land cover data should be extracted. 
        These years must fall within the range of 2000 to 2023 for Forest cover data 
        and 1998 to 2020 for Land cover data. The pipeline calculates Habitat loss 
        at these time intervals and displays them in a graph.
        ''')

def buffer_size_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The radius, in kilometers, used to define a buffer around species observation coordinates. 
        This determines the area considered as the population presence.
        ''')

def distance_between_populations_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The minimum distance, in kilometers, required to consider two groups of observations as separate populations. 
        This parameter helps in identifying distinct populations based on spatial clustering of observations.
        ''')

def ne_nc_ratio_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The ratio of the effective population size (Ne) to the census population size (Nc) for the studied species. 
        Multiple values can be provided, separated by commas, to explore different scenarios.
        ''')

def population_density_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The estimated density of the species populations, given as the number of individuals per square kilometer. 
        Multiple values can be provided, separated by commas, to explore different scenarios.
        ''')

def start_year_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The earliest year for retrieving species occurrence data. 
        This sets the start of the temporal range for the GBIF data to be retrieved. 
        We suggest setting this maximum 10 years before the start of the analysis.
        ''')

def end_year_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The latest year for retrieving species occurrence data. 
        This sets the end of the temporal range for the GBIF data to be retrieved. 
        Make sure that this doesn’t overlap too much with the Analysis timespan (first year of interest).
        ''')

def title_of_run_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        A descriptive title for the pipeline run. 
        This helps differentiate between multiple runs. 
        We suggest that Species name and Land cover type are mentioned.
        ''')

def land_cover_class_types_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        A list of land cover types produced by the ESA Climate Change Initiative (CCI). 
        These classes categorize all Land cover into 23 classes listed above.
        ''')

def upload_tsv_file_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        The tool uses Point observations to create population polygons. 
        You selected that you have preexisting observation data. 
        Please upload the file with coordinates here. You will be able to confirm the uploaded data 
        in the map viewer and remove specific data points by selecting them and pressing remove. 
        The file has to be in the following format: TSV (Tab separated values), 
        longitudinal and latitude in columns `decimal_longitude`, `decimal_latitude` and the coordinate system 
        has to be World Geodetic System 1984, used in GPS - EPSG:4326.
        ''')

def upload_geojson_file_info():
    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
        Population polygons describe the theoretical bounds of each population. 
        These can be either created by creating buffer zones around point observations 
        or more advanced methods like Species distribution models. 
        Please upload the file as a GeoJSON. You will then be able to confirm the uploaded file visualized on the map viewer.
        ''')

#1. TC_obs (Tree Canopy - Observations)
def TC_obs():
    Finished = False
    csv = mapcsv()
    if csv:
        upload_tsv_file_info()
        years = st.multiselect("Years of interest", list(range(1992, 2021)))
        years_of_interest_info()
        if years:
            buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
            buffer_size_info()
            if buffer_size:
                pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                distance_between_populations_info()
                if pop_distance:
                    ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                    ne_nc_ratio_info()
                    if ne_nc:
                        pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                        population_density_info()
                        if pop_density:
                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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


# 2. TC_bbox (Tree Canopy - Bounding Box)
def TC_bbox():
    Finished = False
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    species_name_info()
    if species:
        bbox = mapbbox()
        if bbox:
            years = st.multiselect("Years of interest", list(range(2000, 2024)))
            years_of_interest_info()
            if years:
                buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                buffer_size_info()
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    distance_between_populations_info()
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                        ne_nc_ratio_info()
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            population_density_info()
                            if pop_density:
                                start_year = st.text_input("Start year of the study", placeholder="Example: 1980")
                                start_year_info()
                                if start_year:
                                    end_year = st.text_input("End year of the study", placeholder="Example: 2020")
                                    end_year_info()
                                    if end_year:
                                        runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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

# 3. LC_country (Land Cover - Country)
def LC_country():
    Finished = False
    species = st.text_input("Name of the species", placeholder="Example: Species name", key="species")
    species_name_info()
    if species:
        country_names = [country.name for country in pycountry.countries]
        countries = st.multiselect("Select countries", country_names)
        list_of_countries_info()
        if countries:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            years_of_interest_info()
            if years:
                LC_class = st.multiselect("Land cover class types", options=LC_names, key="LC_class")
                land_cover_class_types_info()
                if LC_class:
                    buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15", key="buffer_size")
                    buffer_size_info()
                    if buffer_size:
                        pop_distance = st.text_input("Distance between populations", placeholder="Example: 25", key="pop_distance")
                        distance_between_populations_info()
                        if pop_distance:
                            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01", key="ne_nc")
                            ne_nc_ratio_info()
                            if ne_nc:
                                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000", key="pop_density")
                                population_density_info()
                                if pop_density:
                                    start_year = st.text_input("Start year of the study", placeholder="Example: 1980", key="start_year")
                                    start_year_info()
                                    if start_year:
                                        end_year = st.text_input("End year of the study", placeholder="Example: 2020", key="end_year")
                                        end_year_info()
                                        if end_year:
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

# 4. TC_polygon (Tree Canopy - Polygon)
def TC_poly():
    Finished = False
    geojson = str(json.dumps(mapgeojson()))
    upload_geojson_file_info()
    if geojson:
        years = st.multiselect("Years of interest", list(range(2000, 2024)))
        years_of_interest_info()
        if years:
            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
            ne_nc_ratio_info()
            if ne_nc:
                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                population_density_info()
                if pop_density:
                    runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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

# 5. LC_bbox (Land Cover - Bounding Box)
def LC_bbox():
    Finished = False
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    species_name_info()
    if species:
        bbox = mapbbox()
        if bbox:
            years = st.multiselect("Years of interest", list(range(1992, 2021)))
            years_of_interest_info()
            if years:
                LC_class = st.multiselect("Land cover class types", options=LC_names)
                land_cover_class_types_info()
                if LC_class:
                    buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                    buffer_size_info()
                    if buffer_size:
                        pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                        distance_between_populations_info()
                        if pop_distance:
                            ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                            ne_nc_ratio_info()
                            if ne_nc:
                                pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                                population_density_info()
                                if pop_density:
                                    start_year = st.text_input("Start year of the study", placeholder="Example: 1980")
                                    start_year_info()
                                    if start_year:
                                        end_year = st.text_input("End year of the study", placeholder="Example: 2020")
                                        end_year_info()
                                        if end_year:
                                            runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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


# 6. LC_obs (Land Cover - Observations)
def LC_obs():
    Finished = False
    csv = mapcsv()
    if csv:
        upload_tsv_file_info()
        years = st.multiselect("Years of interest", list(range(1992, 2021)))
        years_of_interest_info()
        if years:
            LC_class = st.multiselect("Land cover class types", options=LC_names)
            land_cover_class_types_info()
            if LC_class:
                buffer_size = st.text_input("Buffer size for polygons", placeholder="Example: 15")
                buffer_size_info()
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    distance_between_populations_info()
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                        ne_nc_ratio_info()
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            population_density_info()
                            if pop_density:
                                runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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

# 7. LC_polygon (Land Cover - Polygon)
def LC_poly():
    Finished = False
    geojson = str(json.dumps(mapgeojson()))
    upload_geojson_file_info()
    if geojson:
        years = st.multiselect("Years of interest", list(range(1992, 2021)))
        years_of_interest_info()
        if years:
            LC_class = st.multiselect("Land cover class types", options=LC_names)
            land_cover_class_types_info()
            if LC_class:
                ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01")
                ne_nc_ratio_info()
                if ne_nc:
                    pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                    population_density_info()
                    if pop_density:
                        runtitle = st.text_input("Title of the run", placeholder="Example: Analysis title")
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

# 8. TC_country (Tree Canopy - Country)
def TC_country():
    Finished = False
    species = st.text_input("Name of the species", placeholder="Example: Species name")
    species_name_info()
    if species:
        country_names = [country.name for country in pycountry.countries]
        countries = st.multiselect("Select countries", country_names)
        list_of_countries_info()
        if countries:
            years = st.multiselect("Years of interest", list(range(2000, 2024)))
            years_of_interest_info()
            if years:
                buffer_size = st.text_input("Buffer size for population polygons", placeholder="Example: 15")
                buffer_size_info()
                if buffer_size:
                    pop_distance = st.text_input("Distance between populations", placeholder="Example: 25")
                    distance_between_populations_info()
                    if pop_distance:
                        ne_nc = st.text_input("Ne:Nc ratio", placeholder="Example: 0.01, 0.1, 0.5")
                        ne_nc_ratio_info()
                        if ne_nc:
                            pop_density = st.text_input("Population density", placeholder="Example: 50, 100, 1000")
                            population_density_info()
                            if pop_density:
                                start_year = st.text_input("Start year of the study", placeholder="Example: 1980", key="start_year")
                                start_year_info()
                                if start_year:
                                    end_year = st.text_input("End year of the study", placeholder="Example: 2020", key="end_year")
                                    end_year_info()
                                    if end_year:
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

