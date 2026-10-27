import streamlit as st
import zipfile
import os
import pandas as pd

TARGET_DIR = "/home/ubuntu/BIAB/bon-in-a-box-pipelines/userdata/csv_files"

zip_file = st.file_uploader("Upload a ZIP file", type=["zip"], key="zip_file")

if zip_file is not None:
    os.makedirs(TARGET_DIR, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        for member in zip_ref.infolist():

            name = os.path.basename(member.filename)
            # skip folder entries only
            if member.is_dir() or not name:
                continue

            # write the file directly into TARGET_DIR, ignoring any folder in the zip
            with zip_ref.open(member) as src, open(os.path.join(TARGET_DIR, name), "wb") as dst:
                dst.write(src.read())

    st.success("ZIP file extracted successfully!")



