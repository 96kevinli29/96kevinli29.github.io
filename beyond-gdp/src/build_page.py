"""Build ../index.html from template.html and the files in data/.

Inputs:
  data/indicators.json  output of build_data.py
  data/area.json        housing floor area per person, hand-collected (m2, year, source)
  data/rail.json        high-speed rail pkm, light rail / tram trips, China urban-rail pkm
  data/night_safety.json  Gallup: % who feel safe walking alone at night (2024)
  data/stem_extra.json  STEM graduate shares for China and Japan from their ministries
  data/regions.json     Jiangsu+Zhejiang+Shanghai, shown as a regional reference
  data/findings.html    the hand-written findings shown under the scatter chart
  data/jzs.html         the hand-written notes under the Jiangsu-Zhejiang-Shanghai table

Usage: python3 build_page.py
"""
import collections
import json
import os

from names import EXCLUDE, FOCUS, G20

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..", "index.html")
RAIL_MIN, RAIL_MAX = 10, 1500  # km per person per year: 0 and full score (log scale)
# Indicators replaced by another economy's value where the own figure misleads.
# Luxembourg: most students study abroad, so its own tertiary enrolment (22%) is far too low.
SUBSTITUTE = {"LUX": ("EUU", ["ter", "stem"])}


def load(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf8") as f:
        return json.load(f) if name.endswith(".json") else f.read()


ind = load("indicators.json")
rows, yrs = ind["rows"], ind["years"]
area, rail, findings, jzs_text = load("area.json"), load("rail.json"), load("findings.html"), load("jzs.html")
night = load("night_safety.json")
stem_extra = load("stem_extra.json")["values"]
regions = load("regions.json")

DATA = []
for c, r in rows.items():
    if c in EXCLUDE:
        continue
    d = {k: r.get(k) for k in ["code", "name", "gdp", "pop", "elec", "fruit", "veg", "meat", "egg", "life", "imr", "net", "bb", "g5", "cars", "hom", "ter", "stem"]}
    d["gdpY"], d["carsY"] = yrs["gdp"][c], yrs.get("cars", {}).get(c)
    for k in ["fruit", "veg", "meat", "egg", "life", "imr", "net", "bb", "g5", "elec", "hom", "ter", "stem"]:
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
    if d["stem"] is None and c in stem_extra:  # China, Japan: ministry figures
        d["stem"] = stem_extra[c]["v"]
    if c in SUBSTITUTE:
        src, keys = SUBSTITUTE[c]
        for k in keys:
            d[k] = round(rows[src][k], 1)
    DATA.append(d)


def year_summary(label, by_code):
    ys = [int(str(y)[:4]) for y in by_code.values() if y is not None]
    if not ys:
        return None
    mode = collections.Counter(ys).most_common(1)[0][0]
    other = [y for y in ys if y != mode]
    span = "" if not other else f"（另有 {len(other)} 个为 {min(other)}{'' if min(other) == max(other) else '–' + str(max(other))}）"
    return {"label": label, "years": f"{mode}{span}", "n": len(ys)}


shown = {d["code"] for d in DATA}
pick = lambda key: {c: y for c, y in yrs.get(key, {}).items() if c in shown}
YEARS = [y for y in [
    year_summary("人均 GDP（PPP）", pick("gdp")),
    year_summary("人均用电量", pick("elec")),
    year_summary("水果、蔬菜、肉、蛋（FAO）", pick("fruit")),
    year_summary("人均住房面积", {c: a["y"] for c, a in area.items() if c in shown}),
    year_summary("每千人机动车", pick("cars")),
    year_summary("预期寿命", pick("life")),
    year_summary("婴儿死亡率", pick("imr")),
    year_summary("互联网用户比例", pick("net")),
    year_summary("固定宽带", pick("bb")),
    year_summary("5G 覆盖率", pick("g5")),
    year_summary("命案率", pick("hom")),
    year_summary("高等教育毛入学率", pick("ter")),
    year_summary("STEM 毕业生占比", {**pick("stem"), **{c: v["y"] for c, v in stem_extra.items() if c in shown}}),
    year_summary("夜间独自走路感到安全（盖洛普）", {c: night["year"] for c in night["values"] if c in shown}),
] if y]
AREASRC = [{"name": rows[c]["name"], "raw": a["v"], "y": a["y"], "note": a["note"], "url": a["url"]}
           for c, a in sorted(area.items(), key=lambda t: -t[1]["use"]) if c in shown]

with open(os.path.join(HERE, "template.html"), encoding="utf8") as f:
    page = f.read()
fills = {
    "/*__DATA__*/": json.dumps(DATA, ensure_ascii=False, separators=(",", ":")),
    "/*__YEARS__*/": json.dumps(YEARS, ensure_ascii=False),
    "/*__AREASRC__*/": json.dumps(AREASRC, ensure_ascii=False),
    "/*__G20__*/": json.dumps(G20),
    "/*__FOCUS__*/": json.dumps(FOCUS),
    "/*__REGIONS__*/": json.dumps([regions["JZS"]], ensure_ascii=False),
    "<!--__REGIONSRC__-->": "\n    ".join(regions["sources"]),
    "/*__RMIN__*/": str(RAIL_MIN),
    "/*__RMAX__*/": str(RAIL_MAX),
    "__NAREA__": str(sum(1 for d in DATA if d["area"] is not None)),
    "__NOAREA__": str(sum(1 for d in DATA if d["area"] is None)),
    "__N__": str(len(DATA)),
    "<!--__FINDINGS__-->": findings.strip(),
    "<!--__JZSTEXT__-->": jzs_text.strip(),
    "<!--__RAILSRC__-->": "\n    ".join(rail.get("sources", [])),
}
for key, val in fills.items():
    assert key in page, f"placeholder {key} missing from template.html"
    page = page.replace(key, val)
with open(OUT, "w", encoding="utf8") as f:
    f.write(page)
print(f"{len(DATA)} economies, {sum(1 for d in DATA if d['area'] is not None)} with floor area -> beyond-gdp/index.html")
