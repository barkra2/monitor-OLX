import sqlite3
from scraper import scrape_listings
import re

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
                    url TEXT NOT NULL
                )
                """)
    
    listings = scrape_listings("iphone-14", 2)
    for item in listings:
        title = item["title"]
        price = parse_price(item["price"])
        location = item["location"]
        url = item["url"]
        if price is not None and price > 400:
            cursor.execute("INSERT INTO produkty (tytul, cena, lokalizacja, url) VALUES (?, ?, ?, ?)", (title, price, location, url))

    conn.commit()
