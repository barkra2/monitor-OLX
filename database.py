import sqlite3, re, datetime, logging, pandas as pd
from scraper import scrape_listings
import re
import datetime

logger = logging.getLogger(__name__)


MIESIACE = {
    "stycznia": "01", "lutego": "02", "marca": "03",
    "kwietnia": "04", "maja": "05", "czerwca": "06",
    "lipca": "07", "sierpnia": "08", "września": "09",
    "października": "10", "listopada": "11", "grudnia": "12",
}

def parse_price(raw: str) -> float | None:
    if not raw:
        return None
    numbers = re.sub(r"[^\d,.]", "", raw)
    if not numbers:
        return None
    return float(numbers.replace(",", "."))

def parse_date(raw: str) -> str | None:
    if not raw:
        return None

    raw = raw.strip().lower()

    if "dzisiaj" in raw:
        return datetime.date.today().isoformat()

    if "wczoraj" in raw:
        return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", raw)
    if match:
        dzien, miesiac_slowo, rok = match.groups()
        numer_miesiaca = MIESIACE.get(miesiac_slowo)
        if numer_miesiaca:
            try:
                data = datetime.date(int(rok), int(numer_miesiaca), int(dzien))
                return data.isoformat()
            except ValueError:
                logger.warning(f"Niepoprawna data po sparsowaniu: {raw}")
                return None

    logger.warning(f"Nie udało się sparsować daty: {raw}")
    return None

def stworz_tabele(nazwa_db, nazwa_tabeli):
    with sqlite3.connect(f"data/{nazwa_db}.db") as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS "{nazwa_tabeli}" (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                tytul             TEXT NOT NULL,
                cena              REAL,
                cena_poprzednia   REAL,
                stan              TEXT,
                lokalizacja       TEXT,
                data_dodania      DATE,
                url               TEXT NOT NULL UNIQUE,  -- <-- UNIQUE, URL = identyfikator
                status            TEXT DEFAULT 'nowe'    -- 'nowe' | 'wzrost' | 'spadek' | 'bez_zmian'
            )
        """)
        conn.commit()
    return("Baza zostala stworzona.")

def aktualizuj_baze(keyword: str, strony: int, nazwa_db:str, min_price=None, max_price=None, nazwa_tabeli:str="produkty"):
    """
    Scrapuje ogłoszenia i aktualizuje bazę.
    Zwraca DataFrame z wynikami (ze statusem) do wyświetlenia w Streamlit.
    """
    with sqlite3.connect(f"data/{nazwa_db}.db") as conn:
        listings = scrape_listings(keyword, strony)
        logger.debug(f"Pobrano {len(listings)} rekordów ze scrapera")
        wiersze = []
        for item in listings:
            price = parse_price(item["price"])

            if price is None:
                if min_price is not None or max_price is not None:
                    continue
            else:
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
            loc_raw = str(item["location"])
            location = loc_raw[:loc_raw.rfind("-")].strip()
            date_raw = loc_raw[loc_raw.rfind("-") + 2:].strip()

            wiersze.append({
                "tytul":       item["title"],
                "cena":        price,
                "stan":        item["stan"],
                "lokalizacja": location,
                "data_dodania": parse_date(date_raw),
                "url":         item["url"],
            })

        if not wiersze:
            return pd.DataFrame()

        df_nowe = pd.DataFrame(wiersze)

        df_baza = pd.read_sql(f"""SELECT url, cena FROM "{nazwa_tabeli}" """, conn)

        df = df_nowe.merge(df_baza, on="url", how="left", suffixes=("", "_stara"))

        def _wylicz_status(row):
            if pd.isna(row["cena_stara"]):
                return "nowe"
            if row["cena"] > row["cena_stara"]:
                return "wzrost"
            if row["cena"] < row["cena_stara"]:
                return "spadek"
            return "bez_zmian"

        df["status"] = df.apply(_wylicz_status, axis=1)
        df["cena_poprzednia"] = df["cena_stara"]

        # Zapisz do bazy
        cursor = conn.cursor()
        for _, row in df.iterrows():
            if row["status"] == "nowe":
                cursor.execute(f"""
                    INSERT OR IGNORE INTO "{nazwa_tabeli}"
                        (tytul, cena, cena_poprzednia, stan, lokalizacja, data_dodania, url, status)
                    VALUES (?, ?, NULL, ?, ?, ?, ?, 'nowe')
                """, (row["tytul"], row["cena"], row["stan"], row["lokalizacja"], row["data_dodania"], row["url"]))

            elif row["status"] in ("wzrost", "spadek"):
                cursor.execute(f"""
                    UPDATE "{nazwa_tabeli}"
                    SET cena_poprzednia = cena,
                        cena            = ?,
                        status          = ?,
                        data_dodania    = ?
                    WHERE url = ?
                """, (row["cena"], row["status"], row["data_dodania"], row["url"]))

        conn.commit()
        logger.info(f"Zapisano: {(df['status']=='nowe').sum()} nowych, "
                    f"{(df['status']=='wzrost').sum()} wzrostów, "
                    f"{(df['status']=='spadek').sum()} spadków")

        return df[["tytul", "cena", "cena_poprzednia", "stan", "lokalizacja", "data_dodania", "url", "status"]]

def konwersja_pandas(nazwa_db:str, nazwa_tabeli:str):
    with sqlite3.connect(f"{nazwa_db}") as conn:
        try:
            df = pd.read_sql(f"""SELECT * FROM "{nazwa_tabeli}" """, conn)
            return pd.DataFrame(df)
            # df.to_csv(f"data/{nazwa_tabeli}.csv", index=False, encoding="utf-8-sig")
        except Exception as e:
            return(f"Tabela '{nazwa_tabeli}' nie istnieje lub inny blad: {e}")
    return True

if __name__ == "__main__":
    stworz_tabele("baza_danych", "produkty")
    aktualizuj_baze("iphone-14", 2, "baza_danych")