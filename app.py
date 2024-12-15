import streamlit as st

pages = [
    st.Page("other_pages/dm_basic.py", title="DM Plotter"),
    st.Page("other_pages/air_norm.py", title="Air Norm"),
    st.Page("other_pages/difference.py", title="Difference"),
    st.Page("other_pages/area_correction.py", title="Area Correction Map"),
]
pg = st.navigation(pages)

pg.run()
