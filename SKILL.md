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

1. For a focused query, search directly. For a broad/exploratory one, first
   expand it into directions and search the best 2–4 query strings (see
   `references/search.md`, Stages 1–3).
2. Run the retriever (5 keyless APIs in parallel — OpenAlex, Crossref, arXiv,
   Semantic Scholar, Europe PMC — deduped and rule-scored):

   ```bash
   python scripts/search_papers.py "your query" --limit 40 --brief
   # full JSON (with abstracts): drop --brief
   # to restrict years:   --from-year 2021 --to-year 2026
   # open-access only:     --open-access-only
   # pick sources:         --sources openalex,crossref,arxiv,s2,europepmc
   ```
   Use `--brief` for a skimmable ranked table; drop it to get the full JSON
   records (with abstracts) when you need to re-rank or write from them.
3. **Re-rank by research fit, not keyword overlap.** `rule_score` is only a
   keyword/recency/citation prior — the genuinely best-fit paper is often NOT
   `papers[0]`. Apply the research-fit and adversarial-screening criteria in
   `references/search.md`, drop off-target hits, and present a ranked list with a
   one-line "why" per paper. Papers with a `pdf_url` are open-access and can be
   deep-read next.

`s2` may rate-limit (HTTP 429) without a key and `arxiv` can be slow — fine, the
script reports skipped sources on stderr and the rest carry the search. Full
pipeline in `references/search.md`.

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
