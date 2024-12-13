import streamlit as st

pages = [
    st.Page("pages/dm_basic.py", title="DM Plotter"),
    st.Page("pages/air_norm.py", title="Air Norm"),
    st.Page("pages/difference.py", title="Difference"),
]
pg = st.navigation(pages)

pg.run()
