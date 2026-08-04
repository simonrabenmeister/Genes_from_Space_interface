import requests
import pandas as pd
import streamlit as st

from logging_config import (
    get_logger,
    sanitize_headers,
    sanitize_json,
    safe_response_preview,
    truncate_text,
)
from functions import _handle_biab_response, BiaBError
logger = get_logger(__name__)

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





st.session_state.api_link = "https://run.gfstool.com/"


def _call_biab_pipeline(pipeline_name, data):
    """
    Post to a BiaB pipeline endpoint with robust error handling.
    Returns parsed JSON on success. Raises BiaBError on failure.
    """
    url = f"{st.session_state.api_link}pipeline/GenesFromSpace>ToolComponents>Interface>{pipeline_name}.json/run"
    headers = {"Content-Type": "application/json"}

    logger.debug("Calling pipeline: %s", pipeline_name)
    logger.debug("  URL: %s", url)
    logger.debug("  Request data: %s", sanitize_json(data))

    try:
        response = requests.post(url, json=data, headers=headers, timeout=120)
        logger.debug("Request sent, waiting for response...")
    except requests.exceptions.ConnectionError as e:
        logger.exception("Connection error calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — could not reach the Bon-in-a-Box server",
            detail=f"URL: {url}\nError: {str(e)}"
        )
    except requests.exceptions.Timeout as e:
        logger.exception("Timeout calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — request to Bon-in-a-Box timed out",
            detail=f"URL: {url}\nError: {str(e)}"
        )
    except requests.exceptions.RequestException as e:
        logger.exception("Request failed calling %s", url)
        raise BiaBError(
            source="connection",
            message="Connection error — request to Bon-in-a-Box failed",
            detail=str(e)
        )

    return _handle_biab_response(response, pipeline_name)




pipeline = {}
if len(st.session_state.table) > 0:
    # use first row as example mapping
    row = st.session_state.table.iloc[0]
    pipeline = {
        "pipeline@208": int(row["End year"]),
        "pipeline@209": int(row["Start year"]),
        "pipeline@210": row["Species"],
        "pipeline@211": row["Countries list"],
        "pipeline@214": int(row["Size of buffer"]),
        "pipeline@215": int(row["Distance between populations"]),
        "pipeline@217": row["Years of interest"],
        "pipeline@218": row["Landcover classes"],
        "pipeline@224": float(row["Ne:Nc ratio estimate"]),
        "pipeline@225": float(row["Population density"]),
        "pipeline@226": row["Title of the run"],
    }

st.write(pipeline)


if st.button("Call GBIF_LC Pipeline"):
    result = _call_biab_pipeline("GBIF_LC", pipeline)




































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