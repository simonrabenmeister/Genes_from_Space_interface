"""Helpers for batch (multi-species) runs against the combined GBIF_LC / GBIF_GFW pipelines."""
import time
import requests
import streamlit as st

from functions import BiaBError, _call_biab_pipeline
from logging_config import get_logger

logger = get_logger(__name__)

# ============================================================
# Non-blocking polling primitives
# ============================================================

# Job states BiaB reports; anything else is treated as still in progress.
TERMINAL_OK = {"completed"}
TERMINAL_FAIL = {"failed", "error", "cancelled"}


def _api(path):
    return f"{st.session_state.api_link}{path}"


def check_status(run_id):
    """Single non-blocking status poll; returns a status string, never raises."""
    try:
        history = requests.get(_api("api/history"), timeout=30).json()
    except requests.exceptions.RequestException as e:
        logger.warning("check_status: could not reach BiaB for %s: %s", run_id, e)
        return "unreachable"
    except Exception as e:
        logger.warning("check_status: invalid history for %s: %s", run_id, e)
        return "unknown"

    match = next((entry for entry in history if entry.get("runId") == run_id), None)
    if match is None:
        return "missing"
    return match.get("status", "unknown")


def is_terminal(status):
    return status in TERMINAL_OK or status in TERMINAL_FAIL


def fetch_outputs(run_id):
    """Fetch outputs for a completed job. Raises BiaBError on failure."""
    try:
        return requests.get(_api(f"api/{run_id}/outputs"), timeout=60).json()
    except requests.exceptions.RequestException as e:
        logger.exception("fetch_outputs: connection error for %s", run_id)
        raise BiaBError(
            source="connection",
            message="Connection error — could not retrieve pipeline outputs",
            detail=str(e),
        )
    except Exception as e:
        logger.exception("fetch_outputs: invalid outputs for %s", run_id)
        raise BiaBError(
            source="server",
            message="Server error (Bon-in-a-Box) — pipeline outputs returned invalid data",
            detail=str(e),
        )


def wait_for_output(run_id, poll_delay=2):
    """Blocking equivalent of the old get_output, composed from the primitives."""
    status = check_status(run_id)
    while not is_terminal(status):
        time.sleep(poll_delay)
        status = check_status(run_id)
    if status in TERMINAL_OK:
        return fetch_outputs(run_id)
    raise BiaBError(
        source="pipeline",
        message=f"Pipeline error (Bon-in-a-Box) — job ended with status: {status}",
        detail=f"runId: {run_id}",
    )


def find_output(outputs, suffix):
    """Return the first output whose key ends with the given handle (e.g. '|ne500')."""
    if not isinstance(outputs, dict):
        return None
    return next((v for k, v in outputs.items() if k.endswith(suffix)), None)


# ============================================================
# Combined end-to-end pipelines
# ============================================================

def GBIF_LC(data):
    return _call_biab_pipeline("GBIF_LC", data)


def GBIF_GFW(data):
    return _call_biab_pipeline("GBIF_GFW", data)

def CSV_LC(data):
    return _call_biab_pipeline("CSV_LC", data)

def CSV_GFW(data):
    return _call_biab_pipeline("CSV_GFW", data)

def GBIF_CSV_LC(data):
    return _call_biab_pipeline("GBIF_CSV_LC", data)

def GBIF_CSV_GFW(data):
    return _call_biab_pipeline("GBIF_CSV_GFW", data)    


# ============================================================
# CSV row parsing → @208…@226 payloads
# ============================================================

DELIM = ","  # in-cell list separator; multi-value cells must be quoted in the CSV
TREE_COVER_FLAG = "TC"

COL_TITLE = "Title of the run"
COL_SPECIES = "Species"
COL_COUNTRIES = "Countries list"
COL_BBOX = "Bounding box"
COL_BUFFER = "Size of buffer"
COL_DISTANCE = "Distance between populations"
COL_END = "End year"
COL_START = "Start year"
COL_YEARS = "Years of interest"
COL_LC = "Landcover classes"
COL_DENSITY = "Population density"
COL_NENC = "Ne:Nc ratio estimate"
COL_CSV_PATH = "CSV file path"


class RowError(Exception):
    """Raised when a CSV row fails validation; message is user-facing."""


def _clean(value):
    if value is None:
        return ""
    if isinstance(value, float) and value != value:  # NaN is never equal to itself
        return ""
    return str(value).strip()


def _req_num(row, col):
    raw = _clean(row.get(col))
    if raw == "":
        raise RowError(f"'{col}' is required unless '{COL_CSV_PATH}' is set")
    try:
        return float(raw)
    except ValueError:
        raise RowError(f"'{col}' must be a number, got '{raw}'")

def _opt_num(row, col):
    """Optional number: returns None if empty, raises RowError if present but invalid."""
    raw = _clean(row.get(col))
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        raise RowError(f"'{col}' must be a number, got '{raw}'")



def _cell_list(row, col):
    raw = _clean(row.get(col))
    return [p.strip() for p in raw.split(DELIM) if p.strip()] if raw else []


def _int_list(row, col):
    out = []
    for part in _cell_list(row, col):
        try:
            out.append(int(float(part)))
        except ValueError:
            raise RowError(f"'{col}' must be integers, got '{part}'")
    return out


def _float_list(row, col):
    out = []
    for part in _cell_list(row, col):
        try:
            out.append(float(part))
        except ValueError:
            raise RowError(f"'{col}' must be numbers, got '{part}'")
    if not out:
        raise RowError(f"'{col}' is required")
    return out


def parse_row(row):
    """Turn one CSV row (dict) into {'pipeline', 'payload', 'title', 'species'}."""
    csv_path = _clean(row.get(COL_CSV_PATH))
    has_csv = bool(csv_path)

    # Species, years, and location are only mandatory when no CSV file is given.
    species = _clean(row.get(COL_SPECIES))
    if not species and not has_csv:
        raise RowError(f"'{COL_SPECIES}' is required (unless '{COL_CSV_PATH}' is set)")

    if has_csv:
        start_year = _opt_num(row, COL_START)
        end_year = _opt_num(row, COL_END)
    else:
        start_year = _req_num(row, COL_START)
        end_year = _req_num(row, COL_END)
    if start_year is not None and end_year is not None and start_year > end_year:
        raise RowError(f"'{COL_START}' must not exceed '{COL_END}'")

    # Location: countries list or a 4-value bounding box (optional with a CSV file).
    countries = _cell_list(row, COL_COUNTRIES)
    bbox_parts = _cell_list(row, COL_BBOX)
    if not countries and not bbox_parts and not has_csv:
        raise RowError(
            f"provide either '{COL_COUNTRIES}' or '{COL_BBOX}' (unless '{COL_CSV_PATH}' is set)"
        )
    if has_csv and not countries:
        raise RowError(f"'{COL_COUNTRIES}' is required when '{COL_CSV_PATH}' is set")
    bbox = []
    if bbox_parts:
        if len(bbox_parts) != 4:
            raise RowError(f"'{COL_BBOX}' needs 4 values: minLon,minLat,maxLon,maxLat")
        try:
            bbox = [float(x) for x in bbox_parts]
        except ValueError:
            raise RowError(f"'{COL_BBOX}' values must be numbers")

    buffer = _req_num(row, COL_BUFFER)
    distance = _req_num(row, COL_DISTANCE)
    if buffer <= 0 or distance <= 0:
        raise RowError(f"'{COL_BUFFER}' and '{COL_DISTANCE}' must be positive")

    ne_nc = _float_list(row, COL_NENC)
    density = _float_list(row, COL_DENSITY)
    title = _clean(row.get(COL_TITLE)) or species or os.path.basename(csv_path)

    if not has_csv:
        payload = {
            "pipeline@210": species,
            "pipeline@208": [end_year],
            "pipeline@209": [start_year],
            "pipeline@211": countries,
            "pipeline@212": bbox,
            "pipeline@214": buffer,
            "pipeline@215": distance,
            "pipeline@224": ne_nc,
            "pipeline@225": density,
            "pipeline@226": title,
        }
        prefix = "GBIF"


    elif has_csv:
        payload = {

            "pipeline@214": buffer,
            "pipeline@215": distance,
            "pipeline@224": ne_nc,
            "pipeline@225": density,
            "pipeline@226": title,
            "pipeline@231": csv_path,
            "pipeline@211": countries,
        }
        prefix = "CSV" 
        if species or bbox_parts:
            if species and end_year and start_year:
                payload["pipeline@210"] = species
                payload["pipeline@208"] = [end_year]
                payload["pipeline@209"] = [start_year]
                payload["pipeline@211"] = countries
                payload["pipeline@212"] = bbox
                prefix = "GBIF_CSV" 
    if _clean(row.get(COL_LC)).upper() == TREE_COVER_FLAG:
        pipeline = f"{prefix}_GFW"
        payload["pipeline@232"] = years
    else:
        years = _int_list(row, COL_YEARS)
        lc_classes = _int_list(row, COL_LC)
        if not years:
            raise RowError(f"'{COL_YEARS}' is required for land cover")
        if not lc_classes:
            raise RowError(f"'{COL_LC}' must be integer ESA codes (or 'TC' for tree cover)")
        payload["pipeline@217"] = years
        payload["pipeline@218"] = lc_classes
        pipeline = f"{prefix}_LC"

    return {"pipeline": pipeline, "payload": payload, "title": title, "species": species}


def parse_rows(df):
    """Parse a DataFrame of rows; returns (specs, errors) as index-keyed lists."""
    specs, errors = [], []
    for i, row in df.iterrows():
        try:
            specs.append((i, parse_row(row.to_dict())))
        except RowError as e:
            errors.append((i, str(e)))
    return specs, errors


# ============================================================
# Orchestration
# ============================================================

def _run_id_of(response):
    if isinstance(response, dict) and "runId" in response:
        return response["runId"]
    if isinstance(response, str):
        return response
    raise BiaBError(
        source="server",
        message="Server error (Bon-in-a-Box) — unexpected pipeline response",
        detail=str(response),
    )


def submit_spec(spec):
    """POST a parsed spec to its pipeline; returns the runId (non-blocking)."""
    if spec["pipeline"]=="CSV_LC":
        fn = CSV_LC
    elif spec["pipeline"]=="CSV_GFW":
        fn = CSV_GFW
    elif spec["pipeline"]=="GBIF_CSV_LC":
        fn = GBIF_CSV_LC
    elif spec["pipeline"]=="GBIF_CSV_GFW":
        fn = GBIF_CSV_GFW
    elif spec["pipeline"]=="GBIF_LC":
        fn = GBIF_LC
    elif spec["pipeline"]=="GBIF_GFW":
        fn = GBIF_GFW
    return _run_id_of(fn(spec["payload"]))


def run_one_species(spec):
    """Blocking submit + poll; returns the pipeline outputs dict."""
    return wait_for_output(submit_spec(spec))
