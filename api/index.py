from bs4 import BeautifulSoup
from fastapi import FastAPI, Query
import requests

app = FastAPI()


@app.get('/')
def home():
  return {
      'status': (
          'Cloud Lead Scraper is live! Use /scrape?keyword=...&location=...'
      )
  }


@app.get('/scrape')
def scrape_leads(
    keyword: str = Query(..., description='Target niche'),
    location: str = Query(..., description='Target location'),
):
  headers = {
      'User-Agent': (
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
          ' like Gecko) Chrome/120.0.0.0 Safari/537.36'
      )
  }

  query = f'{keyword} {location}'
  leads = []

  try:
    response = requests.post(
        'https://html.duckduckgo.com/html/',
        data={'q': query},
        headers=headers,
        timeout=10,
    )

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      results = soup.find_all('div', class_='result')

      for result in results:
        title_tag = result.find('a', class_='result__snippet')
        link_tag = result.find('a', class_='result__url')

        if title_tag and link_tag:
          leads.append({
              'title': title_tag.get_text(strip=True),
              'link': link_tag.get('href'),
          })
  except Exception as e:
    return {'error': str(e)}

  return {
      'keyword': keyword,
      'location': location,
      'total_leads': len(leads),
      'leads': leads,
  }
