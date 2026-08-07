from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import time, random, logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0" ,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def build_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return f"https://www.olx.pl{href}"

def get_page(url: str):
    logger.info("Tworze sesje...")
    session = requests.Session(impersonate="firefox")
    for attempt in range(3):
        try:
            response = session.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return bs(response.text, "html.parser")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout, proba {attempt+1}/3...")
            time.sleep(5)
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e}, proba {attempt+1}/3...")
            time.sleep(5)
    logger.error("Nie udalo sie polaczyc z OLX.", exc_info=True)
    return None

def scrape_listings(query: str, pages: int = 3) -> list[dict]:
    results = []
    logger.info("Pozyskuje HTML...")
    for page in range(1, pages + 1):
        url = f"https://www.olx.pl/oferty/q-{query}/?page={page}"
        soup = get_page(url)
        if soup:
            logger.info(f"Zbieram informacje na temat {query} ze strony nr {page}/{pages}")
            cards = soup.select("[data-cy='l-card']")
            
            for card in cards:
                title_el = card.select_one("[data-testid='card-title-link']")
                price_el = card.select_one("[data-testid='ad-price']")
                stan_el = card.select_one("[data-nx-name='NexusBadge']:not([data-testid='free-delivery-tag'])")
                location_el = card.select_one("[data-testid='location-date']")

                results.append({
                    "title": title_el.get_text(strip=True) if title_el else None,
                    "price": price_el.get_text(strip=True) if price_el else None,
                    "stan": stan_el.get_text(strip=True) if stan_el else None,
                    "location": location_el.get_text(strip=True) if location_el else None,
                    "url": build_url(title_el["href"]) if title_el and title_el.has_attr("href") else None,
                })
            
            time.sleep(random.uniform(2, 5))
        else:
            logger.error("Nie udalo sie zebrac informacji.", exc_info=True)
    return results


if __name__ == "__main__":
    listings = scrape_listings("iphone-14", pages=1)
    print(f"Znaleziono {len(listings)} ofert")
    print(listings[:2])
