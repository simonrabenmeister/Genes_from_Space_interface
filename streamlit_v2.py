import streamlit as st
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import pandas as pd
import json
import pycountry


##Page configuration
st.set_page_config(
    page_title="Genes from Space Monitoring Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://teams.issibern.ch/genesfromspace/',
        'Report a bug': "https://teams.issibern.ch/genesfromspace/",
    }
)

# Load texts
texts = pd.read_csv("texts.csv").set_index("id")
lan = st.radio("Select Language", ["en"], index=0)

# function to render text
def rtext(id):
        return texts.loc[id,lan].replace("\\n","\n")

### Set ESA LC classes

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


### Set API calls

import requests




def TC_obs():
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Forest_cover_v_obs_server.json/run"

    data = {
        "GFS_IndicatorsTool>read_csv.yml@58|csv": csv,
        "pipeline@41": buffer_size,
        "pipeline@42": pop_distance,
        "pipeline@44": years,
        "pipeline@45": ne_nc,
        "pipeline@46": title,
        "pipeline@47": pop_density,
        "pipeline@52": Name,
        "pipeline@53": Email
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response


def TC_bbox():
     
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Forest_cover_v_GBIF_bbox.json/run"
    data = {
        "pipeline@211": species,
        "pipeline@212": bbox,
        "pipeline@213": buffer_size,
        "pipeline@214": pop_distance,
        "pipeline@215": end_year,
        "pipeline@216": start_year,
        "pipeline@217": years,
        "pipeline@218": title,
        "pipeline@219": ne_nc,
        "pipeline@220": pop_density,
        "pipeline@221": Name,
        "pipeline@222": Email
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_country():

    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_countries.json/run"

    data = {
        "pipeline@186": species,
        "pipeline@187": end_year,
        "pipeline@188": countries,
        "pipeline@189": buffer_size,
        "pipeline@190": pop_distance,
        "pipeline@191": start_year,
        "pipeline@193": years,
        "pipeline@194": LC_class,
        "pipeline@195": ne_nc,
        "pipeline@196": title,
        "pipeline@197": pop_density,
        "pipeline@199": Name,
        "pipeline@200": Email
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)

    return response


def TC_country():

    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Forest_cover_v_GBIF_countries.json/run"

    data = {
        "pipeline@207": years,
        "pipeline@208": species,
        "pipeline@209": countries,
        "pipeline@210": end_year,
        "pipeline@211": buffer_size,
        "pipeline@212": pop_distance,
        "pipeline@213": start_year,
        "pipeline@214": ne_nc,
        "pipeline@215": title,
        "pipeline@216": pop_density,
        "pipeline@218": Name,
        "pipeline@219": Email
    }
    headers = {"Content-Type": "application/json"}

    print(data)
    
    response = requests.post(url, json=data, headers=headers)
    return response


def TC_poly():
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Forestcover_v_polygon.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_GFW_tree_canopy_2000-2023.json@33|pipeline@38": years,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": title,
        "pipeline@40": geojson
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_bbox():
    
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Land_cover_v_GBIF_bbox.json/run"

    data = {
        "pipeline@185": years,
        "pipeline@186": LC_class,
        "pipeline@187": species,
        "pipeline@188": bbox,
        "pipeline@190": buffer_size,
        "pipeline@191": pop_distance,
        "pipeline@192": start_year,
        "pipeline@193": end_year,
        "pipeline@194": Name,
        "pipeline@195": Email,
        "pipeline@198": ne_nc,
        "pipeline@199": title,
        "pipeline@200": pop_density
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_obs():
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Landcover_v_obs_server.json/run"

                          
    data = {
        "GFS_IndicatorsTool>read_csv.yml@42|csv": csv,
        "pipeline@43": pop_distance,
        "pipeline@44": buffer_size,
        "pipeline@45": LC_class,
        "pipeline@46": years,
        "pipeline@47": ne_nc,
        "pipeline@48": title,
        "pipeline@49": pop_density,
        "pipeline@55": Name,
        "pipeline@56": Email
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


def LC_poly():
    url = "https://run.gfstool.com/pipeline/GenesFromSpace>Tool>Landcover_v_polygon.json/run"

    data = {
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@123": years,
        "GenesFromSpace>ToolComponents>GetHabitatMaps>GFS_Habitat_map_Landcover_1992_2020.json@39|pipeline@124": LC_class,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|ne_nc": ne_nc,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|pop_density": pop_density,
        "GenesFromSpace>ToolComponents>GetIndicators>GFS_Indicators.json@32|GFS_IndicatorsTool>get_Indicators.yml@162|runtitle": title,
        "pipeline@38": geojson
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    return response


##Header
st.markdown("# Genes from Space Monitoring Tool")
st.markdown(rtext('h_title'))
with st.expander(rtext('h_exp1_ti')):
     st.markdown(rtext('h_exp1_te'))


with st.expander(rtext('h_exp2_ti'), expanded=False):
        st.markdown(rtext('h_exp2_te'))
        st.image("images/pipeline_description.png")

with st.expander(rtext('h_exp3_ti'), expanded=False):
        st.markdown(rtext('h_exp3_te'))


st.divider() 


### Interactive form

st.markdown(rtext('0_ti'))
st.markdown(rtext('0_te'))


### 1. Define population polygons
st.markdown(rtext('1_ti'))
st.markdown(rtext('1_te'))

with st.expander(rtext('1_exp_ti'), expanded=False):
    st.markdown(rtext('1_exp_te'))

### 1.1 - species name
st.markdown(rtext('1_1_ti'))
st.markdown(rtext('1_1_te'))

species = st.text_input(rtext('1_1_in'), placeholder="Example: Quercus sartorii")

# create empty containers of inputs 
PI=False
start_year=False
end_year=False
buffer_size=False
pop_distance=False
geojson=False
LC_mode=False
LCtype=False
LC_class=False
years=False
area_type=False
ne_nc=False
pop_density=False
bbox=False
countries=False
title=False
Name=False
Email=False

if species:

### 1.2 - pop definition
    st.markdown(rtext('1_2_ti'))
    st.markdown(rtext('1_2_te'))

    poly=st.radio(
        rtext('1_2_in'),
        key="visibility",
        options=["yes", "no"],
        index=None,
        disabled=True
    )
    poly="no"

### 1.3.a: if pop polygons available
    if (poly=='yes'):
        st.markdown(rtext('1_3a_ti'))
        st.markdown(rtext('1_3a_te'))

        with st.expander(rtext('1_3a_ex_ti'), expanded=False):
            st.markdown(rtext('1_3a_ex_te'))
        
        geojson = str(json.dumps(mapgeojson()))

        if (geojson!='null'):

            PI="geojson"

### 1.3.b: if pop poly not available: GBIF or custom input? 
    if (poly=="no"):
        
        st.markdown(rtext('1_3b_te'))
        
        with st.expander(rtext('1_3b_ex_ti'), expanded=False):
            st.markdown(rtext('1_3b_ex_te'))
            st.image("images/polygons_option1.png")
            st.image("images/polygons_option2.png")

    
        points=st.radio(
            rtext('1_3b_in'),
            options=["User-provided","Retrieved from GBIF"],
            index=None
        )

## 1.3.b.1 User provided obs

        if points=="User-provided":
                
                st.markdown(rtext('1_3b1_ti'))
                st.markdown(rtext('1_3b1_te'))

                with st.expander(rtext('1_3b1_ex_ti'), expanded=False):
                    st.markdown(rtext('1_3b1_ex_te'))

                csv = mapcsv()    

                if csv:
                    PI='UP'

### 1.3.b.2 GBIF retrieved obs

        if points=="Retrieved from GBIF":
                area_type=st.radio(
                    rtext('1_3b2_in'),
                    options=["Bounding box", "Country"],
                    index=None
                )

### 1.3.b.2.1 - set study area by bounding box                        

                if area_type=='Bounding box':
                     
                    st.markdown(rtext('1_3b21_ti'))
                    st.markdown(rtext('1_3b21_te'))

                    bbox = mapbbox()
                    st.write("boundry selected:",[bbox[0], bbox[1], bbox[2], bbox[3]])
                    if bbox: 
                        PI=area_type

                        
### 1.3.b.2.2 - set study area by country                        

                if area_type=='Country':
                    
                    st.markdown(rtext('1_3b22_ti'))
                    st.markdown(rtext('1_3b22_te'))

                    country_names = [country.name for country in pycountry.countries]
                    countries = st.multiselect("Select countries", country_names)
                    
                    if countries: 
                        PI=area_type

### 1.4: set temporal frame of species observation

if (PI):

    st.markdown(rtext('1_4_ti'))
    if (PI=='Country' or PI=='Bounding box'):
        st.markdown(rtext('1_4_te1'))
    if (PI=='UP'):
        st.markdown(rtext('1_4_te2'))
    if (PI=='geojson'):
        st.markdown(rtext('1_4_te3'))

    start_year = st.number_input(rtext('1_4_in1'), min_value=1950, max_value=2025, value=None)
    end_year = st.number_input(rtext('1_4_in2'),  min_value=1950, max_value=2025, value=None)

### 1.5: set parameters to calculate polygons

if start_year and end_year:

    if (PI=='geojson'):
        buffer_size=pop_distance='Ignore'
    
    else:
    
        st.markdown(rtext('1_5_ti'))
        st.markdown(rtext('1_5_te'))

        with st.expander(rtext('1_5_ex_ti'), expanded=False):
            st.markdown(rtext('1_5_ex_te'))
            st.image("images/distances_def.png")
        buffer_size = st.text_input(rtext('1_5_in1'), placeholder="Example: 1", key="buffer_size")
        pop_distance = st.text_input(rtext('1_5_in2'), placeholder="Example: 50", key="pop_distance")

### 2. define habitat change

if buffer_size and pop_distance:
     
    st.divider()
    st.markdown(rtext('2_ti'))
    st.markdown(rtext('2_te'))

    with st.expander(rtext('2_ex_ti'), expanded=False):
        st.markdown(rtext('2_ex_te')
    )


### 2.1. set habitat change variable

    LCtype= st.selectbox(
            rtext('2_1_in'),
            ('Landcover (ESA)', 'Tree cover (GFW)'),
            index=None,
            placeholder="Select habitat change dataset")

### 2.1.1. Select LC class 


    if LCtype=='Landcover (ESA)':
            
            st.markdown(rtext('2_1_1_ti'))
            st.markdown(rtext('2_1_1_te'))

            with st.expander(rtext('2_1_1_ex_ti'), expanded=False):
                st.markdown(rtext('2_1_1_ex_te'))
                st.image("images/LC_types.png")
            
            LC_mode= st.selectbox(
            rtext('2_1_1_in1'),
            ('automatic (most common)', 'manual'),
            index=None)

            if (LC_mode=='automatic (most common)'):
                LC_class = [0]
            if (LC_mode=='manual'):
                LC_class = st.multiselect(rtext('2_1_1_in2'), options=LC_names, key="LC_class")
                LC_class = [values[LC_names.index(name)] for name in LC_class]
    if LCtype=='Tree cover (GFW)':
                LC_class = 'Ignore'

# 2.2. Years of interest - habitat change

if LC_class:
     
    st.markdown(rtext('2_2_ti'))
    st.markdown(rtext('2_2_te'))

    if LCtype=='Landcover (ESA)':
        years = st.multiselect(rtext('2_2_in1'), list(range(1992, 2021)))

    if LCtype=='Tree cover (GFW)':
        years = st.multiselect(rtext('2_2_in2'), list(range(2000, 2023)))

### 3. Paramters of indicators estimation
        
if years:
    
    st.divider()
    st.markdown(rtext('3_ti'))
    st.markdown(rtext('3_te'))

    with st.expander(rtext('3_ex_ti'), expanded=False):
        st.markdown(rtext('3_ex_te'))      

    ne_nc = st.text_input(rtext('3_in1'), placeholder="Example: 0.1 or 0.1,0.2", key="ne_nc").split(',')
    pop_density = st.text_input(rtext('3_in2'), placeholder="Example: 50 or 50,100,1000", key="pop_density").split(',')

if ne_nc and pop_density:

#### 4. Name and email

    st.markdown(rtext('4_ti'))
    st.markdown(rtext('4_te'))

    Name=st.text_input(rtext('4_in1'))
if Name:
    Email=st.text_input(rtext('4_in2'))

if Email:
     # draft a title based on input
##### 5. Title for the run
    titledraft = species # start with species name

    if (PI=='Country'): titledraft = titledraft+', '+rtext('5_te1')+' '+str(start_year)+"-"+str(end_year)+" in "+', '.join(countries)+'.'
    if (PI=='Bounding box'): titledraft = titledraft+', '+rtext('5_te2')+' '+str(start_year)+"-"+str(end_year)+" in a user-defined region."
    if (PI=='UP'): titledraft = titledraft+', '+rtext('5_te3')+' '+str(start_year)+"-"+str(end_year)+"."
    if (PI=='geojson'): titledraft = titledraft+', '+rtext('5_te4')+' '+str(start_year)+"-"+str(end_year)+"."

    if (LCtype=='Tree cover (GFW)'): titledraft = titledraft+' '+rtext('5_te5')+' '+str(min(years))+'-'+str(max(years))
    if (LCtype=='Landcover (ESA)'): titledraft = titledraft+' '+rtext('5_te6')+' '+str(min(years))+'-'+str(max(years))

     
    st.markdown(rtext('5_ti'))
    st.markdown(rtext('5_te'))
    title=st.text_input(rtext('5_in'), value=titledraft)

if title:
    if st.button(rtext('5_bu')): 
        ### run the relevant pipeline
        
        ### TC - poly
        if (LCtype=='Tree cover (GFW)' and PI=='geojson'): req=TC_poly()


        ### TC - obs
        if (LCtype=='Tree cover (GFW)' and PI=='UP'): req=TC_obs()

        ### TC - country
        if (LCtype=='Tree cover (GFW)' and PI=='Country'): req=TC_country()


        ### TC - bbox
        if (LCtype=='Tree cover (GFW)' and PI=='Bounding box'): req=TC_bbox()


        ### LC - poly
        if (LCtype=='Landcover (ESA)' and PI=='geojson'): req=LC_poly()


        ### LC - obs
        if (LCtype=='Landcover (ESA)' and PI=='UP'): req=LC_obs()


        ### LC - country
        if (LCtype=='Landcover (ESA)' and PI=='Country'): req=LC_country()
             

        ### LC - bbox
        if (LCtype=='Landcover (ESA)' and PI=='Bounding box'): req=LC_bbox()

        ### get link from request
        link="https://run.gfstool.com/pipeline-form/"+req.text[:-33] + '/' + req.text[-32:]


        ### Step 5 : explore results

            
        st.markdown(rtext('6_ti'))
        st.markdown(rtext('6_te')+link)

        with st.expander(rtext('6_ex1_ti'), expanded=False):
            st.markdown(rtext('6_ex1_te'))      
        with st.expander(rtext('6_ex2_ti'), expanded=False):
            st.markdown(rtext('6_ex2_te'))      
        with st.expander(rtext('6_ex3_ti'), expanded=False):
            st.markdown(rtext('6_ex3_te'))



