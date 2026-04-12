from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import time, random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0" ,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_page(url: str):
    session = requests.Session(impersonate="firefox")
    for attempt in range(3):
        try:
            response = session.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return bs(response.text, "html.parser")
        except requests.exceptions.Timeout:
            print(f"Timeout, proba {attempt+1}/3...")
            time.sleep(5)
    return None

def scrape_listings(query: str, pages: int = 3) -> list[dict]:
    results = []

    for page in range(1, pages + 1):
        url = f"https://www.olx.pl/oferty/q-{query}/?page={page}"
        soup = get_page(url)
        if soup:
            cards = soup.select("[data-cy='l-card']")
            
            for card in cards:
                title_el = card.select_one("[data-cy='ad-card-title'] > a > h4")
                price_el = card.select_one("[data-testid='ad-price']")
                link_el = card.select_one("a[href]")
                location_el = card.select_one("[data-testid='location-date']")

                results.append({
                    "title": title_el.get_text(strip=True) if title_el else None,
                    "price": price_el.get_text(strip=True) if price_el else None,
                    "location": location_el.get_text(strip=True) if location_el else None,
                    "url": f"https://www.olx.pl{link_el["href"]}" if link_el else None,
                })
            
            time.sleep(random.uniform(2, 5))
    return results

# def scrape_detail(url: str) -> dict:
#     soup = get_page(url)
#     if soup:
#     title   = soup.select_one("h1[data-cy='ad_title']")
#     price   = soup.select_one("[data-testid='ad-price-container']")
#     desc    = soup.select_one("[data-cy='ad_description']")

#     # Parametry (np. stan, marka) - są w listach <li>
#     params = {}
#     for item in soup.select("[data-testid='ad-details-list'] li"):
#         key = item.select_one("p:first-child")
#         val = item.select_one("p:last-child")
#         if key and val:
#             params[key.get_text(strip=True)] = val.get_text(strip=True)

#     return {
#         "title":       title.get_text(strip=True) if title else None,
#         "price":       price.get_text(strip=True) if price else None,
#         "description": desc.get_text(strip=True) if desc else None,
#         "params":      params,
#     }

if __name__ == "__main__":
    listings = scrape_listings("iphone-14", pages=2)

    for item in listings:
        print(item["title"], "|", item["price"], "|", item["location"])
        print(" ->", item["url"])
    # if listings:
    #     detail = scrape_detail(listings[0]["url"])
    #     print(detail)