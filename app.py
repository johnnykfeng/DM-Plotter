import streamlit as st

pages = [
    st.Page("other_pages/dm_basic.py", title="DM Plotter"),
    st.Page("other_pages/air_norm.py", title="Air Norm"),
    st.Page("other_pages/air_norm_movie.py", title="Air Norm Movie"),
    st.Page("other_pages/difference.py", title="Difference"),
    st.Page("other_pages/area_correction.py", title="Area Correction Map"),
    st.Page("other_pages/focal_alignment.py", title="Focal Alignment"),
]
pg = st.navigation(pages)

pg.run()
