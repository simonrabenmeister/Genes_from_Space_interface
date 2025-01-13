import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium.plugins as plugins
import geojson as gj
from folium.plugins import Draw


###Upload and display csv files
def mapcsv():

    obs=pd.DataFrame()
##Upload the observations file: Function given by streamlit
    obs_file = st.file_uploader("Choose a file")
    if obs_file is not None:
        # To read file as bytes:
        bytes_data = obs_file.getvalue()
        # accepts TSV files:
        obs = pd.read_csv(obs_file, sep='\t')
        #st.write(obs)
##Initialize the session state:
    #obs is the uploaded file
        if "obs" not in st.session_state:
            st.session_state.obs= obs
    #obs_edit is the file that is edited
        if "obs_edit" not in st.session_state:
            st.session_state.obs_edit= obs
    #out is the displayed map
        if "out" not in st.session_state:
            st.session_state.out={}
    #index is the index of the point that is clicked
        if "index" not in st.session_state:
            st.session_state.index=None
        
    ##Get min max coordinates of points to set the center of the map
        def get_point_range(geom):
            coords = np.array([geom["decimal_latitude"].values, geom["decimal_longitude"].values]).T
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
    ##Get center of Points for Map display       
        rangepoints=get_point_range(obs)
        #st.write (rangepoints)
        y=rangepoints[2]-(rangepoints[2]-rangepoints[0])/2
        x=rangepoints[3]-(rangepoints[3]-rangepoints[1])/2
        #st.write (x,y)
    #Initialize the center of the map,  will be automaticially changed when the map is interacted with
        if "center" not in st.session_state:
            st.session_state["center"] = [ y, x]  # Default center for the map

        if not obs.equals(st.session_state.obs): #reset Center and Zoom if new file is uploaded
            st.session_state.obs=obs
            st.session_state.obs_edit=obs
            st.session_state["center"] = [y, x]
            st.session_state["zoom"] = 6

    #Initialize the zoom level of the map, will be automaticially changed when the map is interacted with
        if "zoom" not in st.session_state:
            st.session_state["zoom"] = 6  # Default zoom level

    #Set the columns for the latitude and longitude
        lat_col = "decimal_latitude"
        lon_col = "decimal_longitude"
        obs_edit=st.session_state.obs_edit

    #Create the map
        fg = folium.FeatureGroup(name="Markers")
        m = folium.Map(
            location=st.session_state["center"], 
            zoom_start=st.session_state["zoom"]
        )
        #add the observations to the map
        for i, row in obs_edit.iterrows():
            fg.add_child(folium.Marker(
                location=[row[lat_col], row[lon_col]],
                tooltip="Click to select",
                icon=plugins.BeautifyIcon(icon="circle")
            ))
        #display the map
        st.session_state.out = st_folium(
            m,
            center=st.session_state["center"],
            zoom=st.session_state["zoom"],
            key="out",
            feature_group_to_add=fg,
            height=400,
            width=700,
        )

        #Get the index of the clicked point
        if st.session_state.out["last_object_clicked"] is not None:
            st.session_state.index=obs_edit.index[(obs_edit[lat_col] == st.session_state.out["last_object_clicked"]["lat"]) & 
            (obs_edit[lon_col] == st.session_state.out["last_object_clicked"]["lng"])]
        
            def remove_point(index):
                st.session_state.obs_edit=obs_edit.drop(index)

            #Remove the point if the remove button is clicked
            st.button("remove_point", on_click=remove_point, args=(st.session_state.index,)) 

        csv=st.session_state.obs_edit.loc[:, [lat_col, lon_col]]

        #create csv file from the edited observations
        def convert_df(df):
            return df.to_csv(index=False,sep='\t').encode('utf-8')

        #create download button for the csv file
        # st.download_button(
        # "Download observations",
        # convert_df(csv),
        # "observations_GFS_tool.csv",
        # "text/csv",
        # key='download-csv'
        # )
        return str([tuple(csv.columns)] + [tuple(x) for x in csv.values])
    



###Upload and display polygon files
def mapgeojson():
##Upload the polygon file
    poly_file = st.file_uploader("Choose a file")

    if poly_file is not None:    
        if "poly" not in st.session_state:
            st.session_state.poly=poly_file
        # read geojson:
        poly_file = gj.load(poly_file)

        #Get the center of the Polygon for Map display
        def get_bounding_box(geom):
            coords = np.array(list(gj.utils.coords(geom)))
            return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
        bbox=get_bounding_box(poly_file)
        #st.write (bbox)
        y=bbox[2]-(bbox[2]-bbox[0])/2
        x=bbox[3]-(bbox[3]-bbox[1])/2
        #st.write (x,y)

        #set Map center to the center of the polygon
        if "center" not in st.session_state:
            st.session_state["center"] = [x,y]  # Default center for the map
        #set Map zoom level
        if "zoom" not in st.session_state:
            st.session_state["zoom"] = 6 # Default zoom level

        if poly_file != st.session_state.poly: #reset if new file is uploaded
            st.session_state.poly=poly_file
            st.session_state["center"] = [x,y]
            st.session_state["zoom"] = 6

##Create the map
        m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
        fg = folium.FeatureGroup(name="Markers")
        fg.add_child(folium.GeoJson(poly_file))
        

##Display the map
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


### BBox selector
def mapbbox():
    #create the map
    m = folium.Map(location=[0,0], zoom_start=2)
    draw = Draw(export=True)
    draw.add_to(m)


    def get_bounding_box(geom):
        coords = np.array(list(gj.utils.coords(geom)))
        
        return [coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max()]
    #display the map
    output = st_folium(m, width=700, height=500)
    #get the bounding box of the last clicked polygon
    if output["last_active_drawing"] is not None:
        geometry = output["last_active_drawing"]["geometry"]
        return get_bounding_box(geometry)
