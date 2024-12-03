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

st.title("Apply Air Normalization")

test_data = st.file_uploader(
    "Upload test data", accept_multiple_files=True, type=["mat"]
)
air_norm_data = st.file_uploader(
    "Upload air norm data", accept_multiple_files=True, type=["mat"]
)


@st.cache_data
def create_heatmap(full_count_map, color_range, colormap="Viridis", invert_color=False):
    if invert_color:
        colormap = colormap + '_r'
    heatmap_fig = create_plotly_heatmaps(
        full_count_map,
        color_range=color_range,
        colormap=colormap,
    )
    return heatmap_fig


if test_data and air_norm_data:
    st.write("Files uploaded successfully")
    test_files = [file for file in test_data]
    air_norm_files = [file for file in air_norm_data]

    with st.expander("Extracted files and folders", expanded=False):
        # st.write(f"{extracted_files = }")
        for file in test_files:
            st.write(file.name)

    def bin_id_to_label(bin_id):
        return BIN_LABELS[bin_id]

    with st.sidebar:
        colormap = st.radio("Colormap", ["Viridis", "Jet", "Plasma", "Magma"])
        invert_color = st.checkbox("Invert color")
        bin_selection = st.multiselect(
            "Select bins",
            [0, 1, 2, 3, 4, 5, 6],
            default=[6],
            format_func=bin_id_to_label,
        )

        color_pctl_0 = st.slider(
            "Lower color range by percentile", 0.0, 5.0, (1.0)
        )
        color_pctl_1 = st.slider(
            "Upper color range by percentile", 95.0, 99.9, (99.5)
        )

    cols = st.columns(3)
    with cols[0]:
        st.header("Test data")
    with cols[1]:
        st.header("Air norm data")
    with cols[2]:
        st.header("Normalized data")

    for i, bin_id in enumerate(bin_selection):
        col1, col2, col3 = st.columns(3)
        with col1:
            _, _, test_count_map = process_mat_files_list(
                bin_id, test_files, file_check=False
            )

            color_min, color_max = np.percentile(
                test_count_map, [color_pctl_0, color_pctl_1]
            )

            color_range = st.slider(
                "Color range", 0.0, color_max * 2, (color_min, color_max)
            )

            heatmap_fig = create_heatmap(
                test_count_map, color_range, colormap, invert_color)
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=True, width=400, height=600)
            st.plotly_chart(heatmap_fig, key=f"heatmap_testdata_{bin_id}")

        with col2:
            _, _, air_norm_count_map = process_mat_files_list(
                bin_id, air_norm_files, file_check=False
            )

            color_min, color_max = np.percentile(
                air_norm_count_map, [color_pctl_0, color_pctl_1]
            )

            color_range = st.slider(
                "Color range", 0.0, color_max * 2, (color_min, color_max)
            )

            heatmap_fig = create_heatmap(
                air_norm_count_map, color_range, colormap, invert_color)
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=True, width=400, height=600)
            st.plotly_chart(heatmap_fig, key=f"heatmap_airnorm_{bin_id}")

        with col3:
            # avoid division by zero
            air_norm_count_map[air_norm_count_map == 0] = 1
            
            normalized_count_map = np.divide(
                test_count_map, air_norm_count_map)

            # replace nans with 0
            normalized_count_map = np.nan_to_num(normalized_count_map)

            color_min, color_max = np.percentile(
                normalized_count_map, [color_pctl_0, color_pctl_1]
            )

            color_range = st.slider(
                "Color range", 0.0, color_max * 2, (color_min, color_max)
            )

            heatmap_fig = create_heatmap(
                normalized_count_map, color_range, colormap, invert_color)
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=True, width=400, height=600)
            st.plotly_chart(heatmap_fig, key=f"heatmap_normalized_{bin_id}")
else:
    st.write("Please upload both files")
