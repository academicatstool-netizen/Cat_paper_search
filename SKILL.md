---
name: paper-search
description: >-
  Find academic papers and read them — searches real scholarly databases for
  prior work on a topic, then resolves and deep-reads the open-access PDF of any
  paper you pick. Use this skill WHENEVER the user wants to discover literature
  or read a study: "find recent papers on X", "what does the research say about
  Y", "find sources for my thesis on Z", "search for prior work on ...", or
  "summarise / read / extract the findings from this paper / this arXiv id /
  this DOI / this PDF". Trigger even when the tool isn't named. Results are real
  papers from public APIs (OpenAlex, Crossref, arXiv, Semantic Scholar, Europe
  PMC) and reading reports use only the actual extracted PDF text — nothing is
  fabricated.
---

# Paper Search

Two chained capabilities: **find papers**, then **deep-read** any one of them.
Both are grounded in real data — search hits come from public scholarly APIs,
and reading reports are built only from the extracted PDF text.

```
  search a topic ──▶ ranked real papers ──▶ deep-read the open-access ones
```

> **Running the scripts:** the commands below use paths relative to this skill's
> folder — run them from the skill directory, or prefix the full path to the
> script. If `python` isn't found, use `python3` (needs Python 3.8+).

## Capability 1 — Search

**When:** the user wants to find papers / prior work / sources on a topic, or
asks what the research says about something.

1. **Show the search setup first, and let the user choose.** Before searching,
   present this compact menu — with sensible defaults pre-filled from what they
   already said — then wait for their reply. It's plain text, so any model shows
   it the same way:

   > 🔍 **Search setup** — confirm or tweak, then I'll run it:
   > 1. **Topic** — `<topic inferred from the user's request>`
   > 2. **How many papers** — `20`  *(e.g. 10 / 20 / 40)*
   > 3. **Years** — `any`  *(e.g. 2020–2026)*
   > 4. **Open-access only** (only papers you can read in full) — `no`  *(yes / no)*
   > 5. **Sort by** — `best match`  *(best match / newest / most cited / open access)*
   >
   > Reply with any changes (e.g. *"30 papers, since 2021, open access"*), or just say **go**.

   Pre-fill any field the user already gave. If they clearly want speed ("just
   search", or they specified everything up front), skip the wait and run it.
   Map the choices to flags: how-many → `--limit`, years →
   `--from-year` / `--to-year`, open-access → `--open-access-only`, sort → your
   re-rank preference (step 5) plus `--open-access-only` for "open access".
2. For a focused query, search directly. For a broad/exploratory one, first
   expand it into directions and search the best 2–4 query strings (see
   `references/search.md`, Stages 1–3).
3. Run the retriever (5 keyless APIs in parallel — OpenAlex, Crossref, arXiv,
   Semantic Scholar, Europe PMC — deduped and rule-scored):

   ```bash
   python scripts/search_papers.py "your query" --limit 40 --compact
   #   --compact  : numbered one-line-per-paper list — USE THIS when the count is
   #                large (~25+) so the whole list is scannable and fully shown
   #   --markdown : richer cards (title + abstract + links) — good for smaller
   #                sets or when the user wants detail
   #   --brief    : plain table, for your own quick skim
   #   (omit all) : full JSON records with abstracts, for re-ranking / writing
   # filters:  --from-year 2021 --to-year 2026  --open-access-only
   # sources:  --sources openalex,crossref,arxiv,s2,europepmc
   ```
4. **Present the full numbered list.** Pick the format by size: **`--compact`**
   for large counts (the user's 200 → a clean 1…N list they can scan), or
   **`--markdown`** cards for smaller/detailed sets. Either way, **show the
   script's output as-is** — the script (not the model) produces the layout, so it
   is identical no matter which model runs the skill. A `--markdown` card looks
   like:

   > ### 1. [Paper title](https://doi.org/…)  ← title links to the original
   > Authors  ·  Year  ·  *Venue*  ·  cited by N  ·  via Source  ·  🟢 Open Access
   > > abstract snippet…
   > [📄 Open paper](url) · [⬇ PDF](pdf_url) · [🔗 DOI](https://doi.org/…)

   Every card carries **clickable links that jump straight to the original paper,
   its open-access PDF, and its DOI** — keep them intact.

   **Hard output rules (do not override these for "helpfulness"):**
   - **Show ALL N cards.** Paste the `--markdown` output in full, from card 1
     through the `— end of N results —` line. If the user asked for 200 and the
     databases returned 169, list all 169. Never stop early, never show only
     "highlights" or "the most representative", never collapse the rest into "…
     and more".
   - **One flat numbered list, 1…N.** Do NOT reorganise into themes, categories,
     sections, or sub-numbered buckets. Keep the script's single continuous
     `1, 2, 3 … N` numbering — that exact number is how the user refers back
     ("deep-read #3", "summarise #7, #12"), so it must be a flat sequence with no
     gaps or restarts.
   - **Don't shorten cards.** Keep each card's metadata + links. You may add at
     most a one-line "why" under a card.
   - A long reply is expected when the count is large — that is what the user
     asked for. You may add ONE line *after* the full list offering to narrow,
     group, or deep-read a number — never *instead of* the full list.
5. **Ordering, not culling.** "Re-rank by fit" means choosing the *order*, never
   removing papers. Apply the user's **Sort** choice by reordering the whole set,
   then number it 1…N (see `references/search.md` for fit criteria; `rule_score`
   is only a prior). Drop papers ONLY if the user explicitly asked to filter
   (e.g. "open access only", "exclude reviews"); otherwise keep all N. Papers with
   a `pdf_url` are open-access and can be deep-read by number next.

The script auto-retries Semantic Scholar on rate-limit (HTTP 429), which clears
most skips. If `s2` still gets skipped a lot, set a free key —
`export S2_API_KEY=...` (from semanticscholar.org/product/api) — and it stops
429-ing. Any skipped source is reported on stderr and the rest carry the search.
Full pipeline in `references/search.md`.

## Capability 2 — Deep Read

**When:** the user wants to actually read, summarise, or extract findings from a
specific paper (by title, DOI, arXiv id, or URL) — including one they just found
in a search.

1. Resolve and extract the PDF (tries direct URL → arXiv-by-DOI → Unpaywall →
   OpenAlex → Semantic Scholar):

   ```bash
   python scripts/fetch_pdf.py --doi 10.1145/3313831.3376234 --text-only
   python scripts/fetch_pdf.py --arxiv 1706.03762 --text-only
   python scripts/fetch_pdf.py --pdf-url https://.../paper.pdf
   python scripts/fetch_pdf.py --title "Attention is all you need"
   # --text-only prints just the extracted text; drop it for full JSON
   #   (per-page array + resolved URL + which sources were tried)
   # reads the first ~12 pages by default; for a long paper's results section
   # raise it, e.g. --max-pages 20 --max-chars 60000   (--email for Unpaywall)
   ```
2. If `resolved_pdf_url` is null, the paper is paywalled with no free copy — say
   so plainly and offer to try another identifier or work from the abstract.
   **Never fabricate the contents.**
3. Produce the evidence-aware reading report using the prompt in
   `references/deep_read.md`, from the extracted text **only**. If extraction was
   `truncated`, disclose that the report covers just the analysed excerpt. You
   can also extract typed claims to hand off to a writing task.

## Setup

```bash
python -m pip install -r scripts/requirements.txt   # only pypdf, for deep read
```
Search needs nothing beyond the Python 3.8+ standard library; all sources are
keyless. If `python` isn't found, use `python3`. Set `UNPAYWALL_EMAIL=you@domain`
(or pass `--email`) to be polite to Unpaywall and slightly improve OA hit-rate.

## Honesty contract

Search results are real papers, not invented. Deep-read reports use only the
extracted PDF text; gaps are disclosed, not filled with guesses. When a PDF is
paywalled or an abstract is too thin to support a claim, say so rather than
fabricating — that candor is the point.
