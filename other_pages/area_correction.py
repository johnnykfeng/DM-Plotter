import scipy.io
import numpy as np
import streamlit as st
import plotly.express as px

area_correction_mat = r"pixel_area_xmed.mat"

area_correction_data = scipy.io.loadmat(area_correction_mat)

st.write(f"{area_correction_data.keys() = }")
pixel_area = area_correction_data['pixel_area']
st.write("shape: ", pixel_area.shape)
st.write("max", np.max(pixel_area))
normalized_pixel_area = pixel_area / np.max(pixel_area)

with st.sidebar:
    colormap = st.selectbox("Colormap", ["Jet", "Viridis", "Haline", "Bluyl", "Ice", "Cividis", "Plasma", "Magma"])
    invert_color = st.checkbox("Invert color")
    if invert_color:
        colormap = colormap + "_r"
    color_pctl_0 = st.slider("Lower color range by percentile", 0.0, 5.0, (1.0))
    color_pctl_1 = st.slider("Upper color range by percentile", 95.0, 99.9, (99.5))
    
color_min, color_max = np.percentile(
    pixel_area, [color_pctl_0, color_pctl_1]
)
color_range = st.slider(
    "Color range", 0.0, color_max * 2, (color_min, color_max),
    key = "color_range_raw"
)

fig = px.imshow(pixel_area, 
                color_continuous_scale=colormap, 
                range_color=color_range,
                title='Pixel Area Raw')

st.plotly_chart(fig)

color_min, color_max = np.percentile(
    normalized_pixel_area, [color_pctl_0, color_pctl_1]
)
color_range = st.slider(
    "Color range", 0.0, color_max * 2, (color_min, color_max),
    key = "color_range_normalized"
)
# Create a heatmap plot of pixel_area
fig2 = px.imshow(normalized_pixel_area, 
                 color_continuous_scale=colormap, 
                 range_color=color_range,
                 title='Pixel Area Normalized')

st.plotly_chart(fig2)

