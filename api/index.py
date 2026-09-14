import csv
import io
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, StreamingResponse
import requests

app = FastAPI()


def clean_ddg_url(raw_url):
  if 'uddg=' in raw_url:
    try:
      parsed = urlparse(raw_url)
      qs = parse_qs(parsed.query)
      if 'uddg' in qs:
        return qs['uddg'][0]
    except:
      pass
  return raw_url


@app.get('/', response_class=HTMLResponse)
def home():
  return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud Lead Generation Dashboard</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #0f172a; color: #f8fafc; padding: 40px 20px; }
            .container { max-width: 900px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
            h1 { color: #38bdf8; text-align: center; margin-bottom: 25px; font-size: 26px; }
            .search-box { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
            .input-group { flex: 1; min-width: 250px; }
            label { display: block; margin-bottom: 8px; color: #cbd5e1; font-size: 14px; font-weight: 600; }
            input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 14px; }
            input:focus { outline: none; border-color: #38bdf8; }
            button { align-self: flex-end; padding: 12px 25px; background: #0284c7; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: background 0.2s; height: 44px; }
            button:hover { background: #0ea5e9; }
            .download-btn { background: #10b981; }
            .download-btn:hover { background: #059669; }
            
            #loader { text-align: center; display: none; color: #38bdf8; margin: 20px 0; font-weight: 600; }
            .results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #334155; padding-bottom: 10px; flex-wrap: wrap; gap: 10px; }
            .lead-card { background: #334155; padding: 18px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #38bdf8; }
            .lead-card h3 { font-size: 16px; margin-bottom: 8px; color: #f1f5f9; }
            .lead-card a { color: #38bdf8; text-decoration: none; word-break: break-all; font-size: 14px; }
            .lead-card a:hover { text-decoration: underline; }
            .no-data { text-align: center; color: #94a3b8; margin-top: 20px; }
        </style>
    </head>
    <body>

        <div class="container">
            <h1>🚀 Cloud Lead Generation Dashboard</h1>
            
            <div class="search-box">
                <div class="input-group">
                    <label>Target Keyword / Niche</label>
                    <input type="text" id="keyword" placeholder="e.g. Real Estate Agents">
                </div>
                <div class="input-group">
                    <label>Target Location</label>
                    <input type="text" id="location" placeholder="e.g. New York">
                </div>
                <button type="button" onclick="fetchLeads()">Generate Leads</button>
            </div>

            <div id="loader">Extracting targeted leads from the cloud... ⏳</div>

            <div id="results-section"></div>
        </div>

        <script>
            let globalLeads = [];

            async function fetchLeads() {
                const keywordInput = document.getElementById('keyword').value.trim();
                const locationInput = document.getElementById('location').value.trim();
                const loaderDiv = document.getElementById('loader');
                const resultsDiv = document.getElementById('results-section');

                if (!keywordInput || !locationInput) {
                    alert('Please fill in both fields!');
                    return;
                }

                loaderDiv.style.display = 'block';
                resultsDiv.innerHTML = '';

                try {
                    const res = await fetch('/scrape?keyword=' + encodeURIComponent(keywordInput) + '&location=' + encodeURIComponent(locationInput));
                    const json = await res.json();

                    loaderDiv.style.display = 'none';
                    globalLeads = json.leads || [];

                    if (globalLeads.length > 0) {
                        let htmlOutput = `
                            <div class="results-header">
                                <h3>Results for "` + json.keyword + `" in "` + json.location + `"</h3>
                                <div>
                                    <button type="button" class="download-btn" onclick="downloadCSV()">📥 Download CSV</button>
                                    <span style="margin-left: 10px;">Total Leads: <strong>` + globalLeads.length + `</strong></span>
                                </div>
                            </div>
                        `;

                        globalLeads.forEach(function(lead, index) {
                            htmlOutput += `
                                <div class="lead-card">
                                    <h3>#` + (index + 1) + ` Business Lead</h3>
                                    <p style="margin-bottom: 8px; color: #cbd5e1; font-size: 14px;">` + lead.title + `</p>
                                    <a href="` + lead.link + `" target="_blank">🔗 ` + lead.link + `</a>
                                </div>
                            `;
                        });

                        resultsDiv.innerHTML = htmlOutput;
                    } else {
                        resultsDiv.innerHTML = '<p class="no-data">No leads found. Try a different keyword or location.</p>';
                    }
                } catch (err) {
                    loaderDiv.style.display = 'none';
                    resultsDiv.innerHTML = '<p class="no-data" style="color: #ef4444;">Error fetching leads: ' + err.message + '</p>';
                }
            }

            function downloadCSV() {
                if (globalLeads.length === 0) return;
                
                let csvContent = "data:text/csv;charset=utf-8,Title,Website\\n";
                globalLeads.forEach(function(lead) {
                    let safeTitle = lead.title ? lead.title.replace(/"/g, '""') : "";
                    csvContent += '"' + safeTitle + '","' + lead.link + '"\\n';
                });

                let encodedUri = encodeURI(csvContent);
                let downloadLink = document.createElement("a");
                downloadLink.setAttribute("href", encodedUri);
                downloadLink.setAttribute("download", "targeted_leads.csv");
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }
        </script>
    </body>
    </html>
    """


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
          raw_link = link_tag.get('href')
          clean_link = clean_ddg_url(raw_link)

          if 'duckduckgo.com' not in clean_link:
            leads.append({
                'title': title_tag.get_text(strip=True),
                'link': clean_link,
            })
  except Exception as e:
    return {'error': str(e)}

  return {
      'keyword': keyword,
      'location': location,
      'total_leads': len(leads),
      'leads': leads,
  }
