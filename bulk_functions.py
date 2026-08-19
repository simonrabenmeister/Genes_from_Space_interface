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
        raise RowError(f"'{col}' is required")
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
    species = _clean(row.get(COL_SPECIES))
    if not species:
        raise RowError(f"'{COL_SPECIES}' is required")

    start_year = _req_num(row, COL_START)
    end_year = _req_num(row, COL_END)
    if start_year > end_year:
        raise RowError(f"'{COL_START}' must not exceed '{COL_END}'")

    # Location: require either a countries list or a 4-value bounding box.
    countries = _cell_list(row, COL_COUNTRIES)
    bbox_parts = _cell_list(row, COL_BBOX)
    if not countries and not bbox_parts:
        raise RowError(f"provide either '{COL_COUNTRIES}' or '{COL_BBOX}'")
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
    title = _clean(row.get(COL_TITLE)) or species

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

    is_tree_cover = _clean(row.get(COL_LC)).upper() == TREE_COVER_FLAG
    if is_tree_cover:
        pipeline = "GBIF_GFW"
    else:
        years = _int_list(row, COL_YEARS)
        lc_classes = _int_list(row, COL_LC)
        if not years:
            raise RowError(f"'{COL_YEARS}' is required for land cover")
        if not lc_classes:
            raise RowError(f"'{COL_LC}' must be integer ESA codes (or 'TC' for tree cover)")
        payload["pipeline@217"] = years
        payload["pipeline@218"] = lc_classes
        pipeline = "GBIF_LC"

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
    fn = GBIF_GFW if spec["pipeline"] == "GBIF_GFW" else GBIF_LC
    return _run_id_of(fn(spec["payload"]))


def run_one_species(spec):
    """Blocking submit + poll; returns the pipeline outputs dict."""
    return wait_for_output(submit_spec(spec))
