# Reference: Literature Search & Ranking

This file holds the prompts and criteria you (Claude) apply around
`scripts/search_papers.py`. The script handles retrieval + transparent
rule scoring; you handle query understanding and research-fit re-ranking.

## Pipeline

1. **Understand the query** → expand into directions/keywords (prompts below).
2. **Retrieve** → run `search_papers.py` with the best query string(s).
3. **Re-rank** → read the returned `papers[]` and apply the research-fit and
   adversarial criteria below. The script's `rule_score` is a prior, not the
   verdict — your job is to judge *fit to the user's actual question*, not
   keyword overlap.
4. **Present** → ranked list with a one-line "why" per paper, grouped by
   direction when the user asked something broad.

---

## Stage 1 — Decompose the query

Reply with JSON only.

```
Decompose this research query into structured parts. Reply with JSON only.
Query: "{q}"

Return this EXACT shape (arrays may be empty; keep each list ≤6 items; one-phrase items):
{
  "core_terms":  ["main concepts the user typed or immediate synonyms"],
  "constraints": ["scope limiters: year/domain/population/language"],
  "methods":     ["study methodology terms if mentioned, else empty"],
  "contexts":    ["application contexts, disciplines, settings"],
  "intent_type": "exploratory | comparative | mechanism | application | critique | historical | survey"
}
Rules: short phrases, no sentences, bilingual OK, no commentary.
```

## Stage 2 — Expand into keyword clusters

```
Expand decomposed research query into keyword clusters for search. JSON only.
{summary of decompose}

Return this EXACT shape (3-6 clusters; each ≤6 terms; no sentences):
{
  "clusters": [
    { "anchor": "<one core_term or synonym>", "terms": ["closely related phrase 1", "phrase 2"] }
  ]
}
Rules: stay tight around anchors. No generic filler. Bilingual OK. No prose.
```

## Stage 3 — Build a directions tree (use for broad/exploratory queries)

```
Build a directions tree for academic search. JSON only. No prose.
Original query: "{q}"
Core terms: {terms_line}
Intent: {intent}
Clusters:
{cluster_lines}

Direction count (IMPORTANT — users want to see real breadth):
- Start by asking: how many genuinely DISTINCT clusters of work exist on this topic? That number is your target.
- Typical well-studied topic: produce 5 or 6 big directions.
- Mature / heavily-researched field (e.g. cardiovascular disease, machine learning, climate change, cancer therapy, quantum computing, education research): produce 6–8 big directions. These fields span many real clusters — do not compress them.
- Output only 4 big directions when the query is genuinely narrow and you cannot identify a 5th distinct angle.
- Sub_directions: 4 minimum; go to 5–7 when the direction itself has many concrete specific angles.
- Hard ceiling: 8 big × 7 sub. No padding, no near-duplicates.

Each direction_title must include at least one core term or cluster anchor.

Shape:
{
  "directions": [
    {
      "direction_title": "6 words max; must cite a core term",
      "direction_summary": "1 sentence on scope",
      "keywords": ["3-6 keywords"],
      "search_query": "short academic query",
      "confidence": 0.0-1.0,
      "sub_directions": [
        { "title": "specific angle, ≤7 words", "summary": "1 sentence on why this angle",
          "keywords": ["2-5 keywords"], "search_query": "short academic query", "confidence": 0.0-1.0 }
      ]
    }
  ],
  "recommended_direction": 0
}

LANGUAGE: Write all titles, summaries, keywords, and search queries in English. Even if the user's query is in another language, return the directions tree in English so the downstream academic search (dominated by English-language sources) gets clean queries. Translate / transliterate non-English terms; keep proper nouns and domain-specific terms (e.g. 'gradient descent', 'p53') verbatim.
```

For a focused query you can skip Stage 3 and just search the recommended
`search_query`. For a broad query, search the top 2–4 `search_query` strings
(separate `search_papers.py` runs) and merge.

---

## Re-ranking: research fit (apply to each returned paper)

Score each paper for how well it fits the user's **current research question**,
not broad keyword overlap. For each paper produce:

- `research_fit_score`: 0-100
- `domain_fit_label`: one of `direct | mostly direct | adjacent | off-target`
- `paper_type_label`: one of `empirical study | review/survey | framework/tool | technical method | application/case | theory/other`
- `abstract_quality_label`: `good | limited | missing`
- `off_target_risk_score`: 0-100
- `reason`: short sentence, max 22 words

Then order primarily by `research_fit_score`, with these adjustments:
- type: empirical +12, review +8, framework −6, technical −14, application −10
- domain: direct +14, mostly +7, adjacent −10, off-target −24
- abstract: good +4, limited −3, missing −18
- subtract `off_target_risk_score` × ~0.25
- citation prior is already in the script's `rule_signals.citation_bonus`

## Adversarial screening (for borderline papers, fit 40–80)

Simulate a 3-role debate and decide keep / uncertain / reject:

```
For each borderline paper, simulate a structured debate between three roles:
1. SelectorAgent — argues for keeping the paper
2. CriticAgent — tries to reject it (off-target, weak support, domain mismatch)
3. ArbiterAgent — makes the final decision: keep | uncertain | reject

Principles:
- Missing abstract should strongly hurt borderline papers.
- Adjacent or off-target domain papers should be rejected unless they clearly
  provide necessary background.
- Technical method / framework papers should be penalised when the user asks
  about substantive research findings rather than tooling.
- Do not reward mere keyword overlap.
```

Drop `reject`ed papers from the main list (optionally show them under a
collapsed "screened out" note with the one-line reason).

## Sort modes

If the user signals a preference, bias the final order accordingly:
- **balanced** (default): research fit, lightly boosted by recency + citations
- **newest**: year first, then fit
- **most cited**: `citation_count` first, then fit
- **open access**: papers with a `pdf_url` first (these are deep-readable)
- **evidence strength**: title/abstract match density + recency over fit
