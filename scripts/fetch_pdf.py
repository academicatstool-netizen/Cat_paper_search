#!/usr/bin/env python3
"""
fetch_pdf.py — Resolve an open-access PDF for a paper and extract its text.

Resolves an open-access PDF via a fallback chain: try any direct PDF URL,
then arXiv-by-DOI, Unpaywall, OpenAlex, and Semantic Scholar in turn.
Downloads the first real PDF (validated by the %PDF magic bytes), extracts
page text with pypdf, and emits JSON that Claude reads to produce a deep-read
report (see references/deep_read.md).

Usage:
    python fetch_pdf.py --doi 10.1145/3313831.3376234
    python fetch_pdf.py --arxiv 1706.03762
    python fetch_pdf.py --pdf-url https://.../paper.pdf
    python fetch_pdf.py --title "Attention is all you need"
    # optional: --max-pages 8 --max-chars 24000 --email you@example.com

Output JSON: {resolved_pdf_url, page_count, pages_extracted,
              pages:[{page_number,text}], text, truncated, tried[]}

Requires: pypdf  (pip install pypdf)
"""
import argparse
import io
import json
import os
import re
import sys
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "academi-skill/1.0 (mailto:hello@example.com)"
TIMEOUT = 25
MAX_PAGES = 12        # default: read the first 12 pages with text (covers most
                      # papers' results/discussion, not just intro+method)
MAX_CHARS = 40000     # cap on how much text to hand back for analysis

# Fall back to an unverified TLS context on machines with a broken CA store
# (common on Windows) — all requests here are public read-only GETs.
try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = ssl.create_default_context()
_CTX_UNVERIFIED = ssl._create_unverified_context()


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX) as resp:
            return resp.read(), resp.headers.get("Content-Type", "")
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), ssl.SSLError):
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX_UNVERIFIED) as resp:
                return resp.read(), resp.headers.get("Content-Type", "")
        raise


def _get_json(url, headers=None):
    data, _ = _get(url, headers)
    return json.loads(data.decode("utf-8", "replace"))


def _looks_like_pdf(b):
    return b[:5].lstrip()[:4] == b"%PDF" or b[:4] == b"%PDF"


# -------------------------------------------------- OA candidate resolvers ---
def cand_arxiv_by_doi(doi):
    if not doi:
        return []
    m = re.search(r"10\.48550/arxiv\.(.+)", doi, re.I)
    if m:
        return [f"https://arxiv.org/pdf/{m.group(1)}"]
    return []


def cand_arxiv_id(arxiv_id):
    if not arxiv_id:
        return []
    aid = arxiv_id.strip().replace("arXiv:", "")
    return [f"https://arxiv.org/pdf/{aid}"]


def cand_unpaywall(doi, email):
    if not doi:
        return []
    try:
        data = _get_json(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}")
    except Exception:
        return []
    urls = []
    best = data.get("best_oa_location") or {}
    if best.get("url_for_pdf"):
        urls.append(best["url_for_pdf"])
    for loc in data.get("oa_locations", []) or []:
        if loc.get("url_for_pdf"):
            urls.append(loc["url_for_pdf"])
    return urls


def cand_openalex(doi):
    if not doi:
        return []
    try:
        data = _get_json(f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi)}")
    except Exception:
        return []
    urls = []
    for key in ("best_oa_location", "primary_location"):
        loc = data.get(key) or {}
        if loc.get("pdf_url"):
            urls.append(loc["pdf_url"])
    return urls


def cand_s2(doi, title):
    ident = f"DOI:{doi}" if doi else None
    try:
        if ident:
            data = _get_json(
                f"https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(ident)}"
                "?fields=openAccessPdf,externalIds")
        elif title:
            sr = _get_json(
                "https://api.semanticscholar.org/graph/v1/paper/search?query=" +
                urllib.parse.quote(title) + "&limit=1&fields=openAccessPdf,externalIds")
            data = (sr.get("data") or [{}])[0]
        else:
            return []
    except Exception:
        return []
    urls = []
    if (data.get("openAccessPdf") or {}).get("url"):
        urls.append(data["openAccessPdf"]["url"])
    ext = data.get("externalIds") or {}
    if ext.get("ArXiv"):
        urls.append(f"https://arxiv.org/pdf/{ext['ArXiv']}")
    return urls


def resolve_doi_from_title(title):
    """Best-effort DOI for a title via Crossref, guarded by a title match so we
    don't silently resolve an unrelated paper. Returns None if nothing fits."""
    try:
        data = _get_json("https://api.crossref.org/works?query.bibliographic=" +
                         urllib.parse.quote(title) + "&rows=3&select=DOI,title")
        for it in data.get("message", {}).get("items", []):
            found = " ".join(it.get("title", []) or [])
            doi = it.get("DOI")
            if doi and _title_match(title, found):
                return doi
        return None
    except Exception:
        return None


def _title_match(query, found):
    """Loose check that a matched record's title really is the queried paper —
    guards against an API returning an unrelated top hit."""
    norm = lambda s: set(re.findall(r"[a-z0-9]+", (s or "").lower()))
    a, b = norm(query), norm(found)
    if not a or not b:
        return False
    return len(a & b) / len(a) >= 0.5


def cand_title_arxiv(title):
    """Search arXiv by title — the most reliable route for the many papers
    people want to read by name that live on arXiv (ML/CS/physics/stat)."""
    if not title:
        return []
    try:
        url = ("https://export.arxiv.org/api/query?search_query=" +
               urllib.parse.quote("all:" + title) + "&max_results=1")
        body, _ = _get(url)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        e = ET.fromstring(body).find("a:entry", ns)
        if e is None or not _title_match(title, e.findtext("a:title", "", ns)):
            return []
        for link in e.findall("a:link", ns):
            if link.get("title") == "pdf":
                return [link.get("href")]
    except Exception:
        return []
    return []


def cand_title_openalex(title):
    """Find an OA PDF by matching the title in OpenAlex (title-only search)."""
    if not title:
        return []
    try:
        data = _get_json("https://api.openalex.org/works?filter=title.search:" +
                         urllib.parse.quote(title) + "&per_page=1")
        results = data.get("results", [])
    except Exception:
        return []
    if not results or not _title_match(title, results[0].get("title")):
        return []
    w, urls = results[0], []
    for key in ("best_oa_location", "primary_location"):
        loc = w.get(key) or {}
        if loc.get("pdf_url"):
            urls.append(loc["pdf_url"])
    return urls


# ----------------------------------------------------------- text extract ----
def extract_text(pdf_bytes, max_pages, max_chars):
    try:
        from pypdf import PdfReader  # imported lazily so --help works without it
    except ImportError:
        sys.stderr.write(
            "ERROR: this step needs the 'pypdf' package.\n"
            "Install it with:  pip install -r scripts/requirements.txt\n"
            "             or:  pip install pypdf\n")
        sys.exit(2)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    total = len(reader.pages)
    chars = 0
    for i, page in enumerate(reader.pages):
        if len(pages) >= max_pages or chars >= max_chars:
            break
        try:
            txt = re.sub(r"[ \t]+", " ", page.extract_text() or "").strip()
        except Exception:
            txt = ""
        if not txt:
            continue
        pages.append({"page_number": i + 1, "text": txt})
        chars += len(txt)
    joined = "\n\n".join(p["text"] for p in pages)[:max_chars]
    return total, pages, joined


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doi")
    ap.add_argument("--arxiv")
    ap.add_argument("--pdf-url")
    ap.add_argument("--title")
    ap.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL", "anonymous@example.com"),
                    help="Contact email for the Unpaywall API (etiquette). "
                         "Defaults to $UNPAYWALL_EMAIL if set.")
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES)
    ap.add_argument("--max-chars", type=int, default=MAX_CHARS)
    ap.add_argument("--text-only", action="store_true",
                    help="Print just the extracted text (and resolved URL on "
                         "stderr) instead of the full JSON object.")
    args = ap.parse_args()

    if not (args.doi or args.arxiv or args.pdf_url or args.title):
        sys.stderr.write("error: give one of --doi, --arxiv, --pdf-url, or --title "
                         "to identify the paper.\n")
        sys.exit(2)

    doi = args.doi
    if not doi and not args.arxiv and not args.pdf_url and args.title:
        doi = resolve_doi_from_title(args.title)

    # Build candidate URL queue in priority order.
    candidates = []
    if args.pdf_url:
        candidates.append(args.pdf_url)
    candidates += cand_arxiv_id(args.arxiv)
    # Title-based direct discovery first — searching S2 and OpenAlex by title
    # finds an OA PDF (or arXiv id) far more reliably than Crossref's DOI alone.
    if args.title:
        candidates += cand_title_arxiv(args.title)
        candidates += cand_s2(None, args.title)
        candidates += cand_title_openalex(args.title)
    candidates += cand_arxiv_by_doi(doi)
    candidates += cand_unpaywall(doi, args.email)
    candidates += cand_openalex(doi)
    candidates += cand_s2(doi, args.title)

    seen, queue = set(), []
    for u in candidates:
        if u and u not in seen:
            seen.add(u)
            queue.append(u)

    tried, pdf_bytes, resolved = [], None, None
    for url in queue:
        try:
            body, ctype = _get(url)
            if _looks_like_pdf(body):
                pdf_bytes, resolved = body, url
                tried.append({"url": url, "ok": True})
                break
            # Landing page: look for an embedded PDF link and try it once.
            m = re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', body.decode("utf-8", "replace"), re.I)
            if m:
                nxt = urllib.parse.urljoin(url, m.group(1))
                if nxt not in seen:
                    body2, _ = _get(nxt)
                    if _looks_like_pdf(body2):
                        pdf_bytes, resolved = body2, nxt
                        tried.append({"url": url, "ok": True, "via": nxt})
                        break
            tried.append({"url": url, "ok": False, "reason": "not a PDF"})
        except Exception as e:
            tried.append({"url": url, "ok": False, "reason": f"{type(e).__name__}: {e}"})

    if pdf_bytes is None:
        if args.text_only:
            sys.stderr.write("No open-access PDF could be resolved (likely paywalled).\n")
            sys.exit(1)
        json.dump({
            "resolved_pdf_url": None,
            "error": "No open-access PDF could be resolved (likely paywalled).",
            "tried": tried,
        }, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return

    total, pages, joined = extract_text(pdf_bytes, args.max_pages, args.max_chars)

    if args.text_only:
        sys.stderr.write(f"resolved: {resolved}\n")
        sys.stderr.write(f"pages: {len(pages)}/{total}"
                         f"{' (truncated)' if len(pages) < total else ''}\n")
        sys.stdout.write(joined + "\n")
        if len(pages) < total:
            # Make truncation visible IN the text stream, not just on stderr, so
            # a reading built from this can't silently omit later sections.
            sys.stdout.write(
                f"\n[... TRUNCATED: only the first {len(pages)} of {total} pages "
                f"were extracted; later sections (e.g. full results) are not "
                f"included. Re-run with --max-pages/--max-chars for more. ...]\n")
        return

    json.dump({
        "resolved_pdf_url": resolved,
        "page_count": total,
        "pages_extracted": len(pages),
        "truncated": len(pages) < total,
        "pages": pages,
        "text": joined,
        "tried": tried,
    }, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
