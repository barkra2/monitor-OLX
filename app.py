import plotly.express as px
from database import aktualizuj_baze, stworz_baze
import streamlit as st

st.set_page_config(page_title="OLX Scraper")
st.title("Scraper cen OLX")

tab1, tab2, tab3 = st.tabs(["Scraper", "Analiza", "Stworz baze"])

with tab1:
    query = st.text_input("Podaj rzecz ktora chcesz wyszukac")
    pages = st.number_input("Podaj liczbe stron ktore chcesz przeszukac", min_value=1, max_value=10, step=1)
    cena_min = st.number_input("Podaj cene minimalna (opcjonalnie)", min_value=1, value=None)
    cena_max = st.number_input("Podaj cene maksymalna (opcjonalnie)", value=None)
    nazwa_db = st.text_input("Podaj nazwe pliku db")
    if query and pages and nazwa_db:
        if st.button("Wygeneruj wyniki"):
            query = query.replace(" ", "-")
            if nazwa_db.count(".db"):
                nazwa_db.replace(".db", "")
            if aktualizuj_baze(query, pages, nazwa_db, cena_min, cena_max) is not None:
                st.text("Scrapowanie zakonczylo sie powodzeniem.")
            else:
                st.error("Nastapil blad w scrapowaniu, po wiecej zobacz plik log")
with tab2:
    st.button("Test2")
with tab3:
    nazwa_bazy = st.text_input("Podaj nazwe bazy")
    if nazwa_bazy:
        if st.button("Stworz"):
            if nazwa_bazy.find(".db"):
                nazwa_bazy.replace(".db", "")
            st.text(stworz_baze(nazwa_bazy))
