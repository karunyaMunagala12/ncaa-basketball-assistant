# scraper_player_profile.py

import requests
from bs4 import BeautifulSoup

def get_text_or_blank(tag):
    return tag.text.strip() if tag else ""

def scrape_player(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.content, "html.parser")

        # === Player Name ===
        name = get_text_or_blank(soup.find("h1"))

        # === Metadata Section ===
        meta = soup.find("div", id="meta")
        position = height = weight = hometown = school = ""

        if meta:
            for li in meta.find_all(["p", "li"]):
                text = li.get_text().strip()
                if "Position:" in text:
                    position = text.split("Position:")[1].strip()
                if "lb" in text and "(" in text:
                    parts = text.split(",")
                    if len(parts) >= 2:
                        height = parts[0].strip()
                        weight = parts[1].strip()
                if "Hometown:" in text:
                    hometown = text.split("Hometown:")[1].strip()
                if "School:" in text and li.find("a"):
                    school = li.find("a").text.strip()

        # === Stats Table (Per Game) ===
        stats = []
        career_totals = {}
        for table in soup.find_all("table"):
            header_cells = [th.text.strip() for th in table.find_all("th")]
            if "G" in header_cells and "PTS" in header_cells:
                try:
                    rows = table.find_all("tr")
                    headers = [th.text.strip() for th in rows[0].find_all("th")]
                    for row in rows[1:]:
                        cols = [td.text.strip() for td in row.find_all("td")]
                        if not cols:
                            continue
                        if "Career" in row.text:
                            career_totals = dict(zip(headers[1:], cols))
                        elif len(cols) == len(headers) - 1:
                            stats.append(dict(zip(headers[1:], cols)))
                    break
                except Exception:
                    continue

        return {
            "name": name,
            "position": position,
            "height": height,
            "weight": weight,
            "hometown": hometown,
            "school": school,
            "stats": stats,
            "career_totals": career_totals
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None