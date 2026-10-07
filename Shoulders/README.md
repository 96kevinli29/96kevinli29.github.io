# 巨人之肩 · On Whose Shoulders

AI 在科学前沿的每一项突破都依靠人类的智慧与努力。本站随每一次 AI 科学突破持续更新，按学科分开。第 1 期（数学）记录 OpenAI 公开的 AI 数学预印本（[openai/math](https://github.com/openai/math)，Apache 2.0）引用了哪些人类数学家的工作，向人类的智力与工作致敬。

- 首页 / Home：https://96kevinli29.github.io/Shoulders/ （English: `/en/`）
- 数学 / Mathematics：https://96kevinli29.github.io/Shoulders/math/ （English: `/math/en/`）

## 目录结构

- `index.html`、`en/index.html`：总入口，由 `hub.py` 生成；新学科上线时在 `hub.py` 中加入卡片。
- `math/`：数学专题（页面与 `math/scripts/` 下的构建脚本）。之后每个学科一个目录，如 `physics/`。

页面包括：基石地图（AI 预印本按学科成"大陆"，被多篇共同引用的人类论文为节点）、被引最多的数学家（标注菲尔兹奖、阿贝尔奖、沃尔夫奖）、按领域的前 300 位排行、各国数学家、全部预印本与参考文献检索。

## 数据口径

- 参考文献从每篇预印本的 BibTeX 或 `\bibitem` 解析。排名可按三种计数切换：正文引用次数（默认，每处 `\cite` 计一次）、参考文献条目数、引用篇数。
- 正文原句从 LaTeX 源码的 `\cite` 位置截取，只为获奖者和少数学者抽取；"直接使用 / 背景 / 提及"为关键词启发式分类。
- 人名按"姓 + 名"合并；常见姓氏的缩写条目不强行合并。
- 国家/地区按出生地或原国籍标注（部分取成长地），覆盖按正文引用排名前 300 位中能查证的人与全部获奖者，可能有误。
- 中国数学家的工作单位见 `math/scripts/affil.txt`（2026 年 10 月核对，来源为学校主页与新闻）。
- 引用不等于依赖；本项目不评判 AI 结果的原创性。

## 更新记录

页面顶部的 Update 栏读取 `math/scripts/updates.txt`。本项目按学科分期更新，每期在文件顶部加一行（日期|中文|English）即可。

## 自动更新

仓库根目录的 `.github/workflows/shoulders.yml` 每天 03:23（UTC）拉取 openai/math 的源文件（不含 PDF），重跑全部脚本；只有引文数据变化时才提交新页面。也可以在 Actions 页面手动运行 “Rebuild Shoulders”。

## 本地重建

```bash
export OPENAI_MATH=/path/to/openai/math OUT_DIR=/path/to/Shoulders/math
cd Shoulders/math/scripts
for s in fields extract build_data contexts cites pack assemble; do python -I $s.py; done
```

新出现的数学家不会自动获得国家标签，需要在 `countries.txt` 中补充。
