<div align="center">

**English** · [中文](README.zh-CN.md)

<img src="assets/cover.png" alt="AcademiCats · Paper Search" width="100%">

<br>

# 🐱 Paper Search

**Find real academic papers across the world's scholarly databases — then read any open-access one in depth. Grounded in real data, never fabricated.**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-0064F4.svg)](LICENSE)
&nbsp;[![Claude](https://img.shields.io/badge/Claude-0064F4.svg)](https://claude.com/claude-code)
&nbsp;[![ChatGPT](https://img.shields.io/badge/ChatGPT-0064F4.svg)](https://chatgpt.com)
&nbsp;[![DeepSeek](https://img.shields.io/badge/DeepSeek-0064F4.svg)](https://chat.deepseek.com)
&nbsp;[![Full product](https://img.shields.io/badge/full%20product-academicats.com-0064F4.svg)](https://academicats.com)

</div>

---

> ### 🪶 This is the **lite, open-source edition** of [**AcademiCats**](https://academicats.com) — now in free open beta
> The full product at **[academicats.com](https://academicats.com)** is an AI research workbench that takes you from *finding* papers all the way through *reading, writing, and self-review* — with Google Scholar breadth, Chinese-language sources, saved libraries, a polished UI, and a multi-agent reviewer. This skill is a free, self-contained slice of that workflow you can run on your own AI — Claude, ChatGPT, or DeepSeek.

---

## ✨ What it does

🔍 **Search that means it** — one question searches five scholarly databases at once (OpenAlex, Crossref, arXiv, Semantic Scholar, Europe PMC), de-duplicates, and ranks by genuine research fit — not just keyword overlap.

📄 **Read, not skim** — pick any open-access paper and it resolves the PDF, extracts the text, and gives you a structured reading — research question, method, key findings, and limitations — with page references where the source supports them.

🛡️ **No made-up papers, no made-up findings** — every result is a real record from a public API, and every reading is built only from the actual extracted text. When a paper is paywalled, it says so — it never invents the contents.

<br>

## 🎬 Demo

Say it in one line — the topic, plus any options inline:

> *"Find 20 papers on CRISPR off-target effects since 2020."*

It runs right away — no forms, no back-and-forth — and returns a **numbered list of every result**, one scannable line each, so you can act on any of them by number. The format is fixed by the tool, identical no matter which model runs the skill:

> ## 🔎 5 results for: CRISPR off-target effects
> 1. **[Off-target effects in CRISPR/Cas9 gene editing](https://doi.org/10.3389/fbioe.2023.1143157)** — Congting Guo et al. · 2023 · cited 537 · 🟢 · [PDF](https://www.frontiersin.org/articles/10.3389/fbioe.2023.1143157/pdf)
> 2. **[Latest Developed Strategies to Minimize Off-Target Effects in CRISPR-Cas Genome Editing](https://doi.org/10.3390/cells9071608)** — Naeem et al. · 2020 · cited 451 · 🟢 · [PDF](https://www.mdpi.com/2073-4409/9/7/1608/pdf)
> 3. **[CRISPR/Cas Systems in Genome Editing: sgRNA Design & Off‑Target Evaluation](https://doi.org/10.1002/advs.201902312)** — Manghwar et al. · 2020 · cited 357 · 🟢 · [PDF](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/advs.201902312)
> 4. **[CRISPR/Cas13 effectors have differing off-target effects in eukaryotic cells](https://doi.org/10.1093/nar/gkac159)** — Ai et al. · 2022 · cited 151 · 🔒
> 5. **[Beyond the promise: evaluating & mitigating off-target effects for safer therapeutics](https://doi.org/10.3389/fbioe.2023.1339189)** — Lopes et al. · 2024 · cited 62 · 🟢

Every title links straight to the paper; 🟢 means a free PDF you can read in full. Then just say **"deep-read #1"** — it opens that paper's PDF and reads it back to you with findings tied to page numbers, grounded entirely in the paper's own text.

> Every search also saves the **complete list** (all results, with abstracts) to a `search-results.md` file — so the full set is always captured, never cut off.

<br>

## 🚀 Get started — pick your platform

Pick whichever AI you use; each setup takes under a minute.

**🖥️ Claude Code** — runs locally, triggers itself (full-power version)
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/jy1529098645-gif/Cat_paper_search.git ~/.claude/skills/paper-search
python -m pip install -r ~/.claude/skills/paper-search/scripts/requirements.txt   # for reading PDFs
```
Restart Claude Code, then just ask — *"find recent papers on …"*, *"summarise this arXiv paper …"*

**🌐 Claude (web / desktop app)** — download **[`paper-search.skill`](paper-search.skill)**, then upload it under **Settings → Capabilities → Skills**. (Its search & PDF scripts run in Claude's built-in code sandbox.)

**🤖 ChatGPT** — open **[`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)**, paste it into a **Custom GPT**'s *Instructions* (or first message), and **turn on web browsing**. Then ask.

**💬 DeepSeek / any other model** — paste **[`PORTABLE_PROMPT.md`](PORTABLE_PROMPT.md)** as the **system prompt**, with web access enabled. Then ask.

> ⚠️ **Web access needed on ChatGPT/DeepSeek** — search runs via web browsing instead of the Python scripts, so turn browsing on. Coverage is lighter than the Claude version, but every result stays real (it says so rather than invent when offline). For the full-power experience, use the Claude Code path (or any agent that can run Python with internet, e.g. Cursor).

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

Three open skills that chain into one research workflow — install any or all:

- 🔍 **Paper Search** *(you are here)* — find & read papers
- ✍️ [Synthesis Lab](https://github.com/jy1529098645-gif/Cat_synthesis_lab) — write grounded papers from your sources
- 🧪 [Paper Review](https://github.com/jy1529098645-gif/Cat_paper_review) — peer-review your own draft

**Install all three at once** — clone any one repo, then run `bash install.sh`.

## 🙋 FAQ

- **What are all these files?** Use just one path above — a git clone (Claude Code), the `.skill` file (Claude web/desktop), or `PORTABLE_PROMPT.md` (ChatGPT/DeepSeek). `SKILL.md`, `references/`, and `scripts/` are internals your assistant loads and runs for you — no need to open them.
- **It didn't trigger?** Restart Claude Code after installing, and phrase your message as a task — *"find recent papers on …"*.
- **A paper won't open?** It's paywalled with no free copy — the skill says so instead of guessing. Try another result, or paste a DOI / PDF link.
- **Why fewer than 5 databases sometimes?** Semantic Scholar rate-limits key-free traffic. It auto-retries, and the other 4 databases carry the search — or grab a free [S2 API key](https://www.semanticscholar.org/product/api) and `export S2_API_KEY=...` to always include it.
- **Which model?** Any strong model works — Claude Sonnet/Opus, GPT‑4o/o‑series, or DeepSeek‑V3/R1 give the best results.
- **Private & free?** It runs on your own AI — no account, nothing sent to us. Searches only hit public scholarly APIs.

<div align="center">
<br>

### Want the whole research workflow?
**→ [academicats.com](https://academicats.com) ←**

*🚀 The full product is in **open beta** — free to try right now.*

<br>

Made with 💙 by the [AcademiCats](https://academicats.com) team · [MIT License](LICENSE)

</div>
