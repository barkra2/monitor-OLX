import pandas as pd
from database import aktualizuj_baze, stworz_tabele, konwersja_pandas
import streamlit as st
import os, io, re
import plotly.express as px
import logging

st.set_page_config(page_title="OLX Scraper")
st.title("Scraper cen OLX")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def waliduj_nazwe(nazwa: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_-]+$", nazwa):
        raise ValueError("Nazwa może zawierać tylko litery, cyfry, - i _")
    return nazwa

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

tab1, tab2, tab3 = st.tabs(["Scraper", "Konwersja", "Analiza"])

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
            nazwa_tabeli = waliduj_nazwe(parse_table(nazwa_tabeli))
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
        nazwa_tabeli = waliduj_nazwe(parse_table(nazwa_tabeli))
        konwersja = konwersja_pandas(nazwa_db, nazwa_tabeli)
        if isinstance(konwersja, pd.DataFrame):
            st.dataframe(konwersja, hide_index=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    konwersja.to_excel(writer, index=False, sheet_name=nazwa_tabeli[:31])
                excel_buffer.seek(0)

                st.download_button(
                    label="Pobierz jako Excel",
                    data=excel_buffer,
                    file_name=f"{nazwa_tabeli}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with col3:
                csv_data = konwersja.to_csv(index=False, encoding="utf-8-sig")

                st.download_button(
                    label="Pobierz jako CSV",
                    data=csv_data,
                    file_name=f"{nazwa_tabeli}.csv",
                    mime="text/csv"
                )            
        else:
            st.error(konwersja)

with tab3:
    nazwa_db = file_selector(id="tab3_file")
    nazwa_tabeli = st.text_input("Podaj nazwe tabeli do filtrowania")
    if nazwa_tabeli and nazwa_db:
        nazwa_tabeli = waliduj_nazwe(nazwa_tabeli)
        konwersja = konwersja_pandas(nazwa_db, nazwa_tabeli)
        if isinstance(konwersja, pd.DataFrame):
            st.dataframe(konwersja)
            konwersja["data_dodania"] = pd.to_datetime(
                konwersja["data_dodania"], format="%d-%m-%Y", errors="coerce"
            )
            konwersja["data_dodania_str"] = konwersja["data_dodania"].dt.strftime("%Y-%m-%d")

            kolumny_numeryczne = konwersja.select_dtypes(include="number").columns.tolist()
            kolumny_kategorie = konwersja.select_dtypes(exclude="number").columns.tolist()

            if "id" in kolumny_numeryczne:
                kolumny_numeryczne.remove("id")

            if "data_dodania" in kolumny_kategorie:
                kolumny_kategorie.remove("data_dodania")

            for kol in ["url", "tytul"]:
                if kol in kolumny_kategorie:
                    kolumny_kategorie.remove(kol)

            os_x = st.selectbox("Kategoria (oś X)", kolumny_kategorie)
            wartosc_y = st.selectbox("Wartość do wykresu (oś Y)", kolumny_numeryczne)
            typ_wykresu = st.selectbox("Typ wykresu", ["Słupkowy (średnia)", "Liniowy (średnia)", "Rozrzut (box plot)"])
            ogranicz_do_20 = st.checkbox("Ogranicz wykres do 20 najnowszych/najliczniejszych wyników")

            # --- Filtrowanie do 20 wyników ---
            if ogranicz_do_20 and os_x == "data_dodania_str":
                ostatnie_daty = konwersja["data_dodania"].drop_duplicates().sort_values(ascending=False).head(20)
                df_do_wykresu = konwersja[konwersja["data_dodania"].isin(ostatnie_daty)]
            elif ogranicz_do_20:
                top_kategorie = konwersja[os_x].value_counts().head(20).index
                df_do_wykresu = konwersja[konwersja[os_x].isin(top_kategorie)]
            else:
                df_do_wykresu = konwersja

            if not df_do_wykresu.empty:
                if os_x == "data_dodania_str":
                    kolejnosc = (
                        df_do_wykresu.drop_duplicates(subset=["data_dodania_str"])
                        .sort_values("data_dodania")["data_dodania_str"]
                        .tolist()
                    )
                else:
                    kolejnosc = (
                        df_do_wykresu.groupby(os_x)[wartosc_y]
                        .mean()
                        .sort_values(ascending=False)
                        .index.tolist()
                    )

                if typ_wykresu == "Rozrzut (box plot)":
                    fig = px.box(
                        df_do_wykresu, x=os_x, y=wartosc_y,
                        category_orders={os_x: kolejnosc},
                        title=f"Rozrzut {wartosc_y} wg {os_x}",
                    )
                else:
                    dane_grupowane = df_do_wykresu.groupby(os_x, as_index=False)[wartosc_y].mean()
                    dane_grupowane[os_x] = pd.Categorical(dane_grupowane[os_x], categories=kolejnosc, ordered=True)
                    dane_grupowane = dane_grupowane.sort_values(by=os_x)

                    if typ_wykresu == "Liniowy (średnia)":
                        fig = px.line(
                            dane_grupowane, x=os_x, y=wartosc_y, markers=True,
                            category_orders={os_x: kolejnosc},
                            title=f"Średnia {wartosc_y} wg {os_x}",
                        )
                    else:
                        fig = px.bar(
                            dane_grupowane, x=os_x, y=wartosc_y,
                            category_orders={os_x: kolejnosc},
                            title=f"Średnia {wartosc_y} wg {os_x}",
                        )

                fig.update_layout(xaxis_title=os_x, yaxis_title=wartosc_y)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Brak danych do wyświetlenia.")

