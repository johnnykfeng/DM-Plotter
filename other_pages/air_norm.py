import streamlit as st
import numpy as np
from utility_functions import (
    BIN_LABELS,
    process_mat_files_list,
    create_plotly_heatmaps,
    sort_module_order,
    get_number_of_frames
)
from config import MM_ORDER

st.set_page_config(
    page_title="Apply Air Normalization",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("Apply Air Normalization")
if st.button("Clear Uploaded Data", key="clear_data_1"):
    st.rerun()


@st.cache_data
def cached_create_heatmap(
    full_count_map, color_range, colormap="Viridis", invert_color=False
):
    if invert_color:
        colormap = colormap + "_r"
    heatmap_fig = create_plotly_heatmaps(
        full_count_map,
        color_range=color_range,
        colormap=colormap,
    )
    return heatmap_fig


@st.cache_data
def cached_process_mat_files_list(bin_id, mat_files, file_check=False, area_correction=False, frame:int = None):
    return process_mat_files_list(bin_id, mat_files, file_check, area_correction, frame)


def bin_id_to_label(bin_id):
    return BIN_LABELS[bin_id]


with st.sidebar:
    area_correction_checkbox = st.checkbox("Apply area correction")
    colormap = st.selectbox("Colormap", ["Viridis", "Haline", "Bluyl", "Ice", "Cividis", "Jet", "Plasma", "Magma"])
    invert_color = st.checkbox("Invert color")
    bin_selection = st.multiselect(
        "Select bins",
        [0, 1, 2, 3, 4, 5, 6],
        default=[6],
        format_func=bin_id_to_label,
    )
    color_pctl_0 = st.slider("Lower color range by percentile", 0.0, 5.0, (1.0))
    color_pctl_1 = st.slider("Upper color range by percentile", 95.0, 99.9, (99.5))
    # fig_width = st.slider("Figure width", 100, 1000, 400)
    fig_height = st.slider("Figure height", 100, 1000, 600)

    if st.button("Clear Uploaded Data", key="clear_data_2"):
        st.rerun()

cols = st.columns(3)
with cols[0]:
    st.header("Test data")
    test_data = st.file_uploader(
        "Upload test data", accept_multiple_files=True, type=["mat"]
    )

with cols[1]:
    st.header("Air norm data")
    air_norm_data = st.file_uploader(
        "Upload air norm data", accept_multiple_files=True, type=["mat"]
    )


with cols[2]:
    st.header("Normalized data")

with cols[0]:
    if test_data:
        # st.write("Files uploaded successfully")
        with st.spinner("**PROCESSING FILES...**"):
            test_files = [file for file in test_data]
            test_files = sort_module_order(test_files)
        
        
        max_frames = get_number_of_frames(test_files[0])
        frame = st.sidebar.slider("Frame", 0, max_frames-1, 0)
        average_over_frames = st.sidebar.checkbox("Average over frames", value=False)
        if average_over_frames:
            frame = None

        with st.expander("Extracted files and folders", expanded=False):
            for file in test_files:
                st.write(file.name)

        for i, bin_id in enumerate(bin_selection):
            _, _, test_count_map = cached_process_mat_files_list(
                bin_id, test_files, file_check=False, area_correction=area_correction_checkbox, frame=frame
            )

            color_min, color_max = np.percentile(
                test_count_map, [color_pctl_0, color_pctl_1]
            )

            color_range = st.slider(
                "Color range",
                0.0,
                color_max * 2,
                (color_min, color_max),
                key=f"testdata_color_range_{bin_id}",
            )

            heatmap_fig = cached_create_heatmap(
                test_count_map, color_range, colormap, invert_color
            )
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=False, width=400, height=fig_height)
            st.plotly_chart(heatmap_fig, key=f"heatmap_testdata_{bin_id}")

    else:
        st.warning("Upload test data")

with cols[1]:
    if air_norm_data:
        with st.spinner("**PROCESSING FILES...**"):
            air_norm_files = [file for file in air_norm_data]
            air_norm_files = sort_module_order(air_norm_files)

        with st.expander("Extracted files and folders", expanded=False):
            for file in air_norm_files:
                st.write(file.name)

        for i, bin_id in enumerate(bin_selection):
            _, _, air_norm_count_map = cached_process_mat_files_list(
                bin_id, air_norm_files, file_check=False, area_correction=area_correction_checkbox
            )

            color_min, color_max = np.percentile(
                air_norm_count_map, [color_pctl_0, color_pctl_1]
            )

            color_range = st.slider(
                "Color range",
                0.0,
                color_max * 2,
                (color_min, color_max),
                key=f"airnorm_color_range_{bin_id}",
            )

            heatmap_fig = cached_create_heatmap(
                air_norm_count_map, color_range, colormap, invert_color
            )
            heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
            heatmap_fig.update_layout(autosize=False, width=400, height=fig_height)
            st.plotly_chart(heatmap_fig, key=f"heatmap_airnorm_{bin_id}")
    else:
        st.warning("Upload air norm data")

with cols[2]:
    if test_data and air_norm_data:
        st.write("Dividing test data by air norm data")
        for _ in range(5):
            st.divider()
        with st.spinner("**PROCESSING FILES...**"):
            for i, bin_id in enumerate(bin_selection):
                _, _, test_count_map = cached_process_mat_files_list(
                    bin_id, test_files, file_check=False, area_correction=area_correction_checkbox, frame=frame
                )
                _, _, air_norm_count_map = cached_process_mat_files_list(
                    bin_id, air_norm_files, file_check=False, area_correction=area_correction_checkbox
                )

                # avoid division by zero
                air_norm_count_map[air_norm_count_map == 0] = 1

                normalized_count_map = np.divide(test_count_map, air_norm_count_map)

                # replace nans with 0
                normalized_count_map = np.nan_to_num(normalized_count_map)

                color_min, color_max = np.percentile(
                    normalized_count_map, [color_pctl_0, color_pctl_1]
                )

                color_range = st.slider(
                    "Color range",
                    0.0,
                    color_max * 2,
                    (color_min, color_max),
                    key=f"normalized_color_range_{bin_id}",
                )

                heatmap_fig = cached_create_heatmap(
                    normalized_count_map, color_range, colormap, invert_color
                )
                heatmap_fig.update_layout(title=f"{BIN_LABELS[bin_id]}")
                heatmap_fig.update_layout(autosize=False, width=400, height=fig_height)
                st.plotly_chart(heatmap_fig, key=f"heatmap_normalized_{bin_id}")
    else:
        st.warning("Upload both test data and air norm data")
