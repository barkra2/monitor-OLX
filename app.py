import plotly.express as px
from database import aktualizuj_baze, stworz_baze
import streamlit as st

st.set_page_config(page_title="OLX Scraper")
st.title("Scraper cen OLX")

col1, col2, col3 = st.columns(3, gap=None)

col1.button("Wyswietl tabele", type="primary")
col2.button("Uzyj scrapera", type="primary")
col3.button("Stworz baze", type="primary")