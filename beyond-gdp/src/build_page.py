"""Build the Chinese and English pages from the templates and the files in data/.

Outputs:
  ../index.html     Chinese, from template_zh.html
  ../en/index.html  English, from template_en.html

Inputs:
  data/indicators.json  output of build_data.py
  data/area.json        housing floor area per person, hand-collected (m2, year, source)
  data/rail.json        high-speed rail pkm, light rail / tram trips, China urban-rail pkm
  data/night_safety.json  Gallup: % who feel safe walking alone at night (2024)
  data/regions.json     Jiangsu+Zhejiang+Shanghai, shown as a regional reference
  data/findings_<lang>.html  the hand-written findings shown under the scatter chart
  data/jzs_<lang>.html       the hand-written notes under the Jiangsu-Zhejiang-Shanghai table

Usage: python3 build_page.py
"""
import collections
import json
import os

from names import EN, EXCLUDE, FOCUS, G20

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUTPUTS = {"zh": os.path.join(HERE, "..", "index.html"), "en": os.path.join(HERE, "..", "en", "index.html")}
RAIL_MIN, RAIL_MAX = 10, 1500  # km per person per year: 0 and full score (log scale)
# Indicators replaced by another economy's value where the own figure misleads.
# Luxembourg: most students study abroad, so its own tertiary enrolment (22%) is far too low.
SUBSTITUTE = {"LUX": ("EUU", ["ter"])}

YEAR_LABELS = {
    "gdp": ("人均 GDP（PPP）", "GDP per person (PPP)"),
    "elec": ("人均用电量", "Electricity use per person"),
    "fruit": ("水果、蔬菜、肉、蛋（FAO）", "Fruit, vegetables, meat, eggs (FAO)"),
    "area": ("人均住房面积", "Floor area per person"),
    "cars": ("每千人机动车", "Vehicles per 1,000 people"),
    "life": ("预期寿命", "Life expectancy"),
    "imr": ("婴儿死亡率", "Infant mortality"),
    "net": ("互联网用户比例", "Internet users"),
    "bb": ("固定宽带", "Fixed broadband"),
    "g5": ("5G 覆盖率", "5G coverage"),
    "hom": ("命案率", "Homicide rate"),
    "ter": ("高等教育毛入学率", "Tertiary gross enrolment"),
    "night": ("夜间独自走路感到安全（盖洛普）", "Feel safe walking alone at night (Gallup)"),
}


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf8") as f:
        return json.load(f) if name.endswith(".json") else f.read()


ind = load("indicators.json")
rows, yrs = ind["rows"], ind["years"]
area, rail, night, regions = load("area.json"), load("rail.json"), load("night_safety.json"), load("regions.json")

DATA = []
for c, r in rows.items():
    if c in EXCLUDE:
        continue
    d = {k: r.get(k) for k in ["code", "name", "gdp", "pop", "elec", "fruit", "veg", "meat", "egg", "life", "imr", "net", "bb", "g5", "cars", "hom", "ter"]}
    d["gdpY"], d["carsY"] = yrs["gdp"][c], yrs.get("cars", {}).get(c)
    for k in ["fruit", "veg", "meat", "egg", "life", "imr", "net", "bb", "g5", "elec", "hom", "ter"]:
        if d[k] is not None:
            d[k] = round(d[k], 1)
    d["gdp"] = round(d["gdp"])
    if c in area:
        d["area"], d["areaY"], d["weakArea"] = area[c]["use"], area[c]["y"], bool(area[c].get("weak"))
    else:
        d["area"] = None
    d["hsr"] = rail["hsr"].get(c, {}).get("v")
    d["urbanTrips"] = round((r.get("metroTrips") or 0) + rail["lrt"].get(c, 0), 1)
    d["urbanPkm"] = rail.get("urbanPkm", {}).get(c)
    d["night"] = night["values"].get(c)
    if c in SUBSTITUTE:
        src, keys = SUBSTITUTE[c]
        for k in keys:
            d[k] = round(rows[src][k], 1)
    DATA.append(d)
shown = {d["code"] for d in DATA}


def year_summary(label, by_code, lang):
    ys = [int(str(y)[:4]) for y in by_code.values() if y is not None]
    if not ys:
        return None
    mode = collections.Counter(ys).most_common(1)[0][0]
    other = [y for y in ys if y != mode]
    rng = "" if not other else f"{min(other)}{'' if min(other) == max(other) else '–' + str(max(other))}"
    if not other:
        span = ""
    elif lang == "zh":
        span = f"（另有 {len(other)} 个为 {rng}）"
    else:
        span = f" ({len(other)} others: {rng})"
    return {"label": label, "years": f"{mode}{span}", "n": len(ys)}


def build(lang):
    zh = lang == "zh"
    sfx = "" if zh else "_en"
    data = [dict(d, name=d["name"] if zh else EN[d["code"]]) for d in DATA]
    pick = lambda key: {c: y for c, y in yrs.get(key, {}).items() if c in shown}
    sources_by_key = {
        "area": {c: a["y"] for c, a in area.items() if c in shown},
        "night": {c: night["year"] for c in night["values"] if c in shown},
    }
    years = []
    for key, labels in YEAR_LABELS.items():
        y = year_summary(labels[0 if zh else 1], sources_by_key.get(key) or pick(key), lang)
        if y:
            years.append(y)
    areasrc = [{"name": rows[c]["name"] if zh else EN[c], "raw": a["v"], "y": a["y"], "note": a["note" + sfx], "url": a["url"]}
               for c, a in sorted(area.items(), key=lambda t: -t[1]["use"]) if c in shown]
    jzs = dict(regions["JZS"])
    jzs["name"], jzs["notes"], jzs["national"] = jzs["name" + sfx], jzs["notes" + sfx], jzs["national" + sfx]
    with open(os.path.join(HERE, f"template_{lang}.html"), encoding="utf8") as f:
        page = f.read()
    fills = {
        "/*__DATA__*/": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        "/*__YEARS__*/": json.dumps(years, ensure_ascii=False),
        "/*__AREASRC__*/": json.dumps(areasrc, ensure_ascii=False),
        "/*__G20__*/": json.dumps(G20),
        "/*__FOCUS__*/": json.dumps(FOCUS),
        "/*__REGIONS__*/": json.dumps([jzs], ensure_ascii=False),
        "<!--__REGIONSRC__-->": "\n    ".join(regions["sources" + sfx]),
        "/*__RMIN__*/": str(RAIL_MIN),
        "/*__RMAX__*/": str(RAIL_MAX),
        "__NAREA__": str(sum(1 for d in DATA if d["area"] is not None)),
        "__NOAREA__": str(sum(1 for d in DATA if d["area"] is None)),
        "__N__": str(len(DATA)),
        "<!--__FINDINGS__-->": load(f"findings_{lang}.html").strip(),
        "<!--__JZSTEXT__-->": load(f"jzs_{lang}.html").strip(),
        "<!--__RAILSRC__-->": "\n    ".join(rail["sources" + sfx]),
    }
    for key, val in fills.items():
        assert key in page, f"placeholder {key} missing from template_{lang}.html"
        page = page.replace(key, val)
    os.makedirs(os.path.dirname(OUTPUTS[lang]), exist_ok=True)
    with open(OUTPUTS[lang], "w", encoding="utf8") as f:
        f.write(page)
    print(f"{lang}: {len(data)} economies -> {os.path.relpath(OUTPUTS[lang], os.path.join(HERE, '..', '..'))}")


for lang in OUTPUTS:
    build(lang)
