import streamlit as st
import numpy as np
import plotly.express as px
from utility_functions import (
    BIN_LABELS,
    get_data_info,
    process_mat_files_list,
    create_plotly_heatmaps,
    sort_module_order,
)
from config import MM_ORDER


st.set_page_config(
    page_title="Basic MAT file viewer",
    page_icon=":computer:",
    layout="centered",
)


st.write("### Drag and drop or upload all the MAT files to use this app.")

# File uploader for multiple files
uploaded_files = st.file_uploader(
    "Upload all the MAT files", accept_multiple_files=True, type=["mat"]
)


def bin_id_to_label(bin_id):
    return BIN_LABELS[bin_id]


@st.cache_data
def create_heatmap(full_count_map, color_range, colormap="Viridis", invert_color=False):
    if invert_color:
        colormap = colormap + "_r"
    heatmap_fig = create_plotly_heatmaps(
        full_count_map,
        color_range=color_range,
        colormap=colormap,
    )
    return heatmap_fig


@st.cache_data
def cached_process_mat_files_list(
    bin_id, mat_files, file_check=False, area_correction=True
):
    return process_mat_files_list(bin_id, mat_files, file_check, area_correction)


with st.sidebar:
    area_correction_checkbox = st.checkbox("Apply area correction")
    # colormap = st.radio("Colormap", ["Viridis", "Jet", "Plasma", "Magma"])
    colormap = st.selectbox("Colormap", ["Viridis", "Haline", "Bluyl", "Ice", "Cividis", "Jet", "Plasma", "Magma"])
    invert_color = st.checkbox("Invert color")
    bin_selection = st.multiselect(
        "Select bins",
        [0, 1, 2, 3, 4, 5, 6],
        default=[0, 1, 2, 3, 4, 5, 6],
        format_func=bin_id_to_label,
    )

    color_pctl_0 = st.slider("Lower color range by percentile", 0.0, 5.0, (1.0))
    color_pctl_1 = st.slider("Upper color range by percentile", 95.0, 99.9, (99.5))
    fig_height = st.slider("Figure height", 100, 1500, 600)


if uploaded_files:
    st.write(f"Processing {len(uploaded_files)} uploaded files...")

    st.write(uploaded_files[0].name)
    extracted_files = [file for file in uploaded_files]
    # Reorder the extracted_files list based on MM_ORDER
    extracted_files = sort_module_order(extracted_files)

    with st.expander("Metadata", expanded=False):
        msgs, params_info, params = get_data_info(extracted_files, check_mat=False)
        st.write("**cc_data_shape**")
        st.write(msgs)
        st.write("**params_info**")
        st.write(params_info)

    with st.expander("Extracted files and folders", expanded=False):
        # st.write(f"{extracted_files = }")
        for file in extracted_files:
            st.write(file.name)

    for i, bin_id in enumerate(bin_selection):
        _, _, full_count_map = cached_process_mat_files_list(
            bin_id,
            extracted_files,
            file_check=False,
            area_correction=area_correction_checkbox,
        )

        color_min, color_max = np.percentile(
            full_count_map, [color_pctl_0, color_pctl_1]
        )

        st.header(f"{BIN_LABELS[bin_id]}")
        color_range = st.slider(
            "Color range", 0.0, color_max * 2, (color_min, color_max)
        )

        heatmap_fig = create_heatmap(
            full_count_map, color_range, colormap, invert_color
        )
        heatmap_fig.update_layout(autosize=True, width=400, height=fig_height)
        st.plotly_chart(heatmap_fig, key=f"heatmap_{bin_id}")
