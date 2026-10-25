"""Select the economies and merge every downloaded indicator into data/indicators.json.

Reads raw/ (from fetch.py). The curated files in data/ (area.json, rail.json) are
not touched here; build_page.py combines them with this output.

Usage: python3 build_data.py
"""
import csv
import html
import json
import os
import re

from names import ALIAS, EU, EXCLUDE, MEMBERS_SHOWN, METRO_CITY, ZH

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "data", "indicators.json")
TOP_PER_CAPITA, TOP_TOTAL = 100, 50


def load(rel):
    with open(os.path.join(RAW, rel), encoding="utf8") as f:
        return json.load(f) if rel.endswith(".json") else f.read()


meta = {c["id"]: c for c in load("wb/countries.json")[1]}
real = {k for k, v in meta.items() if v["region"]["value"] != "Aggregates"}
n2iso = {v["name"]: k for k, v in meta.items()}
n2iso.update(ALIAS)


def wb(code):
    """Latest non-null (value, year) per country for one World Bank indicator."""
    best = {}
    for x in load(f"wb/{code}.json")[1]:
        c = x["countryiso3code"]
        if x["value"] is not None and (c not in best or int(x["date"]) > best[c][1]):
            best[c] = (x["value"], int(x["date"]))
    return best


# --- selection: top 100 by GDP per capita (PPP) plus top 50 by total GDP, EU merged
gdp_pc, gdp_total = wb("NY.GDP.PCAP.PP.CD"), wb("NY.GDP.MKTP.CD")
by_pc = sorted((c for c in gdp_pc if c in real), key=lambda c: -gdp_pc[c][0])[:TOP_PER_CAPITA]
by_total = sorted((c for c in gdp_total if c in real), key=lambda c: -gdp_total[c][0])[:TOP_TOTAL]
lst = []
for c in by_pc + by_total:
    if c not in EU and c not in EXCLUDE and c not in lst:
        lst.append(c)
lst += MEMBERS_SHOWN  # France, Germany, Italy also stand on their own
missing_names = [c for c in lst if c not in ZH]
if missing_names:
    raise SystemExit(f"Add Chinese names to names.py for: {missing_names}")
ECON = lst + ["EUU"]

pop = wb("SP.POP.TOTL")
rows = {c: {"code": c, "name": ZH[c]} for c in ECON}
years = {}


def put(key, c, val):
    if val is None:
        rows[c][key] = None
        return
    rows[c][key] = val[0]
    years.setdefault(key, {})[c] = val[1]


def eu_avg(r, min_members=27):
    """Population-weighted average of the EU members that have data; year is the oldest member year."""
    have = [c for c in EU if c in r]
    if len(have) < min_members:
        return None
    v = sum(r[c][0] * pop[c][0] for c in have) / sum(pop[c][0] for c in have)
    return (v, min(r[c][1] for c in have))


for c in lst:
    put("gdp", c, gdp_pc[c])
put("gdp", "EUU", gdp_pc.get("EUU"))
for c in ECON:
    put("pop", c, pop.get(c))
for key, code in [("life", "SP.DYN.LE00.IN"), ("imr", "SP.DYN.IMRT.IN"), ("net", "IT.NET.USER.ZS"), ("bb", "IT.NET.BBND.P2"), ("hom", "VC.IHR.PSRC.P5")]:
    r = wb(code)
    for c in lst:
        put(key, c, r.get(c))
    put(key, "EUU", eu_avg(r) or r.get("EUU"))


def owid(fn, col=None):
    """Latest value per economy from an OWID CSV; the EU row is 'European Union (27)'."""
    rd = csv.DictReader(open(os.path.join(RAW, "owid", fn), encoding="utf8"))
    col = col or rd.fieldnames[3]
    best = {}
    for x in rd:
        code = x.get("code") or x.get("iso_code")
        ent = x.get("entity") or x.get("country")
        k = "EUU" if ent == "European Union (27)" else code
        if k and x.get(col):
            y = int(x["year"])
            if k not in best or y > best[k][1]:
                best[k] = (float(x[col]), y)
    return best


for key, fn, col in [
    ("elec", "energy.csv", "electricity_demand_per_capita"),  # generation + net imports
    ("fruit", "fruit-consumption-per-capita.csv", None),
    ("veg", "vegetable-consumption-per-capita.csv", None),
    ("meat", "meat-supply-per-person.csv", None),
    ("egg", "per-capita-egg-consumption-kilograms-per-year.csv", None),
]:
    b = owid(fn, col)
    for c in ECON:
        put(key, c, b.get(c))
# 5G population coverage from the UN SDG database, which uses numeric M49 codes
m49 = {int(r["country-code"]): r["alpha-3"] for r in csv.DictReader(open(os.path.join(RAW, "un", "iso3166.csv"), encoding="utf8"))}
g5 = {}
for x in load("un/IT_MOB_5GNTWK.json")["data"]:
    c, y = m49.get(int(x["geoAreaCode"])), int(float(x["timePeriodStart"]))
    try:
        v = float(x["value"])
    except (TypeError, ValueError):
        continue
    if c and (c not in g5 or y > g5[c][1]):
        g5[c] = (v, y)
for c in lst:
    put("g5", c, g5.get(c))
put("g5", "EUU", eu_avg(g5))

# Education (UNESCO UIS): tertiary gross enrolment ratio and STEM share of tertiary graduates
for key, code in [("ter", "GER.5T8"), ("stem", "FOSGP.5T8.F500600700")]:
    best = {}
    for x in load(f"uis/{code}.json")["records"]:
        c, y = x["geoUnit"], x["year"]
        if x["value"] is not None and (c not in best or y > best[c][1]):
            best[c] = (x["value"], y)
    for c in lst:
        put(key, c, best.get(c))
    put(key, "EUU", eu_avg(best, min_members=24))

# --- Wikipedia tables
clean = lambda s: re.sub(r"\[[^\]]*\]", "", html.unescape(re.sub("<[^>]+>", "", s))).strip()

t = load("wiki/vehicles.html")
veh = {}
for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
    cells = [clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
    if len(cells) > 4 and cells[0] in n2iso and re.match(r"^[\d,]+$", cells[2] or ""):
        iso = n2iso[cells[0]]
        veh.setdefault(iso, (int(cells[2].replace(",", "")), int(cells[3].replace(",", "")), cells[4]))
for c in lst:
    put("cars", c, (round(veh[c][0] / veh[c][1] * 1000), int(veh[c][2][:4])) if c in veh else None)
eu_v = [veh[c] for c in EU if c in veh]
put("cars", "EUU", (round(sum(v[0] for v in eu_v) / sum(v[1] for v in eu_v) * 1000), max(int(v[2][:4]) for v in eu_v)))

# Metro ridership: the table uses rowspan for countries, so carry spanned cells down.
t = load("wiki/metro.html")
table = max(re.findall(r"<table[^>]*wikitable[^>]*>(.*?)</table>", t, re.S), key=len)
grid, carry = [], {}
for r in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)[1:]:
    cells = re.findall(r"<t[hd]([^>]*)>(.*?)</t[hd]>", r, re.S)
    row, ci, k = [], 0, 0
    while ci < 8:
        if ci in carry and carry[ci][1] > 0:
            row.append(carry[ci][0])
            carry[ci] = (carry[ci][0], carry[ci][1] - 1)
            ci += 1
            continue
        if k >= len(cells):
            break
        attr, c = cells[k]
        k += 1
        v = clean(c)
        row.append(v)
        m = re.search(r'rowspan="?(\d+)', attr)
        if m:
            carry[ci] = (v, int(m.group(1)) - 1)
        ci += 1
    grid.append(row)
metro = {}
for row in grid:
    if len(row) < 8:
        continue
    iso = METRO_CITY.get(row[1]) or n2iso.get(row[2])
    m = re.match(r"([\d.]+)\s*\((\d{4})", row[7].replace(",", ""))
    if not m:
        continue
    for key in {iso, "EUU" if iso in EU else iso}:  # a shown EU member counts for itself and the EU
        if key in ECON:
            metro[key] = metro.get(key, 0) + float(m.group(1))
for c in ECON:
    rows[c]["metroTrips"] = round(metro.get(c, 0), 1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf8") as f:
    json.dump({"rows": rows, "years": years}, f, ensure_ascii=False, indent=1)
print(f"{len(ECON)} economies -> {os.path.relpath(OUT, HERE)}")
for key in ["elec", "fruit", "cars", "life", "imr", "net", "g5", "hom", "ter", "stem"]:
    gaps = [ZH[c] for c in ECON if rows[c].get(key) is None]
    if gaps:
        print(f"  missing {key}: {', '.join(gaps)}")
