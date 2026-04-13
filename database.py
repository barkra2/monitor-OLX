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

with sqlite3.connect("baza_danych.db") as conn:

    cursor = conn.cursor()

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS produkty (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tytul TEXT NOT NULL,
                    cena FLOAT,
                    lokalizacja TEXT,
                    data TEXT, 
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
            if date.find("Dzisiaj") > -1:
                date = f"{date[-5:]} {datetime.date.today()}"
            # if date.find("Odświeżono"):
            #     date = date[date.find("a "):]
            cursor.execute("INSERT INTO produkty (tytul, cena, lokalizacja, data, url) VALUES (?, ?, ?, ?, ?)", (title, price, location, date, url))

    conn.commit()
