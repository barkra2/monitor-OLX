import plotly.express as px
from database import aktualizuj_baze, stworz_tabele
import streamlit as st

st.set_page_config(page_title="OLX Scraper")
st.title("Scraper cen OLX")

def parse_db(db:str):
    if db.count(".db"):
        db.replace(".db", "")
    return db
def parse_table(table:str):
    if table.count(" "):
        table.replace(" ", "-")
    return table

tab1, tab2 = st.tabs(["Scraper", "Analiza"])

with tab1:
    query = st.text_input("Podaj rzecz ktora chcesz wyszukac")
    pages = st.number_input("Podaj liczbe stron ktore chcesz przeszukac", min_value=1, max_value=10, step=1)
    cena_min = st.number_input("Podaj cene minimalna (opcjonalnie)", min_value=1.00, value=None)
    cena_max = st.number_input("Podaj cene maksymalna (opcjonalnie)", value=None)
    nazwa_db = st.text_input("Podaj nazwe pliku db (stworzy nowa jesli nie ma)")
    nazwa_tabeli = st.text_input("Nazwa tabeli (stworzy nowa jesli nie ma lub nadpisze istniejaca)")
    if query and pages and nazwa_db and nazwa_tabeli:
        if st.button("Wygeneruj wyniki"):
            query = query.replace(" ", "-")
            nazwa_db = parse_db(nazwa_db)
            nazwa_tabeli = parse_table(nazwa_tabeli)
            if stworz_tabele(nazwa_db, nazwa_tabeli) is not None:
                st.text("Stworzono tabele")
            if aktualizuj_baze(query, pages, nazwa_db, cena_min, cena_max, nazwa_tabeli) is not None:
                st.text("Scrapowanie zakonczylo sie powodzeniem.")
            else:
                st.error("Nastapil blad w scrapowaniu, po wiecej zobacz plik log")
with tab2:
    nazwa_db = st.text_input("Podaj nazwe bazy danych")
    nazwa_tabeli = st.text_input("Podaj nazwe tabeli")
    if nazwa_db and nazwa_tabeli:
        nazwa_db = parse_db(nazwa_db)
        nazwa_tabeli = parse_table(nazwa_tabeli)
        

# with tab3:
#     nazwa_bazy = st.text_input("Podaj nazwe bazy")
#     if nazwa_bazy:
#         if st.button("Stworz"):
#             if nazwa_bazy.find(".db"):
#                 nazwa_bazy.replace(".db", "")
#             st.text(stworz_baze(nazwa_bazy))
