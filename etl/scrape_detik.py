import requests
from bs4 import BeautifulSoup
import pandas as pd

query = "pssi"

def scrape_detik():
    pages_num = 5
    berita_list = []
    print(f"Scraping Detik for query: {query} for {pages_num} pages...")

    for i in range(pages_num):
        url = f'https://www.detik.com/search/searchnews?query={query}&result_type=latest&page={i+1}'
        headers = {
            'User-Agent': 'Mozilla/5.0' 
        }

        res = requests.get(url, headers=headers)
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

    # convert ke DataFrame
    df = pd.DataFrame(berita_list)
    return df

