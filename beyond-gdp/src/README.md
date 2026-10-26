# GDP 之外 / Beyond GDP：生成页面的脚本和数据

`../index.html`（中文，https://seafill.info/beyond-gdp/）和 `../en/index.html`（英文，https://seafill.info/beyond-gdp/en/）都由这里的脚本生成，不要直接改它们。只需要 Python 3，不用装任何第三方包。

## 文件

| 文件 | 作用 |
|---|---|
| `fetch.py` | 下载原始数据到 `raw/`（世界银行、Our World in Data、维基百科）。`raw/` 不进 git。 |
| `build_data.py` | 选出经济体，合并各项指标，写出 `data/indicators.json`。 |
| `build_page.py` | 把模板、`style.css`、`app.js` 和 `data/` 里的文件合成中英文两个页面（样式和脚本内联进页面）。 |
| `names.py` | 中英文名、名称别名、欧盟成员、单独列出的欧盟成员、排除的小地区、G20 和富国名单。 |
| `template_zh.html`, `template_en.html` | 中英文页面模板：正文、八个维度的定义（`DIMS`，含默认权重）和脚本里显示的文字（`L`）。改正文或权重时，两个模板要一起改。 |
| `style.css` | 两个页面共用的样式，包括图表配色（八个维度用经过色盲检验的 8 色分类色板，浅色和深色模式各一套）。 |
| `app.js` | 两个页面共用的计分和画图代码：计分区间、排名、斜线图、散点图、条形图、表格。改计分区间只改这里。 |
| `data/indicators.json` | `build_data.py` 的输出快照，提交到 git，没有 `raw/` 也能重建页面。 |
| `data/area.json` | 人均住房面积，手工逐国整理（数值、年份、口径、来源链接）。 |
| `data/rail.json` | 高铁人公里、轻轨和有轨电车客运人次、中国城市轨道交通人公里，手工整理。 |
| `data/night_safety.json` | 盖洛普 2024 年“晚上独自走路感到安全”的比例，从 Global Safety Report 2025 的表格里摘录。 |
| `data/regions.json` | 江浙沪（三省市合并）的地区数据，手工整理，作为参照显示在各图表和“江浙沪”一节里。 |
| `data/jzs_zh.html`, `data/jzs_en.html` | “江浙沪”一节表格下面的解读文字，手写。 |
| `data/findings_zh.html`, `data/findings_en.html` | 散点图下面的结论文字，手写。 |

## 常见操作

只改文字、权重或计分区间（不更新数据）：

```bash
# 编辑模板或 data/ 里的文字之后
python3 build_page.py
```

更新全部数据：

```bash
python3 fetch.py        # 下载最新原始数据，几分钟
python3 build_data.py   # 打印缺数据的经济体
python3 build_page.py
```

更新数据后排名会变，记得核对 `data/findings_*.html`、`data/jzs_*.html` 和模板正文里写死的名次和数字。

## 选取规则

- 2025 年人均 GDP（PPP）前 100 名，加上 GDP 总量（现价美元）前 50 名；没有 2025 年数据的用最新一年。
- 欧盟 27 国合并成“欧盟”；G20 成员法国、德国、意大利另外单独列出（`names.py` 里的 `MEMBERS_SHOWN`）。
- `names.py` 里的 `EXCLUDE` 是缺两项以上数据的 13 个小地区。
- 有新经济体进入名单时，`build_data.py` 会提示在 `names.py` 的 `ZH` 里补中文名。

## 计分

八个维度，默认权重（模板里的 `DIMS`）：用电、住房、健康各 15，饮食、出行、教育、安全各 12.5，联网 5，合计 100。计分区间在 `app.js` 的 `dimScores`。某个经济体缺某一维度时，用 G20 和欧盟中有数据经济体在这一维度的平均分代替。
