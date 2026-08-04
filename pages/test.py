import requests
import pandas as pd
import streamlit as st


st.markdown("### Batch Processing of Runs")
st.markdown("This page allows you to automatically generate multiple runs by uploading a CSV file with the required parameters. Each row in the CSV will be treated as a separate run.")
if "editable_table" not in st.session_state:
    st.session_state.table = pd.DataFrame(columns=[
        "Title of the run",
        "Species",
        "Countries list",
        "Size of buffer",
        "Distance between populations",
        "End year",
        "Start year",
        "Years of interest",
        "Landcover classes",
        "Population density",
        "Ne:Nc ratio estimate",

        
    ])

st.file_uploader("Upload CSV", type=["csv"], key="file_uploader")

# Safely load uploaded CSV only if a file is provided and not empty
if st.session_state.get("file_uploader"):
    try:
        st.session_state.table = pd.read_csv(st.session_state.file_uploader, sep=",")
    except pd.errors.EmptyDataError:
        st.warning("Uploaded CSV is empty or has no columns.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

st.data_editor(st.session_state.table, num_rows="dynamic", key="editable_table")

with st.expander("Column Descriptions"):
    st.markdown("""
    - **Title of the run**: A descriptive title for the run.
    - **Species**: The species name as listed in the GBIF database.
    - **Countries list**: A comma-separated list of countries where the species is found.
    - **Size of buffer**: The size of the buffer zone around the species' range.
    - **Distance between populations**: The distance between populations in kilometers.
    - **End year**: The last year to be considered by the GBIF API.
    - **Start year**: The first year to be considered by the GBIF API.
    - **Years of interest**: A comma-separated list for which the population sizes will be calculated.
    - **Landcover classes**: A comma-separated list of landcover classes to be considered. To use the Global forest watch landcover dataset, enter TC.
    - **Population density**: The population density to be used in the calculations.
    - **Ne:Nc ratio estimate**: The estimated ratio of effective population size to census population size. If unknown, use 0.1 as a default value.
    """)






















































# if "obs_edit" not in st.session_state:
#     st.session_state.obs_edit = None


    
# def get_dataset_name(dataset_key):
#     url = f"https://api.gbif.org/v1/dataset/{dataset_key}"
#     response = requests.get(url)
#     return response.json().get("title", "Unknown")

# if st.session_state.obs_edit is not None:
#     df = st.session_state.obs_edit

#     # Only call API for unique keys
#     unique_datasets = df["datasetkey"].unique()
#     unique_publishers = df["publisher"].unique()

#     # Build lookup dicts
#     dataset_lookup = {k: get_dataset_name(k) for k in unique_datasets}


#     # Map back to full dataframe as new columns
#     df["dataset_name"] = df["datasetkey"].map(dataset_lookup)


#     st.session_state.obs_edit = df
#     st.session_state.obs_edit

# url = f"https://api.gbif.org/v1/dataset/89971212-f762-11e1-a439-00145eb45e9a"

# response= requests.get(url).json()
# st.write(response)