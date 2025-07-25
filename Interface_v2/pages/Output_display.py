import streamlit as st
import matplotlib.pyplot as plt 
from streamlit_folium import folium_static
import folium
import rasterio
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
import json
import matplotlib
import pandas as pd
from streamlit_folium import st_folium# A dummy Sentinel 2 COG I had laying around
import plotly.express as px
from typing import Union
from PIL import Image
from fpdf import FPDF
import io
import uuid
import os
import plotly.graph_objects as go

if "output_stage" not in st.session_state:
    st.session_state.output_stage = "upload"
if "out" not in st.session_state:
    st.session_state.out = None
if "name" not in st.session_state:
    st.session_state.name = None
if "relareaplot" not in st.session_state:
    st.session_state.relareaplot = None
if "areaplot" not in st.session_state:
    st.session_state.areaplot = None
if "height" not in st.session_state:
    st.session_state.height=1000
if "geojson_data" not in st.session_state:
    st.session_state.geojson_data = None
if "properties" not in st.session_state:
    st.session_state.properties = None
if "upload" not in st.session_state:
    st.session_state.upload = False
if "rel_habitat_change_table" not in st.session_state:
    st.session_state.rel_habitat_change_table = None
if "area_table" not in st.session_state:
    st.session_state.area_table = None
if "pop_polygons" not in st.session_state:
    st.session_state.pop_polygons = None
if "NE" not in st.session_state:
    st.session_state.NE = None
if "editable_df" not in st.session_state:
    st.session_state.editable_df = None
if "NC" not in st.session_state:
    st.session_state.NC = None
if "GAIN" not in st.session_state:
    st.session_state.GAIN = None
if "LOSS" not in st.session_state:
    st.session_state.LOSS = None
if "polyinfo" not in st.session_state:
    st.session_state.polyinfo = None
if "LC_classnames" not in st.session_state:
    st.session_state.LC_classnames = None
st.set_page_config(page_title="Habitat Change", page_icon="🌍", layout="wide")
st.markdown("# Output Page")
st.sidebar.header("Habitat")

with st.sidebar:
    with st.expander("Settings", expanded=False):
        st.session_state.height = st.slider(
            "Page Height",0, 2000, st.session_state.height
        )
        st.session_state.lan = st.radio("Select Language", ["en"], index=0)


texts = pd.read_csv("texts.csv").set_index("id")

def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")


def open_tif(tif):
    src = rasterio.open(tif)
    array = src.read()
    bounds = src.bounds
    x1, y1, x2, y2 = src.bounds
    bbox = [(bounds.bottom, bounds.left), (bounds.top, bounds.right)]
    return array, bbox



##Load Runs
input = st.file_uploader("Upload a GeoJSON file", type=["geojson"], key="geojson", on_change=lambda: st.session_state.update({"upload": True, "polyinfo": {"buffer": None,"distance": None,"polygons": None}}))

if st.session_state.upload and input is not None:
    # Load the GeoJSON file
    geojson_data = json.load(input)
    st.session_state.pop_polygons = geojson_data["pop_polygons"]
    st.session_state.NE= pd.DataFrame(geojson_data["NE"])
    st.session_state.area_table = pd.DataFrame(geojson_data["area_table"])
    st.session_state.rel_habitat_change_table  = pd.DataFrame(geojson_data["rel_habitat_change_table"])
    st.session_state.editable_df = pd.DataFrame(geojson_data["editable_df"])
    st.session_state.NC = geojson_data["NC"]
    st.session_state.GAIN = geojson_data["GAIN"]
    st.session_state.LOSS = geojson_data["LOSS"]
    st.session_state.properties = pd.DataFrame(geojson_data["properties"])
    st.session_state.upload = False
    st.session_state.LC_classnames =geojson_data["LC_class_names"]
    st.session_state.run_id = geojson_data["run_id"]

if st.session_state.output_stage == "run":
    st.session_state.pop_polygons = st.session_state.polyinfo["polygons"]

rel_habitat_change_table=st.session_state.rel_habitat_change_table
area_table=st.session_state.area_table
NE=st.session_state.NE
editable_df=st.session_state.editable_df
NC=st.session_state.NC
GAIN=st.session_state.GAIN
LOSS=st.session_state.LOSS
properties=st.session_state.properties
class_names=st.session_state.LC_classnames

if input is not None or st.session_state.polyinfo is not None:
    ##create LC maps
    if NC is not None:
        NCarray, NCbbox = open_tif(NC)
        GAINarray, GAINbbox = open_tif(GAIN)
        LOSSarray, LOSSbbox = open_tif(LOSS)

        NCcolor = np.zeros((NCarray.shape[1], NCarray.shape[2], 4), dtype=np.uint8)
        NCcolor[NCarray[0] == 1] = [0, 255, 0, 127]
        NCcolor[NCarray[0] == 0] = [0, 0, 0, 0]

        GAINcolor = np.zeros((GAINarray.shape[1], GAINarray.shape[2], 4), dtype=np.uint8)
        GAINcolor[GAINarray[0] == 1] = [0, 0, 255, 127]
        GAINcolor[GAINarray[0] == 0] = [0, 0, 0, 0]

        LOSScolor = np.zeros((LOSSarray.shape[1], LOSSarray.shape[2], 4), dtype=np.uint8)
        LOSScolor[LOSSarray[0] == 1] = [255, 0, 0, 127]
        LOSScolor[LOSSarray[0] == 0] = [0, 0, 0, 0]

    ##prepare polygon properties
    if st.session_state.pop_polygons is not None:
        for i, poly in enumerate(st.session_state.pop_polygons["features"]):
            if "pop_size" not in poly["properties"]:
                poly["properties"]["pop_size"] = 0
            if "effective_size" not in poly["properties"]:
                poly["properties"]["effective_size"] = 0
            if "Population_Density" not in poly["properties"]:
                poly["properties"]["Population_Density"] = 0
            if "nenc" not in poly["properties"]:
                poly["properties"]["nenc"] = 0
        # Generate a list of colors for the polygons
        colors = [matplotlib.colors.rgb2hex(c) for c in cm.rainbow(np.linspace(0, 1, len(st.session_state.pop_polygons["features"])))]
        # Assign a color to each polygon
        for i, (feature, c) in enumerate(zip(st.session_state.pop_polygons["features"], colors)):
            feature["properties"]["color"] = c

    @st.fragment
    def render_map_fragment():
        # Calculate the middle of NCbbox
        middle_lat = (NCbbox[0][0] + NCbbox[1][0]) / 2
        middle_lon = (NCbbox[0][1] + NCbbox[1][1]) / 2
        m = folium.Map(location=[middle_lat, middle_lon], zoom_start=7, tiles="CartoDB Positron")


        # Use ImageOverlay for raster overlays
        # Save NC, GAIN, and LOSS arrays as images


        run_dir = os.path.join("temp_tiles", st.session_state.run_id)
        os.makedirs(run_dir, exist_ok=True)
        # Save the images in the run-specific directory
        Image.fromarray(NCcolor).save(os.path.join(run_dir, "NC.png"))
        Image.fromarray(GAINcolor).save(os.path.join(run_dir, "GAIN.png"))
        Image.fromarray(LOSScolor).save(os.path.join(run_dir, "LOSS.png"))


        # Add NC raster overlay
        folium.raster_layers.ImageOverlay(
            image=os.path.join(run_dir, "NC.png"),
            name="NC",
            bounds=NCbbox,
            opacity=1.0,
            zindex=1
        ).add_to(m)
        folium.raster_layers.ImageOverlay(
            image=os.path.join(run_dir, "GAIN.png"),
            name="GAIN",
            bounds=GAINbbox,
            opacity=1.0,
            zindex=1
        ).add_to(m)
        folium.raster_layers.ImageOverlay(
            image=os.path.join(run_dir, "LOSS.png"),
            name="LOSS",
            bounds=LOSSbbox,
            opacity=1.0,
            zindex=1
        ).add_to(m)

        # Add the possibility to select layers in Map
        folium.LayerControl().add_to(m)

        fg = folium.FeatureGroup(name="Population Polygons")
        fg.add_child(folium.GeoJson(
            st.session_state.pop_polygons,
            popup=folium.GeoJsonPopup(fields=["name", "Population_Density", "nenc", "pop_size", "effective_size"]),
            style_function=lambda x: {
                'fillOpacity': 0.5,
                'fillColor': x['properties']['color'],
                'color': x['properties']['color']
            }
        ))
        st.session_state.map = m
        # Call to render Folium map in Streamlit
        st.session_state.out = st_folium(m, use_container_width=True, pixelated=True, feature_group_to_add=fg)
    if NC is not None:
        st.write("#### The land cover classes used where:")
        for value in class_names:
            st.markdown(f"<li><strong>{value}</strong></li>", unsafe_allow_html=True)
        st.markdown("</ul>", unsafe_allow_html=True)
        with st.expander("Land Cover classes", expanded=False):
            st.image("images/LC_types.png")
        render_map_fragment()

    ##Input form for population density and Ne:Nc
    if st.session_state.out is not None:
        with st.form(key='polygon', enter_to_submit=False):

            default_dens = st.number_input(
                "Default density", 
                min_value=0.0, 
                step=0.01, 

                key="pop_density"
            )

            default_nenc = st.number_input(
                "Default Ne:Nc", 
                min_value=0.0, 
                max_value=1.0, 
                step=0.01, 

                key="nenc"
            )
            with st.expander(rtext("3_ex_ti"), expanded=False):
                st.markdown(rtext("3_ex_te"))

    #Create dataframe to be manipulated
            properties = pd.DataFrame(
                [
                    {"Name": poly["properties"]["name"]}
                    for poly in st.session_state.pop_polygons["features"]
                ]
            )

            properties["Population_Density"] = [0] * len(properties)
            properties["nenc"] = [0] * len(properties)
            properties["pop_size"] = [0] * len(properties)
            properties["effective_size"] = [0] * len(properties)

            if st.form_submit_button("Submit" ):
                properties = properties.assign(Population_Density=default_dens)
                properties = properties.assign(nenc=default_nenc)
                properties = properties.assign(pop_size=(area_table.iloc[:, 1].values * np.array(default_dens) ))
                properties = properties.assign(effective_size=area_table.iloc[:, -1].values * np.array(default_dens) * np.array(default_nenc))
                st.session_state.properties = properties


    
    if st.session_state.properties is not None:
    ## Create relative change plot
        rel_change = pd.DataFrame(rel_habitat_change_table)

        rel_change = rel_change.melt(id_vars="name", var_name="year", value_name="habitat_area")
        rel_change["year"] = rel_change["year"].str.replace("y", "").astype(int)

        # Plot using Plotly
        rel_change_fig = px.line(
            rel_change,
            x="year",
            y="habitat_area",
            color="name",
            markers=True,
            title="Habitat Area Change Over Time",
            labels={"habitat_area": "Habitat Area", "year": "Year", "name": "Population"},
            color_discrete_map={
                feature["properties"]["name"]: feature["properties"]["color"]
                for feature in st.session_state.pop_polygons["features"]
            }
        )

    ## Create area plot
        area_df = pd.DataFrame(area_table)
        area_df = area_df.melt(id_vars=area_df.columns[0], var_name="year", value_name="area")
        area_df["year"] = area_df["year"].str.replace("y", "").astype(int)

        area_fig = px.line(
            area_df,
            x="year",
            y="area",
            color=area_df.columns[0],
            markers=True,
            title="Area Trends Over Time",
            labels={"area": "Area", "year": "Year", area_df.columns[0]: "Category"},
                    color_discrete_map={
                feature["properties"]["name"]: feature["properties"]["color"]
                for feature in st.session_state.pop_polygons["features"]
            }
        )

    ## Create NE plot
        NE= area_table.copy()
        for i in range(0, len(NE)):
            ratio= st.session_state.properties["pop_size"][i] / area_table.iloc[i, 1]* st.session_state.properties["nenc"][i]
            NE.iloc[i, 1:]=NE.iloc[i, 1:] * ratio

        st.session_state.NE = NE

        if "NE" in st.session_state:

            NE = st.session_state.NE
            ne_df_long = NE.melt(id_vars=NE.columns[0], var_name="year", value_name="NE")
            ne_df_long["year"] = ne_df_long["year"].str.replace("y", "").astype(int)

            # Plot using Plotly
            ne_fig = px.line(
                ne_df_long,
                x="year",
                y="NE",
                color=NE.columns[0],
                markers=True,
                title="Effective Population Size (NE) Over Time",
                labels={"NE": "Effective Population Size (NE)", "year": "Year", NE.columns[0]: "Category"},
                color_discrete_map={
                    feature["properties"]["name"]: feature["properties"]["color"]
                    for feature in st.session_state.pop_polygons["features"]
                }
            )

            # Add a black, striped horizontal line at popsize=500
            ne_fig.add_hline(
                y=500,
                line_dash="dash",
                line_color="black",
                annotation_text="NE>500",
                annotation_position="top left"
            )




        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.markdown("### Population Properties")
            st.markdown("The table bellow shows the properties of the populations. You can edit the Population Density and Population size values. The effective population size is calculated based on these values and the area of the polygons.")

    ##Make the dataframe adaptable
            def adapt_df(new_df: Union[pd.DataFrame, None] = None):
                if new_df is not None:
                    if new_df.equals(st.session_state.properties):
                        return
                    old_df = st.session_state.properties
                    st.session_state.properties = new_df

                df = st.session_state.properties
                for i, row in df.iterrows():
                    calculated_pop_size = row["Population_Density"] * area_table.iloc[int(i), 1]
                    if not np.isclose(old_df.at[i, "Population_Density"], row["Population_Density"], equal_nan=True):
                        df.at[i, "pop_size"] = calculated_pop_size
                            
                for i, row in df.iterrows():
                    calculated_pop_size = row["Population_Density"] * area_table.iloc[int(i), 1]
                    if not np.isclose(row["pop_size"], calculated_pop_size):
                        df.at[i, "Population_Density"] = None
                    else:
                        df.at[i, "pop_size"] = calculated_pop_size

                    df.at[i, "effective_size"] = df.at[i, "pop_size"] * area_table.iloc[int(i), -1] / area_table.iloc[int(i), 1] * row["nenc"]
                st.session_state.properties = df
                st.rerun()

            with st.container(height=330, border=False):#Create container for formatting reasons
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                if st.session_state.properties is not None:
                    editable_df = st.data_editor(
                        st.session_state.properties,
                        key="data",
                        column_config={
                        "effective_size": st.column_config.Column(disabled=True),
                        "Name": st.column_config.Column(disabled=True),
                        "nenc": st.column_config.Column(disabled=True)
                        },
                        hide_index=True,
                    )
                properties= st.session_state.properties
                for i, poly in enumerate(st.session_state.pop_polygons["features"]):
                    poly["properties"]["Population_Density"] = float(properties["Population_Density"][i])
                    poly["properties"]["nenc"] = float(properties["nenc"][i])
                    poly["properties"]["pop_size"] = int(properties["pop_size"][i])
                    poly["properties"]["effective_size"] = int(properties["effective_size"][i])

                adapt_df(editable_df)
                
                # Calculate the ratio of populations with effective size > 500
                ne_greater_500 = (st.session_state.properties["effective_size"] > 500).sum()
                ratio_ne_greater_500 = ne_greater_500 / len(st.session_state.properties)

                # Calculate the ratio of effective population sizes > 50
                ne_greater_50 = (st.session_state.properties["effective_size"] > 50).sum()
                ratio_ne_greater_50 = ne_greater_50 / len(st.session_state.properties)
                st.markdown("### Effective Population Size (NE) Statistics")
                st.markdown(
                    "**NE>500:** {:.2f}".format(ratio_ne_greater_500)
                )
                st.markdown(
                    "**PM:** {:.2f}".format(ratio_ne_greater_50)
                )
    # Display the plot in Streamlit
            ne_plot=st.plotly_chart(ne_fig, use_container_width=True)

        with subcol2:
            relareaplot = st.plotly_chart(rel_change_fig, use_container_width=True, on_select="rerun")
            areaplot = st.plotly_chart(area_fig, use_container_width=True, on_select="rerun")


        geojson_data = json.dumps({
            "pop_polygons": st.session_state.pop_polygons,
            "NE": NE.to_dict(),
            "area_table": area_table.to_dict(),
            "rel_habitat_change_table": rel_habitat_change_table.to_dict(),
            "editable_df": editable_df.to_dict(),
            "NC": NC,
            "GAIN": GAIN,
            "LOSS": LOSS,
            "properties": st.session_state.properties.to_dict(),
            "LC_class_names": st.session_state.LC_classnames,
            "run_id": st.session_state.run_id 


        })
        st.markdown("#### Download The Run as a GeoJSON file")
        st.markdown("You can download your Run as a GeoJSON file. This file contains all the relevant Data to reconstruct the Output. You can upload this file at a later date in this datavisualizer.")
        st.download_button(
        label="Download GeoJSON",
        data=geojson_data,
        file_name="data.geojson",
        mime="text/csv",
        icon=":material/download:",
    )
    if st.button("Generate PDF Report"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Habitat Change Report", ln=True, align="C")
        pdf.ln(10)

        # Add map
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Map Overview", ln=True, align="L")
        pdf.ln(5)
 
        map=st.session_state.map
        img_data=map._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img.save('map_image.png')
        pdf.image("map_image.png", x=10, y=None, w=190)
        pdf.ln(10)

    # Add data table
        pdf.cell(200, 10, txt="Population Properties Table", ln=True, align="L")
        pdf.ln(5)

        # Create a Plotly table
        table_data = st.session_state.properties
        fig_table = go.Figure(data=[go.Table(
            header=dict(values=list(table_data.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[table_data[col] for col in table_data.columns],
                    fill_color='lavender',
                    align='left'))
        ])

        # Save the table as an image
        fig_table.write_image("table_plot.png")

        # Add the table image to the PDF
        pdf.image("table_plot.png", x=10, y=None, w=190)
        pdf.ln(10)

        # Add NE plot
        pdf.ln(5)
        ne_fig.write_image("ne_plot.png")
        pdf.image("ne_plot.png", x=10, y=None, w=190)
        pdf.ln(10)

        # Add relative habitat change plot
        pdf.ln(5)
        rel_change_fig.write_image("rel_change_plot.png")
        pdf.image("rel_change_plot.png", x=10, y=None, w=190)
        pdf.ln(10)

        # Add area trends plot
        pdf.ln(5)
        area_fig.write_image("area_plot.png")
        pdf.image("area_plot.png", x=10, y=None, w=190)
        pdf.ln(10)

        # Add indicators
        pdf.cell(200, 10, txt="Indicators", ln=True, align="L")
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"NE>500: {ratio_ne_greater_500:.2f}", ln=True)
        pdf.cell(0, 10, txt=f"PM: {ratio_ne_greater_50:.2f}", ln=True)

        # Save and download PDF
        pdf_output = io.BytesIO()
        pdf_output.write(pdf.output(dest='S').encode('latin1'))
        st.download_button(
            label="Download PDF Report",
            data=pdf_output.getvalue(),
            file_name="Habitat_Change_Report.pdf",
            mime="application/pdf",
        )
