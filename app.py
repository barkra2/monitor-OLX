import pandas as pd
from database import aktualizuj_baze, stworz_tabele, konwersja_pandas
from raport import generuj_xlsx
import streamlit as st
import os

st.set_page_config(page_title="OLX Scraper")
st.title("Scraper cen OLX")

def parse_db(db: str) -> str:
    return db.replace(".db", "").strip()

def parse_table(table: str) -> str:
    return table.replace(" ", "-").strip()

def file_selector(id, folder_path='data'):
    filenames = os.listdir(folder_path)
    filenames = [i for i in filenames if i.endswith('.db')]
    # for i in filenames[:]:
    #     if i[-3:] != '.db':
    #         filenames.remove(i)
    selected_filename = st.selectbox('Wybierz plik', filenames, key=id)
    return os.path.join(folder_path, selected_filename)

tab1, tab2, tab3 = st.tabs(["Scraper", "Analiza", "Filtruj"])

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
                st.text("Stworzono tabele...")
            wynik = aktualizuj_baze(query, pages, nazwa_db, cena_min, cena_max, nazwa_tabeli)
            if wynik is not None and not wynik.empty:
                st.success(f"Zapisano {len(wynik)} rekordów.")
                st.dataframe(wynik)
            else:
                st.warning("Brak nowych danych do zapisania (sprawdź filtry cenowe lub wyniki scrapera).")
with tab2:
    nazwa_db = file_selector(id="tab2_file")
    nazwa_tabeli = st.text_input("Podaj nazwe tabeli")
    if nazwa_db and nazwa_tabeli:
        nazwa_tabeli = parse_table(nazwa_tabeli)
        konwersja = konwersja_pandas(nazwa_db, nazwa_tabeli)
        if konwersja is True:
            csv = pd.read_csv(f"data/{nazwa_tabeli}.csv")
            st.dataframe(csv, hide_index=True)
            # st.download_button("Pobierz plik excel")
            # if st.button("Generuj plik xlsx", key="button2"):
            #     csv = pd.read_csv(f"data/{nazwa_tabeli}.csv", encoding="utf-8")
                
            #     csv.to_excel(f'data/{nazwa_tabeli}.xlsx')
        else:
            st.error(konwersja)
with tab3:
    nazwa_tabeli = st.text_input("Podaj nazwe tabeli do filtrowania (upewnij sie ze w folderze data jest obecny plik .csv)")
    if nazwa_tabeli:
        plik = pd.read_csv(f'data/{nazwa_tabeli}.csv')
        kolumny = plik.columns.tolist()
        wybor = st.selectbox("Wybierz kolumne", kolumny, key="filtr_kolumny")
        if wybor:
            if pd.api.types.is_numeric_dtype(plik[f'{wybor}']):
                min = st.number_input("Podaj minimalna liczbe", value=0, key="min")
                max = st.number_input("Podaj maksymalna liczbe", value=100, key="max")
                # if min and max:


        

# with tab3:
#     nazwa_bazy = st.text_input("Podaj nazwe bazy")
#     if nazwa_bazy:
#         if st.button("Stworz"):
#             if nazwa_bazy.find(".db"):
#                 nazwa_bazy.replace(".db", "")
#             st.text(stworz_baze(nazwa_bazy))
