"""Download the raw inputs into raw/. Run before build_data.py when updating the numbers.

Usage: python3 fetch.py
"""
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
UA = {"User-Agent": "Mozilla/5.0 (Sea-Fill beyond-gdp build)"}

WB = "https://api.worldbank.org/v2"
WB_INDICATORS = {
    "NY.GDP.PCAP.PP.CD": "2022:2025",  # GDP per capita, PPP; selection and comparison
    "NY.GDP.MKTP.CD": "2022:2025",     # total GDP, current US$; selection only
    "SP.POP.TOTL": "2015:2025",
    "SP.DYN.LE00.IN": "2015:2025",
    "SP.DYN.IMRT.IN": "2015:2025",
    "IT.NET.USER.ZS": "2015:2025",
    "IT.NET.BBND.P2": "2015:2025",
}
OWID_CHARTS = [
    "fruit-consumption-per-capita",
    "vegetable-consumption-per-capita",
    "meat-supply-per-person",
    "per-capita-egg-consumption-kilograms-per-year",
]
FILES = {
    "wb/countries.json": f"{WB}/country?format=json&per_page=400",
    "owid/energy.csv": "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv",
    "wiki/vehicles.html": "https://en.wikipedia.org/wiki/List_of_countries_by_vehicles_per_capita",
    "wiki/metro.html": "https://en.wikipedia.org/wiki/List_of_metro_systems",
    # ITU 5G population coverage (SDG 9.c.1) and an ISO numeric -> alpha-3 table for its UN M49 codes
    "un/IT_MOB_5GNTWK.json": "https://unstats.un.org/sdgapi/v1/sdg/Series/Data?seriesCode=IT_MOB_5GNTWK&pageSize=20000",
    "un/iso3166.csv": "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv",
}
for code, years in WB_INDICATORS.items():
    FILES[f"wb/{code}.json"] = f"{WB}/country/all/indicator/{code}?format=json&date={years}&per_page=20000"
for slug in OWID_CHARTS:
    FILES[f"owid/{slug}.csv"] = f"https://ourworldindata.org/grapher/{slug}.csv?v=1&csvType=full&useColumnShortNames=true"


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except Exception as e:  # the World Bank API times out now and then
            if i == tries - 1:
                raise
            print("  retry:", e)
            time.sleep(5)


for rel, url in FILES.items():
    path = os.path.join(RAW, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print("fetch", rel)
    data = get(url)
    with open(path, "wb") as f:
        f.write(data)
print("done:", len(FILES), "files in raw/")
