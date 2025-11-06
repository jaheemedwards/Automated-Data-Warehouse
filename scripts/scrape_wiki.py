import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# List of 20 capitals
capitals = [
    {"city": "Washington, D.C.", "country": "United States"},
    {"city": "London", "country": "United Kingdom"},
    {"city": "Moscow", "country": "Russia"},
    {"city": "Beijing", "country": "China"},
    {"city": "Tokyo", "country": "Japan"},
    {"city": "Port of Spain", "country": "Trinidad and Tobago"},
    {"city": "Ottawa", "country": "Canada"},
    {"city": "Berlin", "country": "Germany"},
    {"city": "Paris", "country": "France"},
    {"city": "Brasília", "country": "Brazil"},
    {"city": "Canberra", "country": "Australia"},
    {"city": "New Delhi", "country": "India"},
    {"city": "Rome", "country": "Italy"},
    {"city": "Madrid", "country": "Spain"},
    {"city": "Cairo", "country": "Egypt"},
    {"city": "Seoul", "country": "South Korea"},
    {"city": "Bangkok", "country": "Thailand"},
    {"city": "Nairobi", "country": "Kenya"},
    {"city": "Mexico City", "country": "Mexico"},
    {"city": "Buenos Aires", "country": "Argentina"}
]

def dms_to_decimal(dms_str):
    """Convert DMS (55°45′21″N) to decimal degrees"""
    s = dms_str.replace("°", " ").replace("′", " ").replace("″", " ")
    parts = re.findall(r'([0-9]+(?:\.[0-9]+)?)', s)
    dir_match = re.search(r'([NSEW])', dms_str, re.I)
    if not parts:
        return None
    deg = float(parts[0])
    minute = float(parts[1]) if len(parts) > 1 else 0
    sec = float(parts[2]) if len(parts) > 2 else 0
    dec = deg + minute/60 + sec/3600
    if dir_match:
        d = dir_match.group(1).upper()
        if d in ("S", "W"):
            dec = -dec
    return dec

def extract_coordinates(infobox):
    """Extract coordinates from infobox"""
    geo = infobox.select_one("span.geo")
    if geo and geo.text.strip():
        text = geo.text.strip()
        if ";" in text:
            lat_str, lon_str = [p.strip() for p in text.split(";")[:2]]
        else:
            parts = text.split()
            lat_str, lon_str = parts[0], parts[1] if len(parts) >= 2 else (None, None)
        try:
            return float(lat_str), float(lon_str)
        except:
            pass

    geo_dec = infobox.select_one("span.geo-dec")
    if geo_dec:
        matches = re.findall(r'(-?\d+(?:\.\d+)?)', geo_dec.text)
        if len(matches) >= 2:
            return float(matches[0]), float(matches[1])

    geo_dms = infobox.select_one("span.geo-dms")
    if geo_dms:
        dms_groups = re.findall(r'[0-9°\'\"″′\s]+[NnSsEeWw]', geo_dms.text)
        if len(dms_groups) >= 2:
            return dms_to_decimal(dms_groups[0]), dms_to_decimal(dms_groups[1])

    return None, None

def scrape_city_coordinates(city_name):
    """Scrape infobox for coordinates only"""
    url = f"https://en.wikipedia.org/wiki/{city_name.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    infobox = soup.select_one("table.infobox.ib-settlement.vcard")
    if infobox:
        return extract_coordinates(infobox)
    return None, None

# Build DataFrame
records = []
for cap in capitals:
    lat, lon = scrape_city_coordinates(cap["city"])
    records.append({
        "city_name": cap["city"],
        "country": cap["country"],
        "latitude": lat,
        "longitude": lon
    })

df = pd.DataFrame(records)
# print(df)
# Optionally save
# import os
# os.makedirs("data", exist_ok=True)
# df.to_csv("data/capitals_coordinates.csv", index=False)
