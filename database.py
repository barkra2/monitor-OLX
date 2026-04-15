import sqlite3
from scraper import scrape_listings
import re
import datetime

def parse_price(raw: str) -> float | None:
    if not raw:
        return None
    numbers = re.sub(r"[^\d,.]", "", raw)
    if not numbers:
        return None
    return float(numbers.replace(",", "."))

def parse_date(raw: str):
    DATY = {
        "stycznia": "01",
        "lutego": "02",
        "marca": "03",
        "kwietnia": "04",
        "maja": "05",
        "czerwca": "06",
        "lipca": "07",
        "sierpnia": "08",
        "września": "09",
        "października": "10",
        "listopada": "11",
        "grudnia": "12"
    }
    data = ""
    for i in DATY:
        if raw.find(i) > -1:
            data = raw.replace(i, DATY[i])
            data = data[-10:].replace(" ", "-")
        if raw.find("Dzisiaj") > -1 or raw.find("dzisiaj") > -1:
            data = str(datetime.date.today())
            data = f"{data[8:]}-{data[5:7]}-{data[:4]}"
    return data
            

with sqlite3.connect("baza_danych.db") as conn:

    cursor = conn.cursor()

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS produkty (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tytul TEXT NOT NULL,
                    cena FLOAT,
                    lokalizacja TEXT,
                    data DATE, 
                    url TEXT NOT NULL
                )
                """)
    
    listings = scrape_listings("iphone-14", 2)
    for item in listings:
        title = item["title"]
        price = parse_price(item["price"])
        location_and_date = str(item["location"])
        url = item["url"]
        location = location_and_date[:location_and_date.rfind("-")]
        date = location_and_date[location_and_date.rfind("-")+2:]
        if price is not None and price > 400:
            date = parse_date(date)

            cursor.execute("INSERT INTO produkty (tytul, cena, lokalizacja, data, url) VALUES (?, ?, ?, ?, ?)", (title, price, location, date, url))

    conn.commit()