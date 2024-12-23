

import streamlit as st
from streamlit_map import mapcsv
from streamlit_map import mapgeojson
from streamlit_map import mapbbox
import api_calls
import webbrowser 

import questions

##Page configuration
st.set_page_config(
    page_title="Genes from Space Monitoring Tool",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://teams.issibern.ch/genesfromspace/',
        'Report a bug': "https://teams.issibern.ch/genesfromspace/",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

#session state initialization
#saves the Inputs for Pipeline selection
if "save" not in st.session_state:
    st.session_state.save= {}
    st.session_state.save["poly"]=""
    st.session_state.save["points"]=""
#used to check if the user has changed the selection
if "savecheck" not in st.session_state:
    st.session_state.savecheck= {}
#saves the type of pipeline
if "type" not in st.session_state:
    st.session_state.type= {}
#used to check if the user has clicked on the commit button
if "commit" not in st.session_state:
    st.session_state.commit=False
#saves inputs for pipeline
if "input" not in st.session_state:
    st.session_state.input= {}

types = {
    "LC_bbox": {"LCtype": "Land cover", "poly": "no", "points": "GBIF", "area_type": "BBox"},
    "TC_bbox": {"LCtype": "Forest cover", "poly": "no", "points": "GBIF", "area_type": "BBox"},
    "LC_country": {"LCtype": "Land cover", "poly": "no", "points": "GBIF", "area_type": "Country"},
    "TC_country": {"LCtype": "Forest cover", "poly": "no", "points": "GBIF", "area_type": "Country"},
    "LC_poly": {"LCtype": "Land cover", "poly": "yes", "points": "NA", "area_type": "NA"},
    "TC_poly": {"LCtype": "Forest cover", "poly": "yes", "points": "NA", "area_type": "NA"},
    "LC_obs": {"LCtype": "Land cover", "poly": "no", "points": "pre", "area_type": "NA"},
    "TC_obs": {"LCtype": "Forest cover", "poly": "no", "points": "pre", "area_type": "NA"}
}

urls = {
    "LC_bbox": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_bbox",
    "TC_bbox": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_GBIF_bbox",
    "LC_country": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELand_cover_v_GBIF_countries",
    "TC_country": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_GBIF_countries",
    "LC_poly": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_polygon",
    "TC_poly": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForestcover_v_polygon",
    "LC_obs": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3ELandcover_v_obs_server",
    "TC_obs": "http://130.60.24.27/pipeline-form/GenesFromSpace%3ETool%3EForest_cover_v_obs_server"
}


##Header
st.markdown("# Genes from Space Monitoring Tool")
st.markdown('''
The Genes From Space monitoring tool uses Earth Observations (EO) to track habitat changes over time and infer population trends as indicators of genetic diversity. 
''')
with st.expander("Expand for more information"):
    st.markdown('''Leveraging public EO data, the tool enables users to estimate two genetic diversity indicators adopted by the Convention on Biological Diversity:
- the Ne500 indicator, indicating the fraction of populations with an effective population size (Ne) above 500 units. Populations with Ne below 500 units are at risk of genetic erosion.
- the Populations Maintained indicator (PM), indicating the fraction of populations that are maintained (i.e., that did not extinct) over time.
\nDeveloped within the BON in a box platform, the tool provides an interface that simplifies the process of accessingselecting EO datasets, running analyses, and estimatinginterpreting genetic diversity indicators. Ultimately, this tool offers a more scalable and accessible solution for researchers, conservationists, and policymakers to monitor and protect biodiversity at local, regional, and global levels.
For detailedmore information on methods and assumptions underlying the tool, Infos check out the Genes from Space website.
''')
st.markdown("## Integration within BON in a Box")
st.markdown('''
The tool runs within [Bon in a Box](http://130.60.24.27/pipeline-form), a platform designed to develop and share tools that support biodiversity monitoring. 
            The tool can be launched through the standard  [BON in a Box interface] (http://130.60.24.27/pipeline-form); however, the numerous options and parameters 
            may make this challenging for beginners. To address this, we propose the interactive form below, which guides users 
            through the preparation and execution of a run with the tool.
            ''')


st.markdown('''## Interactive Form
Use the form below to prepare and launch your tool run. As you complete each field, the form will dynamically reveal new options, guiding you step-by-step through the setup process.

''')
with st.expander("Expand for more information", expanded=False):
    st.markdown('''The figure below provides an overview of how the tool works. There a two main  main inputs:
1. Populations Distribution Map: This map represents the geographic distribution of the species' populations, typically derived from field observations of the studied species. The observation can be provided by the user, or retrieved from a public repository (GBIF) using the tool. 
2. Habitat Suitability Maps: These maps depict changes in the species' suitable habitat over time. These maps are generated by the tool using Earth observation-derived data and models. 
\n Using these inputs, the tool assesses how the size of suitable habitat for each population changes over time. This analysis can identify populations that have completely lost their habitat over a given period (estimating the PM indicator). Additionally, by combining suitable habitat size with an estimate of population density, the tool can estimate the size of each population, which is then used to estimate the Ne500 indicator.
The interactive form will ask which data to use for representing the populations distribution, habitat change, and set the parameters to estimate the indicators. 
''')
    st.image("pipeline_description.png")
st.divider() 
###Pipeline Selection
LCtype= st.selectbox(
    'Habitat change Variable:',
    ('Forest cover', 'Land cover'),
    index=None,
    placeholder="Select LC Type...")

with st.expander("Expand for more information", expanded=False):
    st.markdown('''
    The tool currently offers two options for estimating changes in suitable habitat over time:
    1. **Landcover from the European Space Agency**
    \t* Provides global maps showing annual changes across 30 landcover classes. These classes are standardized and describe the features covering the Earth's surface, such as evergreen forests, deciduous forests, grasslands, agricultural areas, urban areas, and water bodies.
    \t* Ideal for analyzing large spatial scales (entire countries), or when focusing on non-forest species (e.g., species in low-vegetation habitats) or species associated with specific forest types (e.g., needle-leaved, evergreen, or deciduous forests).
    \t* Resolution: 300 meters.
    \t* Timeframe: 1992–2021.
    2. **Tree Cover from Global Forest Watch**
    \t* Offers global maps detailing annual tree cover loss.
    \t* Best suited for studying forest species in small geographic regions with homogenous forest types.
    \t* Resolution: 20 meters.
    \t* Timeframe: 2000–2023.
    ''')
st.divider() 

if LCtype:
    #save LCtype
    st.session_state.save["LCtype"]=LCtype

    poly=st.radio(
        "Do you have preprocessed polygons?",
        key="visibility",
        options=["yes", "no"],
        index=None
    )

    with st.expander("Expand for more information", expanded=False):
        st.markdown('''
    Population polygons represent the geographic distribution of the studied populations. These polygons can be provided as vector files in “geojson” format, with an attribute named “pop” encoding a unique identifier for each population (e.g., “pop_1,” “pop_2,” “pop_3,” etc.).
    ''')
    
    if poly=="yes":
        st.session_state.save["poly"]="yes"
        st.session_state.save["points"]="NA"
        st.session_state.save["area_type"]= "NA"

    if poly=="no":
        #correct the save state if the user changes the selection after commiting.  prevents the commit button from appearing prematurely
        if st.session_state.save["poly"]=="yes":
            del st.session_state.save["area_type"]
        st.session_state.save["poly"]="no"

        points=st.radio(
            "Do you have preprocessed polygons?",
            options=["GBIF", "preexisting observations"],
            index=None
        )
        with st.expander("Expand for more information", expanded=False):
            st.markdown('''The tool can generate population polygons by processing geographic coordinates of species observations. These coordinates can either be supplied by the user (Figure below, option 1) or retrieved from a public species observation repository [GBIF](https://www.gbif.org/); option 2). 
        ''')
            st.image("polygons_option1.png")
            st.image("polygons_option2.png")

        if points=="preexisting observations":
                st.session_state.save["points"]="pre"
                st.session_state.save["area_type"]= "NA"

        if points=="GBIF":
            #correct the save state if the user changes the selection after commiting. prevents the commit button from appearing prematurely
            if st.session_state.save["points"]=="pre":
                del st.session_state.save["area_type"]

            st.session_state.save["points"]="GBIF"

            area_type=st.radio(
                "Country or BBox?",
                options=["BBox", "Country"],
                index=None
            )

            with st.expander("Expand for more information", expanded=False):
                st.markdown('''The area of interest is used to retrieve species observation from a public repostiory [(GBIF)](https://www.gbif.org/). The area of interest can be set in two ways:
- Bounding box: the user draws the area of interest on an interactive map. 
- Country list: the user selects one or more countries of interest from a list. 

 Note that the tool will take longer to run on large study areas. If using the Global Forest Watch habitat change data, we recommend setting a study area size below 500’000 Km^2.
''')
            if area_type:
                        st.session_state.save["area_type"]=area_type

#Display Commit button if all inputs are selected
if len(st.session_state.save)==4:
    st.write("Are you happy with your choices? If so click on Submit and you will be directed to the correct pipeline.")
    if st.button("Commit"):
        st.session_state.commit=True
        st.session_state.savecheck=st.session_state.save.copy()
        st.session_state.input=None

    for key, value in types.items():
        st.session_state.type[key] = st.session_state.save == value


#Display Input fields if the user only if the selected inputs are commited  
if st.session_state.savecheck==st.session_state.save:
    for key, value in st.session_state.type.items():
        if value:
#get script from questions.py for the selected pipeline
            script=getattr(questions, key)
            inputs=script()
            if inputs:
                st.write(st.session_state.input)
#Run Bon in a Box with selected inputs via API call script
                if st.button("Run Script"):
                    for key, value in st.session_state.type.items():
                        func = None
                        if value:
                            func = getattr(api_calls, key)

                        if func:
                            link="http://130.60.24.27/pipeline-form/"+func(st.session_state.input).text[:-33] + '/' + func(st.session_state.input).text[-32:]
                            st.write(link)
                            webbrowser.open(link)
                        
