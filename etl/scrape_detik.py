import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

query = "pssi"

def scrape_detik():
    pages_num = 5
    berita_list = []
    print(f"Scraping Detik for query: {query} for {pages_num} pages...")

    # Setup session + retry
    session = requests.Session()
    retry_strategy = Retry(
        total=3,            # coba ulang 3 kali
        backoff_factor=1,   # jeda antar retry: 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' 
    }

    for i in range(pages_num):
        url = f'https://www.detik.com/search/searchnews?query={query}&result_type=latest&page={i+1}'
        print(f"Fetching: {url}")
        
        try:
            res = session.get(url, headers=headers, timeout=10)
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text[:500]}")
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            articles = soup.find_all('article', class_='list-content__item')

            for art in articles:
                title_elem = art.find('h3', class_='media__title')
                desc_elem = art.find('div', class_='media__desc')
                link_elem = art.find('a', class_='media__link')
                time_elem = art.find('div', class_='media__date')

                berita = {
                    'judul': title_elem.text.strip() if title_elem else '',
                    'deskripsi': desc_elem.text.strip() if desc_elem else '',
                    'link': link_elem['href'] if link_elem else '',
                    'waktu': time_elem.text.strip() if time_elem else ''
                }

                berita_list.append(berita)
            print(f'Page {i+1} scraped successfully.')

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text[:500]}") 

            continue

    # convert ke DataFrame
    df = pd.DataFrame(berita_list)
    return df

