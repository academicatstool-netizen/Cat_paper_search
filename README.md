<div align="center">

**English** · [中文](README.zh-CN.md)

<img src="assets/cover.png" alt="AcademiCats · Paper Search" width="100%">

<br>

# 🐱 Paper Search

**Find real academic papers across the world's scholarly databases — then read any open-access one in depth. Grounded in real data, never fabricated.**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-0064F4.svg)](LICENSE)
&nbsp;[![Claude](https://img.shields.io/badge/Claude-0064F4.svg)](https://claude.com/claude-code)
&nbsp;[![Codex](https://img.shields.io/badge/Codex-0064F4.svg)](https://github.com/openai/codex)
&nbsp;[![Full product](https://img.shields.io/badge/full%20product-academicats.com-0064F4.svg)](https://academicats.com)

</div>

---

> ### 🪶 This is the **lite, open-source edition** of [**AcademiCats**](https://academicats.com) — now in free open beta
> The full product at **[academicats.com](https://academicats.com)** is an AI research workbench that takes you from *finding* papers all the way through *reading, writing, and self-review* — with Google Scholar breadth, Chinese-language sources, saved libraries, a polished UI, and a multi-agent reviewer. This skill is a free, self-contained slice of that workflow you can run on your own AI — Claude or Codex.

---

## ✨ What it does

🔍 **Search that means it** — one question searches five scholarly databases at once (OpenAlex, Crossref, arXiv, Semantic Scholar, Europe PMC), de-duplicates, and ranks by genuine research fit — not just keyword overlap.

📄 **Read, not skim** — pick any open-access paper and it resolves the PDF, extracts the text, and gives you a structured reading — research question, method, key findings, and limitations — with page references where the source supports them.

🛡️ **No made-up papers, no made-up findings** — every result is a real record from a public API, and every reading is built only from the actual extracted text. When a paper is paywalled, it says so — it never invents the contents.

<br>

## 🎬 Demo

<div align="center">
<img src="assets/paperSearch_large.gif" alt="Paper Search in action" width="100%">
</div>

Say it in one line — the topic, plus any options inline:

> *"Find 200 papers on XR experience."*

It runs right away — no forms, no back-and-forth — and returns a **numbered list of every result**, one scannable line each, so you can act on any of them by number. The format is fixed by the tool, identical no matter which model runs the skill:

> ## 🔎 5 results for: XR experience
> 1. **[PLUME: Record, Replay, Analyze and Share User Behavior in 6DoF XR Experiences](https://doi.org/10.1109/tvcg.2024.3372107)** — Charles Javerliat et al. · 2024 · cited 23 · 🟢 · [PDF](https://hal.science/hal-04488824v1/file/PlumeIEEEVR%281%29.pdf)
> 2. **[A bibliometric analysis of immersive technology in museum exhibitions: exploring user experience](https://doi.org/10.3389/frvir.2023.1240562)** — Jingjing Li et al. · 2023 · cited 92 · 🟢 · [PDF](https://www.frontiersin.org/articles/10.3389/frvir.2023.1240562/pdf)
> 3. **[Two sides of the same coin: accessibility practices and neurodivergent users' experience of extended reality](https://doi.org/10.1108/jet-03-2022-0025)** — Tamari Lukava et al. · 2022 · cited 40 · 🟢 · [PDF](https://discovery.ucl.ac.uk/10150777/1/Two%20sides%20of%20the%20same%20coin_revision_clean.pdf)
> 4. **[A framework study on the use of immersive XR technologies in the cultural heritage domain](https://doi.org/10.1016/j.culher.2023.06.001)** — Chiara Innocente et al. · 2023 · cited 144 · 🔒
> 5. **[Wayfinding in Virtual Reality Serious Game: An Exploratory Study in the Context of User Perceived Experiences](https://doi.org/10.3390/app11177822)** — Shafaq Irshad et al. · 2021 · cited 27 · 🟢 · [PDF](https://www.mdpi.com/2076-3417/11/17/7822/pdf?version=1630052587)

Every title links straight to the paper; 🟢 means a free PDF you can read in full. Then just say **"deep-read #1"** — it opens that paper's PDF and reads it back to you with findings tied to page numbers, grounded entirely in the paper's own text.

> Every search also saves the **complete list** (all results, with abstracts) to a `search-results.md` file — so the full set is always captured, never cut off.

<br>

## 🚀 Get started — pick your platform

Pick whichever AI you use; each setup takes under a minute.

**🖥️ Claude Code** — runs locally, triggers itself (full-power version)
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/academicatstool-netizen/Cat_paper_search.git ~/.claude/skills/paper-search
python -m pip install -r ~/.claude/skills/paper-search/scripts/requirements.txt   # for reading PDFs
```
Restart Claude Code, then just ask — *"find recent papers on …"*, *"summarise this arXiv paper …"*

**🌐 Claude (web / desktop app)** — download **[`paper-search.skill`](paper-search.skill)**, then upload it under **Settings → Capabilities → Skills**. (Its search & PDF scripts run in Claude's built-in code sandbox.)

**💻 Codex / any coding agent** — clone the repo into your project and let the agent run the Python scripts directly — the same full-power path as Claude Code (real APIs, deep-read PDFs), no browsing needed.

**💬 Any other model** — paste **[`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)** as the **system prompt**, with web access enabled. Then ask.

> ⚠️ **Browsing models need web access** — on a browsing-only model (no Python), search runs via web browsing instead of the scripts, so turn browsing on. Coverage is lighter, but every result stays real (it says so rather than invent when offline). For the full-power experience use **Claude Code or Codex** (or any agent that can run Python with internet, e.g. Cursor).

<br>

## 💙 Why people like it

|  | Paper Search (this skill) | [AcademiCats full product →](https://academicats.com) |
|---|:---:|:---:|
| ⚡ **Speed** | minutes (runs live on your model) | **seconds** — tuned pipeline + caching |
| Real papers, honest reading | ✅ | ✅ |
| Scholarly databases | 5 (key-free) | 14+ incl. Google Scholar & Chinese sources |
| Saved libraries & history | — | ✅ |
| Write & self-review from your sources | — | ✅ Synthesis Lab + Paper Review |
| Polished web & mobile app | — | ✅ |

## 🐱 The AcademiCats skill family

Four open skills that chain into one research workflow — install any or all:

- 🧭 [Find Angles](https://github.com/academicatstool-netizen/Cat_find_angles) — turn a topic into research directions
- 🔍 **Paper Search** *(you are here)* — find & read papers
- ✍️ [Synthesis Lab](https://github.com/academicatstool-netizen/Cat_synthesis_lab) — write grounded papers from your sources
- 🧪 [Paper Review](https://github.com/academicatstool-netizen/Cat_paper_review) — peer-review your own draft

**Install all at once** — clone any one repo, then run `bash install.sh`.

## 🙋 FAQ

- **What are all these files?** Use just one path above — a git clone (Claude Code), the `.skill` file (Claude web/desktop), or `PORTABLE_PROMPT.md` (any other model). `SKILL.md`, `references/`, and `scripts/` are internals your assistant loads and runs for you — no need to open them.
- **It didn't trigger?** Restart Claude Code after installing, and phrase your message as a task — *"find recent papers on …"*.
- **A paper won't open?** It's paywalled with no free copy — the skill says so instead of guessing. Try another result, or paste a DOI / PDF link.
- **Why fewer than 5 databases sometimes?** Semantic Scholar rate-limits key-free traffic. It auto-retries, and the other 4 databases carry the search — or grab a free [S2 API key](https://www.semanticscholar.org/product/api) and `export S2_API_KEY=...` to always include it.
- **Which model or agent?** Claude (Sonnet/Opus) via Claude Code or Codex give the best results — any other capable model can run the portable prompt.
- **Private & free?** It runs on your own AI — no account, nothing sent to us. Searches only hit public scholarly APIs.

<div align="center">
<br>

### Want the whole research workflow?
**→ [academicats.com](https://academicats.com) ←**

*🚀 The full product is in **open beta** — free to try right now.*

<br>

Made with 💙 by the [AcademiCats](https://academicats.com) team · [MIT License](LICENSE)

</div>
