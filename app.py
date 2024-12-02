import streamlit as st
import zipfile
import os
import tempfile
import numpy as np
import scipy.io
import plotly.express as px
from utility_functions import (
    BIN_LABELS,
    get_data_info,
    process_mat_files_list,
    create_plotly_heatmaps,
)

# File uploader for multiple files
uploaded_files = st.file_uploader(
    "Upload all the MAT files", accept_multiple_files=True, type=["mat"]
)


@st.cache_data
def create_heatmap(full_count_map, color_range):
    heatmap_fig = create_plotly_heatmaps(
        full_count_map,
        color_range=color_range,
    )
    return heatmap_fig


if uploaded_files:
    st.write(f"Processing {len(uploaded_files)} uploaded files...")

    st.write(uploaded_files[0].name)
    extracted_files = [file for file in uploaded_files]
    file_type = type(extracted_files[0])
    # st.write(file_type)
    # print(file_type)
    with st.expander("Metadata", expanded=False):
        msgs, params = get_data_info(extracted_files, check_mat=False)
        for msg in msgs:
            st.write(msg)
        for p in params:
            st.write(p)

    with st.expander("Extracted files and folders", expanded=False):
        # st.write(f"{extracted_files = }")
        for file in extracted_files:
            st.write(file.name)

    for i, bin_id in enumerate(range(7)):
        _, _, full_count_map = process_mat_files_list(
            bin_id, extracted_files, file_check=False
        )

        color_min, color_max = np.percentile(full_count_map, [1, 99.5])

        with st.expander(f"{BIN_LABELS[bin_id]}", expanded=True):
            color_range = st.slider(
                "Color range", 0.0, color_max * 2, (color_min, color_max)
            )

            heatmap_fig = create_heatmap(full_count_map, color_range)
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=False, width=400, height=600)
            st.plotly_chart(heatmap_fig, key=f"heatmap_{i}")
