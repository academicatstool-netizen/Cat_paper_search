<div align="center">

**English** · [中文](README.zh-CN.md)

<img src="assets/cover.png" alt="AcademiCats · Paper Search" width="100%">

<br>

# 🐱 Paper Search

**Find real academic papers across the world's scholarly databases — then read any open-access one in depth. Grounded in real data, never fabricated.**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-0064F4.svg)](LICENSE)
&nbsp;[![Runs on Claude](https://img.shields.io/badge/runs%20on-Claude-0064F4.svg)](https://claude.com/claude-code)
&nbsp;[![Full product](https://img.shields.io/badge/full%20product-academicats.com-0064F4.svg)](https://academicats.com)

</div>

---

> ### 🪶 This is the **lite, open-source edition** of [**AcademiCats**](https://academicats.com)
> The full product at **[academicats.com](https://academicats.com)** is an AI research workbench that takes you from *finding* papers all the way through *reading, writing, and self-review* — with Google Scholar breadth, Chinese-language sources, saved libraries, a polished UI, and a multi-agent reviewer. This skill is a free, self-contained slice of that workflow you can run on your own Claude.

---

## ✨ What it does

🔍 **Search that means it** — one question fans out across five scholarly databases (OpenAlex, Crossref, arXiv, Semantic Scholar, Europe PMC), de-duplicates, and ranks by genuine research fit — not just keyword overlap.

📄 **Read, not skim** — pick any open-access paper and it resolves the PDF, extracts the text, and gives you a structured, page-anchored reading: the research question, method, key findings, and limitations.

🛡️ **No made-up papers, no made-up findings** — every result is a real record from a public API, and every reading is built only from the actual extracted text. When a paper is paywalled, it says so — it never invents the contents.

<br>

## 🎬 Demo

Ask in plain language:

> *"Find me papers on CRISPR off-target effects."*

First it shows a quick **search setup** so you stay in control — same on any model:

> 🔍 **Search setup** — confirm or tweak, then I'll run it:
> 1. **Topic** — CRISPR off-target effects
> 2. **How many papers** — 20  *(10 / 20 / 40)*
> 3. **Years** — any  *(e.g. 2020–2026)*
> 4. **Open-access only** — no  *(yes / no)*
> 5. **Sort by** — best match  *(best match / newest / most cited / open access)*
>
> Reply with any changes, or just say **go**.

Then it runs a real search and hands back **result cards** — each with full details and links that jump straight to the paper. The cards look the same no matter which model runs the skill, because the format is fixed by the tool, not improvised:

---

**1. [Off-target effects in CRISPR/Cas9 gene editing](https://doi.org/10.3389/fbioe.2023.1143157)**
Congting Guo, Xiaoteng Ma, Fei Gao, Yuxuan Guo · 2023 · *Frontiers in Bioengineering and Biotechnology* · cited by 537 · 🟢 Open Access

> Gene editing stands for the methods to precisely make changes to a specific nucleic acid sequence. With the recent development of the CRISPR/Cas9 system, gene editing has become efficient, convenient and programmable…

[📄 Open paper](https://doi.org/10.3389/fbioe.2023.1143157) · [⬇ PDF](https://www.frontiersin.org/articles/10.3389/fbioe.2023.1143157/pdf) · [🔗 DOI](https://doi.org/10.3389/fbioe.2023.1143157)

---

…then it opens the open-access PDF and reads it back to you with findings tied to page numbers — grounded entirely in the paper's own text.

<br>

## 🚀 Get started in 60 seconds

```bash
# 1. install into Claude Code's skills folder
mkdir -p ~/.claude/skills
git clone https://github.com/jy1529098645-gif/Cat_paper_search.git ~/.claude/skills/paper-search

# 2. install the one dependency (Python 3.8+, for reading PDFs)
cd ~/.claude/skills/paper-search && python -m pip install -r scripts/requirements.txt
```

Restart Claude Code so it loads the skill. From then on, just talk to Claude — *"find recent papers on …"*, *"summarise this arXiv paper …"* — and it triggers itself. Everything runs on your own Claude; all data sources are free and need no API keys.

<br>

## 💙 Why people like it

|  | Paper Search (this skill) | [AcademiCats full product →](https://academicats.com) |
|---|:---:|:---:|
| Real papers, honest reading | ✅ | ✅ |
| Scholarly databases | 5 (key-free) | 14+ incl. Google Scholar & Chinese sources |
| Saved libraries & history | — | ✅ |
| Write & self-review from your sources | — | ✅ Synthesis Lab + Paper Review |
| Polished web & mobile app | — | ✅ |

## 🐱 The AcademiCats skill family

Three open skills that chain into one research workflow — install any or all:

- 🔍 **Paper Search** *(you are here)* — find & read papers
- ✍️ [Synthesis Lab](https://github.com/jy1529098645-gif/Cat_synthesis_lab) — write grounded papers from your sources
- 🧪 [Paper Review](https://github.com/jy1529098645-gif/Cat_paper_review) — peer-review your own draft

**Install all three at once** — clone any one repo, then run `bash install.sh`.

## 🙋 FAQ

- **It didn't trigger?** Restart Claude Code after installing, and phrase your message as a task — *"find recent papers on …"*.
- **A paper won't open?** It's paywalled with no free copy — the skill says so instead of guessing. Try another result, or paste a DOI / PDF link.
- **Why fewer than 5 databases sometimes?** Semantic Scholar rate-limits key-free traffic. It auto-retries, and the other 4 databases carry the search — or grab a free [S2 API key](https://www.semanticscholar.org/product/api) and `export S2_API_KEY=...` to always include it.
- **Which model?** Any model works; quality is best on Claude Sonnet or above.
- **Private & free?** It runs on your own Claude — no account, nothing sent to us. Searches only hit public scholarly APIs.

<div align="center">
<br>

### Want the whole research workflow?
**→ [academicats.com](https://academicats.com) ←**

<br>

Made with 💙 by the [AcademiCats](https://academicats.com) team · [MIT License](LICENSE)

</div>
