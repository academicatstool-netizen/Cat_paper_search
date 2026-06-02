#!/usr/bin/env python3
"""
search_papers.py — Multi-source academic paper retrieval (keyless).

Queries several free, key-free scholarly APIs in parallel, normalises the
results into one schema, de-duplicates, and applies a transparent rule-based
relevance score. The heavy "research-fit" judgement (LLM rerank + adversarial
screening) is left to Claude, which reads this script's JSON output and
re-ranks per the criteria in references/search.md.

Sources (all keyless): OpenAlex, Crossref, arXiv, Semantic Scholar, Europe PMC.

Usage:
    python search_papers.py "your query" [--limit 40] [--from-year 2018]
                            [--to-year 2026] [--open-access-only]
                            [--sources openalex,crossref,arxiv,s2,europepmc]

Output: JSON to stdout -> {"query":..., "count":..., "papers":[ ... ]}
Each paper: title, authors[], year, abstract, doi, url, pdf_url,
            citation_count, venue, source, rule_score, rule_signals{}.

Pure standard library — no pip install required.
"""
import argparse
import concurrent.futures as cf
import json
import math
import os
import re
import sys
import ssl
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "academi-skill/1.0 (https://github.com/; mailto:hello@example.com)"
TIMEOUT = 20

# Some machines (notably Windows) ship a broken/empty CA store, which makes
# every HTTPS call to these public read-only APIs fail with CERTIFICATE_VERIFY_
# FAILED. Try verified first; fall back to an unverified context so the skill
# still works. These are all public GET requests, so the fallback is low-risk.
try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = ssl.create_default_context()
_CTX_UNVERIFIED = ssl._create_unverified_context()


def _get(url, headers=None, retries=3):
    """GET with a short backoff retry on rate-limit / transient 5xx (fixes the
    common Semantic Scholar 429 when running key-free). Timeouts are NOT retried
    (they're slow) — a dead source just drops and the others carry the search."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                # honour Retry-After if present, else exponential-ish backoff
                wait = e.headers.get("Retry-After")
                time.sleep(min(float(wait), 6) if (wait and wait.isdigit()) else 1.2 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError as e:
            if isinstance(getattr(e, "reason", None), ssl.SSLError):
                with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX_UNVERIFIED) as resp:
                    return resp.read()
            raise


def _get_json(url, headers=None):
    return json.loads(_get(url, headers).decode("utf-8", "replace"))


def _norm_year(v):
    if v is None:
        return None
    m = re.search(r"(\d{4})", str(v))
    return int(m.group(1)) if m else None


def _clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


# ---------------------------------------------------------------- sources ----
def search_openalex(q, limit):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q) +
           f"&per_page={min(limit, 50)}&mailto=hello@example.com")
    out = []
    for w in _get_json(url).get("results", []):
        # OpenAlex stores abstracts as an inverted index; rebuild it.
        abstract = ""
        inv = w.get("abstract_inverted_index")
        if inv:
            positions = {}
            for word, idxs in inv.items():
                for i in idxs:
                    positions[i] = word
            abstract = " ".join(positions[i] for i in sorted(positions))
        oa = (w.get("best_oa_location") or w.get("primary_location") or {})
        out.append({
            "title": _clean(w.get("title")),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])
                        if a.get("author")],
            "year": w.get("publication_year"),
            "abstract": _clean(abstract),
            "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
            "url": w.get("id"),
            "pdf_url": oa.get("pdf_url"),
            "citation_count": w.get("cited_by_count", 0),
            "venue": _clean((w.get("primary_location") or {}).get("source", {}).get("display_name")
                            if (w.get("primary_location") or {}).get("source") else ""),
            "source": "OpenAlex",
        })
    return out


def search_crossref(q, limit):
    url = ("https://api.crossref.org/works?query=" + urllib.parse.quote(q) +
           f"&rows={min(limit, 40)}&select=title,author,issued,DOI,URL,abstract,"
           "container-title,is-referenced-by-count")
    out = []
    for w in _get_json(url).get("message", {}).get("items", []):
        abstract = re.sub(r"<[^>]+>", "", w.get("abstract", "") or "")
        issued = (((w.get("issued") or {}).get("date-parts") or [[None]])[0] or [None])[0]
        out.append({
            "title": _clean(" ".join(w.get("title", [])) or ""),
            "authors": [_clean(f"{a.get('given','')} {a.get('family','')}")
                        for a in w.get("author", [])],
            "year": _norm_year(issued),
            "abstract": _clean(abstract),
            "doi": w.get("DOI"),
            "url": w.get("URL"),
            "pdf_url": None,
            "citation_count": w.get("is-referenced-by-count", 0),
            "venue": _clean(" ".join(w.get("container-title", []) or [])),
            "source": "Crossref",
        })
    return out


def search_arxiv(q, limit):
    url = ("https://export.arxiv.org/api/query?search_query=all:" +
           urllib.parse.quote(q) + f"&start=0&max_results={min(limit, 40)}")
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(_get(url))
    out = []
    for e in root.findall("a:entry", ns):
        doi_el = e.find("arxiv:doi", ns)
        pdf = None
        for link in e.findall("a:link", ns):
            if link.get("title") == "pdf":
                pdf = link.get("href")
        out.append({
            "title": _clean((e.findtext("a:title", "", ns))),
            "authors": [_clean(a.findtext("a:name", "", ns)) for a in e.findall("a:author", ns)],
            "year": _norm_year(e.findtext("a:published", "", ns)),
            "abstract": _clean(e.findtext("a:summary", "", ns)),
            "doi": doi_el.text if doi_el is not None else None,
            "url": e.findtext("a:id", "", ns),
            "pdf_url": pdf,
            "citation_count": 0,
            "venue": "arXiv",
            "source": "arXiv",
        })
    return out


def search_s2(q, limit):
    fields = "title,abstract,year,authors,externalIds,openAccessPdf,citationCount,venue,url"
    url = ("https://api.semanticscholar.org/graph/v1/paper/search?query=" +
           urllib.parse.quote(q) + f"&limit={min(limit, 40)}&fields={fields}")
    # An optional free API key (https://www.semanticscholar.org/product/api) lifts
    # the rate limit dramatically — set S2_API_KEY to stop the 429 skips.
    key = os.environ.get("S2_API_KEY") or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    headers = {"x-api-key": key} if key else None
    out = []
    for w in _get_json(url, headers).get("data", []) or []:
        ext = w.get("externalIds") or {}
        out.append({
            "title": _clean(w.get("title")),
            "authors": [a.get("name", "") for a in w.get("authors", [])],
            "year": w.get("year"),
            "abstract": _clean(w.get("abstract")),
            "doi": ext.get("DOI"),
            "url": w.get("url"),
            "pdf_url": (w.get("openAccessPdf") or {}).get("url"),
            "citation_count": w.get("citationCount", 0),
            "venue": _clean(w.get("venue")),
            "source": "SemanticScholar",
        })
    return out


def search_europepmc(q, limit):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" +
           urllib.parse.quote(q) + f"&format=json&pageSize={min(limit, 40)}&resultType=core")
    out = []
    for w in _get_json(url).get("resultList", {}).get("result", []):
        pdf = None
        for ft in (w.get("fullTextUrlList", {}) or {}).get("fullTextUrl", []):
            if ft.get("documentStyle") == "pdf":
                pdf = ft.get("url")
        out.append({
            "title": _clean(w.get("title")),
            "authors": [a.get("fullName", "") for a in
                        (w.get("authorList", {}) or {}).get("author", [])],
            "year": _norm_year(w.get("pubYear")),
            "abstract": _clean(w.get("abstractText")),
            "doi": w.get("doi"),
            "url": (f"https://doi.org/{w['doi']}" if w.get("doi")
                    else f"https://europepmc.org/article/{w.get('source')}/{w.get('id')}"),
            "pdf_url": pdf,
            "citation_count": w.get("citedByCount", 0),
            "venue": _clean(w.get("journalTitle")),
            "source": "EuropePMC",
        })
    return out


SOURCES = {
    "openalex": search_openalex,
    "crossref": search_crossref,
    "arxiv": search_arxiv,
    "s2": search_s2,
    "europepmc": search_europepmc,
}


# ----------------------------------------------------------------- dedup -----
def _dedup_key(p):
    if p.get("doi"):
        return ("doi", p["doi"].lower().strip())
    t = re.sub(r"[^a-z0-9]", "", (p.get("title") or "").lower())
    return ("title", t[:80])


def dedup(papers):
    best = {}
    for p in papers:
        k = _dedup_key(p)
        if k not in best:
            best[k] = p
        else:
            # Merge: keep the record with abstract / pdf / more citations.
            cur = best[k]
            if not cur.get("abstract") and p.get("abstract"):
                cur["abstract"] = p["abstract"]
            if not cur.get("pdf_url") and p.get("pdf_url"):
                cur["pdf_url"] = p["pdf_url"]
            cur["citation_count"] = max(cur.get("citation_count", 0), p.get("citation_count", 0))
    return list(best.values())


# -------------------------------------------------------------- scoring ------
# Transparent rule-based relevance prior from simple signals: title/abstract
# hits, exact phrase, query coverage, recency, and citations. This is only a
# prior — Claude re-ranks by research fit downstream (see references/search.md).
def rule_score(p, query, this_year=2026):
    q = query.lower()
    # ASCII word tokens (>2 chars) plus individual CJK characters, so Chinese /
    # Japanese queries get real keyword signal instead of scoring near-zero.
    ascii_tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 2]
    cjk_tokens = re.findall(r"[一-鿿]", q)
    tokens = ascii_tokens + cjk_tokens
    title = (p.get("title") or "").lower()
    abstract = (p.get("abstract") or "").lower()
    sig = {}

    title_hits = sum(1 for t in set(tokens) if t in title)
    abs_hits = sum(1 for t in set(tokens) if t in abstract)
    sig["title_hits"] = title_hits
    sig["abstract_hits"] = abs_hits

    score = title_hits * 4 + abs_hits * 1.5
    if q and q in title:
        score += 5
        sig["exact_phrase_in_title"] = True
    elif q and q in abstract:
        score += 3
        sig["exact_phrase_in_abstract"] = True

    coverage = (len([t for t in set(tokens) if t in title or t in abstract]) /
                max(1, len(set(tokens))))
    score += coverage * 12
    sig["token_coverage"] = round(coverage, 2)

    if abstract:
        score += 2
        sig["has_abstract"] = True
    else:
        sig["has_abstract"] = False

    year = p.get("year")
    if year:
        recency = max(0.0, 10.0 - (this_year - year) * 0.55)
        score += recency
        sig["recency_bonus"] = round(recency, 1)

    cites = p.get("citation_count", 0) or 0
    cite_bonus = min(12.0, math.log1p(cites) * 2.0)
    score += cite_bonus
    sig["citation_bonus"] = round(cite_bonus, 1)

    return round(score, 2), sig


# ---------------------------------------------------------- markdown render --
def _doi_url(p):
    d = (p.get("doi") or "").strip()
    return f"https://doi.org/{d}" if d else None


def render_compact(papers, query):
    """One numbered line per paper — scannable for large result sets, and the
    number is how the user refers back ('deep-read #3')."""
    if not papers:
        return f"## 🔎 No results for: {query}\n\nTry broader terms or fewer filters."
    n = len(papers)
    out = [f"## 🔎 {n} results for: {query}",
           f"*All {n}, numbered 1–{n}. Show the whole list; the user refers to any "
           f"paper by its number (e.g. \"deep-read #3\").*", ""]
    for i, p in enumerate(papers, 1):
        title = (p.get("title") or "Untitled").strip()
        link = _doi_url(p) or p.get("url") or p.get("pdf_url")
        head = f"[{title}]({link})" if link else title
        authors = p.get("authors") or []
        who = (authors[0] + " et al." if len(authors) > 1 else (authors[0] if authors else ""))
        bits = [x for x in [who, str(p.get("year") or ""),
                            f"cited {p.get('citation_count', 0)}",
                            "🟢" if p.get("pdf_url") else "🔒"] if x]
        line = f"{i}. **{head}** — " + " · ".join(bits)
        if p.get("pdf_url"):
            line += f" · [PDF]({p['pdf_url']})"
        out.append(line)
    out.append(f"\n— end of {n} results —")
    return "\n".join(out)


def render_markdown(papers, query):
    """Fixed, self-contained Markdown so the result looks identical no matter
    which model relays it. Each paper = a card with title, full metadata, an
    abstract, and clickable links straight to the original / PDF / DOI."""
    if not papers:
        return f"## 🔎 No results for: {query}\n\nTry broader terms or fewer filters."
    n = len(papers)
    out = [f"## 🔎 {n} results for: {query}",
           f"*All {n} results, numbered 1–{n}. Show every card as one flat list — "
           f"don't truncate or regroup; the user refers to papers by number.*", ""]
    for i, p in enumerate(papers, 1):
        title = (p.get("title") or "Untitled").strip()
        primary = _doi_url(p) or p.get("url") or p.get("pdf_url")
        out.append(f"### {i}. [{title}]({primary})" if primary else f"### {i}. {title}")

        authors = p.get("authors") or []
        astr = ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else "")
        meta = [x for x in [
            astr or None,
            str(p["year"]) if p.get("year") else None,
            f"*{p['venue']}*" if p.get("venue") else None,
            f"cited by {p.get('citation_count', 0)}",
            f"via {p.get('source', '')}",
            "🟢 Open Access" if p.get("pdf_url") else "🔒 No free PDF",
        ] if x]
        out.append("  ".join(meta))

        ab = re.sub(r"\s+", " ", (p.get("abstract") or "")).strip()
        if ab:
            out.append("")
            out.append("> " + (ab[:300] + "…" if len(ab) > 300 else ab))

        links = []
        if p.get("url"):
            links.append(f"[📄 Open paper]({p['url']})")
        if p.get("pdf_url"):
            links.append(f"[⬇ PDF]({p['pdf_url']})")
        if _doi_url(p):
            links.append(f"[🔗 DOI]({_doi_url(p)})")
        if links:
            out.append("")
            out.append(" · ".join(links))
        out.append("")
    out.append(f"— end of {n} results —")
    return "\n".join(out)


# -------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--from-year", type=int, default=None)
    ap.add_argument("--to-year", type=int, default=None)
    ap.add_argument("--open-access-only", action="store_true")
    ap.add_argument("--sources", default="openalex,crossref,arxiv,s2,europepmc")
    ap.add_argument("--brief", action="store_true",
                    help="Print a compact ranked table instead of full JSON "
                         "(easy to skim; omit for the full records incl. abstracts).")
    ap.add_argument("--markdown", action="store_true",
                    help="Print ready-to-show Markdown cards: title + full details "
                         "+ clickable links to the original / PDF / DOI. This is the "
                         "fixed user-facing format — identical no matter which model "
                         "relays it.")
    ap.add_argument("--compact", action="store_true",
                    help="Print a numbered one-line-per-paper list (title link + "
                         "authors/year/citations/OA + PDF). Best for scanning many "
                         "results and referring to a paper by its number.")
    args = ap.parse_args()

    requested = [s.strip() for s in args.sources.split(",") if s.strip()]
    chosen = [s for s in requested if s in SOURCES]
    unknown = [s for s in requested if s not in SOURCES]
    if unknown:
        sys.stderr.write(f"note: ignoring unknown source(s): {', '.join(unknown)} "
                         f"(valid: {', '.join(SOURCES)})\n")
    if not chosen:
        sys.stderr.write("error: no valid sources selected.\n")
        json.dump({"query": args.query, "count": 0, "source_errors": {}, "papers": []},
                  sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    # Fetch a healthy candidate pool per source (decoupled from --limit) so that
    # year / open-access filters have room to work instead of wiping a tiny pool.
    per_source = min(50, max(40, args.limit))
    errors = {}
    collected = []
    with cf.ThreadPoolExecutor(max_workers=len(chosen) or 1) as ex:
        futs = {ex.submit(SOURCES[s], args.query, per_source): s for s in chosen}
        for fut in cf.as_completed(futs):
            s = futs[fut]
            try:
                collected.extend(fut.result())
            except Exception as e:  # one dead source must not kill the search
                errors[s] = f"{type(e).__name__}: {e}"

    papers = dedup([p for p in collected if p.get("title")])

    if args.from_year:
        papers = [p for p in papers if (p.get("year") or 0) >= args.from_year]
    if args.to_year:
        papers = [p for p in papers if (p.get("year") or 9999) <= args.to_year]
    if args.open_access_only:
        papers = [p for p in papers if p.get("pdf_url")]

    for p in papers:
        p["rule_score"], p["rule_signals"] = rule_score(p, args.query)
    papers.sort(key=lambda p: p["rule_score"], reverse=True)
    papers = papers[:args.limit]

    if errors:
        def _why(s, msg):
            if s == "s2" and "429" in msg:
                has_key = os.environ.get("S2_API_KEY") or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
                return ("s2 rate-limited" + ("" if has_key else
                        " — set S2_API_KEY (free) to enable it"))
            return f"{s} unavailable"
        note = "; ".join(_why(s, m) for s, m in errors.items())
        sys.stderr.write(f"note: {len(errors)}/{len(chosen)} source(s) skipped "
                         f"({note}); results came from the other {len(chosen)-len(errors)}.\n")

    if args.compact:
        print(render_compact(papers, args.query))
        return

    if args.markdown:
        print(render_markdown(papers, args.query))
        return

    if args.brief:
        # Compact, skimmable table. rule_score is a keyword prior, not a verdict —
        # the genuinely best-fit paper may sit lower; re-rank by research fit.
        print(f"# {len(papers)} papers for: {args.query}")
        print(f"{'#':>2}  {'year':>4}  {'cites':>5}  OA  score   title")
        for i, p in enumerate(papers, 1):
            oa = "Y" if p.get("pdf_url") else "-"
            title = (p.get("title") or "")[:70]
            print(f"{i:>2}  {str(p.get('year') or '?'):>4}  "
                  f"{p.get('citation_count', 0):>5}  {oa}  {p['rule_score']:>5.1f}  {title}")
        print("\n(rule_score = keyword/recency/citation prior, NOT final relevance — re-rank by fit.)")
        return

    json.dump({
        "query": args.query,
        "count": len(papers),
        "source_errors": errors,
        "papers": papers,
    }, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
