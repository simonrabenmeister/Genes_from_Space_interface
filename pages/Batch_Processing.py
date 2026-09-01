import io
import json
import os
import uuid
import zipfile
import csv
import pandas as pd
import streamlit as st
from bulk_functions import (
    parse_rows,
    submit_spec, check_status, is_terminal, find_output,
    TERMINAL_FAIL,
    COL_TITLE, COL_SPECIES, COL_COUNTRIES, COL_BBOX, COL_BUFFER, COL_DISTANCE,
    COL_END, COL_START, COL_YEARS, COL_LC, COL_DENSITY, COL_NENC,
)
from functions import BiaBError, _show_biab_error, read_occurrence_file
from logging_config import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Genes from Space — Batch", page_icon="🌍", layout="wide")

# !! Hide a page
st.markdown(
    """
    <style>
    /* Hide the batch page from the sidebar nav; its URL still works */
    [data-testid="stSidebarNav"] a[href$="/Batch_Processing"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Page setup / session bootstrap
# ---------------------------------------------------------------

# Session bootstrap (normally set in Input_form.py, which may not have run yet).
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "biab_dir" not in st.session_state:
    with open("directories.txt", "r") as file:
        directories = file.readlines()
    st.session_state.biab_dir = directories[0].strip()
    st.session_state.api_link = directories[2].strip()

DEFAULT_COLUMNS = [
    COL_TITLE, COL_SPECIES, COL_COUNTRIES, COL_BBOX, COL_BUFFER, COL_DISTANCE,
    COL_END, COL_START, COL_YEARS, COL_LC, COL_DENSITY, COL_NENC,
]

if "table" not in st.session_state:
    st.session_state.table = pd.DataFrame(columns=DEFAULT_COLUMNS)
if "batch_jobs" not in st.session_state:
    st.session_state.batch_jobs = []
if "batch_all_done" not in st.session_state:
    st.session_state.batch_all_done = False

# Initialize language if not already set (prevents AttributeError on direct navigation)
if "lan" not in st.session_state:
    st.session_state.lan = "en"  # Default to English

texts = pd.read_csv("texts.csv").set_index("id")

def rtext(id):
        return texts.loc[id,st.session_state.lan].replace("\\n","\n")

st.markdown(rtext("out_ti"))


with st.sidebar:
    st.session_state.lan = st.radio("Select Language", ["en", "sp"], index=0)
    # Display the session ID for user confirmation when debugging
    st.divider()
    st.caption(
        f"**Debug Session ID:** `{st.session_state.get('session_id', 'Loading...')}`"
        )

# ---------------------------------------------------------------
# Output/file helpers
# ---------------------------------------------------------------

def _disk_path(value):
    """Map a BiaB output value ('/output/…') to an absolute file/dir on disk, else None."""
    if not isinstance(value, str) or not value.startswith("/output/"):
        return None
    path = st.session_state.biab_dir + value
    return path if os.path.exists(path) else None


def _run_output_dir(run_id):
    """On-disk folder for a BiaB runId ('>' segments map to path separators)."""
    return os.path.join(st.session_state.biab_dir, "output", run_id.replace(">", "/"))


def _already_completed(run_id):
    """True if BiaB already has a finished result for this exact runId (cached inputs)."""
    return os.path.exists(os.path.join(_run_output_dir(run_id), "pipelineOutput.json"))


def _resolve_outputs(run_id):
    """Read a completed run's outputs from disk into the pipeline's declared
    '{stepKey}|{handle}' form, so find_output(..., '|ne500') works.

    The API's /outputs only returns a step→folder map; the real values live in
    each step's own output.json.
    """
    pipe = os.path.join(_run_output_dir(run_id), "pipelineOutput.json")
    try:
        with open(pipe) as f:
            step_map = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    resolved = {}
    for step_key, folder in step_map.items():
        step_json = os.path.join(st.session_state.biab_dir, "output", folder, "output.json")
        try:
            with open(step_json) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        for handle, value in data.items():
            resolved[f"{step_key}|{handle}"] = value
    return resolved


def _capture_outputs(job, out):
    """Copy pipeline outputs into a job dict and mark it completed."""
    job["Ne>500"] = find_output(out, "|ne500")
    job["PM"] = find_output(out, "|pm")
    job["Plot"] = find_output(out, "|interactive_plot")
    job["NE table"] = find_output(out, "|ne_table")
    job["Area table"] = find_output(out, "|pop_area")
    job["outputs"] = out
    job["Status"] = "completed"


def _iter_output_files(value):
    """Yield absolute paths for a BiaB output value — a single file (plus its
    '<name>_files' asset folder if present) or every file under a folder."""
    path = _disk_path(value)
    if not path:
        return
    if os.path.isfile(path):
        yield path
        assets = os.path.splitext(path)[0] + "_files"   # e.g. interactive_plot_files/
        if os.path.isdir(assets):
            for root, _, names in os.walk(assets):
                for n in names:
                    yield os.path.join(root, n)
    elif os.path.isdir(path):
        for root, _, names in os.walk(path):
            for n in names:
                yield os.path.join(root, n)


def _build_batch_zip(jobs):
    """Bundle every completed job's output files into a single in-memory zip."""
    out_root = os.path.join(st.session_state.biab_dir, "output")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for j in jobs:
            folder = f"{j['Row']:02d}_{j['Species'].replace(' ', '_')}"
            seen = set()
            for value in (j.get("outputs") or {}).values():
                for fpath in _iter_output_files(value):
                    if fpath in seen:
                        continue
                    seen.add(fpath)
                    rel = os.path.relpath(fpath, out_root)
                    zf.write(fpath, arcname=f"{folder}/{rel}")
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------
# Input table
# ---------------------------------------------------------------

st.markdown("### Batch Processing of Runs")
st.markdown(
    "Upload a CSV (or edit the table) with one row per run. Each row is submitted to the "
    "combined pipeline: **GBIF_LC** for land cover, or **GBIF_GFW** when *Landcover classes* is `TC`."
)

uploaded = st.file_uploader("Upload CSV", type=["csv", "tsv"], key="file_uploader")
if uploaded:
    try:
        st.session_state.table = read_occurrence_file(uploaded)
    except pd.errors.EmptyDataError:
        st.warning("Uploaded CSV is empty or has no columns.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

edited = st.data_editor(st.session_state.table, num_rows="dynamic", key="editable_table")

st.download_button(
    "Download Input File",
    edited.to_csv(index=False).encode("utf-8"),
    file_name="genes_from_space_input.csv",
    mime="text/csv",
    key="dl_input_csv",
)

with st.expander("Column Descriptions"):
    st.markdown("""
    - **Title of the run**: A descriptive title (defaults to the species name if blank).
    - **Species**: The species name as listed in the GBIF database.
    - **Countries list**: Comma-separated list of countries. Provide this *or* a Bounding box.
    - **Bounding box**: `minLon,minLat,maxLon,maxLat` (optional alternative to countries).
    - **Size of buffer**: Buffer radius around observations, in km.
    - **Distance between populations**: Clustering distance between populations, in km.
    - **End year / Start year**: Year range considered by the GBIF query.
    - **Years of interest**: Comma-separated years for habitat calculation (land cover only).
    - **Landcover classes**: Comma-separated ESA class codes, or `TC` for Global Forest Watch tree cover.
    - **Population density**: Population density used in the calculations.
    - **Ne:Nc ratio estimate**: Effective-to-census size ratio (default 0.1 if unknown).
    """)

specs, errors = parse_rows(edited)

if errors:
    st.warning("Some rows have problems and will be skipped:")
    for i, msg in errors:
        st.markdown(f"- Row {i}: {msg}")

st.caption(f"{len(specs)} valid row(s) ready to run.")


# ---------------------------------------------------------------
# Submit / clear
# ---------------------------------------------------------------

col_run, col_clear = st.columns(2)

if col_run.button("Run all", disabled=not specs):
    st.session_state.batch_jobs = []
    st.session_state.batch_all_done = False
    for i, spec in specs:
        job = {
            "Row": i, "Title": spec["title"], "Species": spec["species"],
            "Pipeline": spec["pipeline"], "Status": "running", "Detail": "",
            "runId": None, "Ne>500": None, "PM": None, "Plot": None,
        }
        try:
            job["runId"] = submit_spec(spec)          # non-blocking: returns immediately
        except BiaBError as e:
            job["Status"], job["Detail"] = "failed", e.message
            _show_biab_error(e)
        except Exception as e:
            job["Status"], job["Detail"] = "error", str(e)
            logger.exception("submit failed for row %s", i)
        else:
            # Cache hit: results already on disk — capture immediately.
            if _already_completed(job["runId"]):
                out = _resolve_outputs(job["runId"])
                if find_output(out, "|ne500") is not None:
                    _capture_outputs(job, out)
                    job["Detail"] = "cached — existing result reused"
        st.session_state.batch_jobs.append(job)

if col_clear.button("Clear results", disabled=not st.session_state.batch_jobs):
    st.session_state.batch_jobs = []
    st.session_state.batch_all_done = False
    st.rerun()


# ---------------------------------------------------------------
# Live monitor
# ---------------------------------------------------------------

@st.fragment(run_every=3)
def batch_monitor():
    jobs = st.session_state.batch_jobs
    if not jobs:
        return
    for j in jobs:
        if not j["runId"] or is_terminal(j["Status"]):
            continue
        # Finished runs write pipelineOutput.json; read results straight from disk.
        if _already_completed(j["runId"]):
            out = _resolve_outputs(j["runId"])
            if find_output(out, "|ne500") is not None:
                _capture_outputs(j, out)
                continue
        status = check_status(j["runId"])
        if status in TERMINAL_FAIL:
            j["Status"], j["Detail"] = "failed", f"pipeline status: {status}"
        else:
            j["Status"] = status          # running / missing / etc. — keep polling

    done = sum(1 for j in jobs if is_terminal(j["Status"]))
    st.progress(done / len(jobs), text=f"{done}/{len(jobs)} complete")
    display_cols = ["Row", "Title", "Species", "Pipeline", "Status", "Detail", "Ne>500", "PM"]
    st.dataframe(pd.DataFrame(jobs, columns=display_cols), use_container_width=True)

    # Fire one app-level rerun when everything finishes, so the Downloads section renders.
    if done == len(jobs) and not st.session_state.batch_all_done:
        st.session_state.batch_all_done = True
        st.rerun(scope="app")

batch_monitor()


# ---------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------

completed = [j for j in st.session_state.batch_jobs if j["Status"] == "completed"]
if completed:
    st.markdown("#### Downloads")
    st.download_button(
        "Download all (zip)",
        _build_batch_zip(completed),
        file_name="genes_from_space_batch.zip",
        mime="application/zip",
        key="dl_all_zip",
    )
    for j in completed:
        with st.expander(f"Row {j['Row']} — {j['Title']} — {j['Species']} ({j['Pipeline']})"):
            st.write(f"**Ne>500 indicator:** {j['Ne>500']}")
            st.write(f"**Population maintained (PM):** {j['PM']}")

            st.download_button(
                "Download Full Species/Row (Zip)",
                _build_batch_zip([j]),
                file_name=f"{j['Row']:02d}_{j['Species'].replace(' ', '_')}.zip",
                mime="application/zip",
                key=f"dl_zip_{j['Row']}",
            )

            files = [
                ("Effective size table (NE.tsv)", j.get("NE table"), "NE.tsv", "text/tab-separated-values"),
                ("Habitat area table",            j.get("Area table"), "pop_habitat_area.tsv", "text/tab-separated-values"),
                ("Interactive plot (HTML)",       j.get("Plot"), "interactive_plot.html", "text/html"),
            ]
            for label, value, fname, mime in files:
                path = _disk_path(value)
                if path:
                    with open(path, "rb") as fh:
                        st.download_button(
                            label, fh.read(),
                            file_name=f"{j['Species']}_{fname}",
                            mime=mime,
                            key=f"dl_{j['Row']}_{fname}",
                        )
