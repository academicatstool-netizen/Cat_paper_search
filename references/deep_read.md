# Reference: Deep Read (single-paper analysis)

You run `scripts/fetch_pdf.py` to resolve an open-access PDF and extract its
text, then produce an evidence-aware reading report from the extracted text
**only**. The cardinal rule: never add facts from your own memory of the paper
— if the excerpt doesn't contain it, say so.

## Flow

1. Get an identifier for the paper (DOI, arXiv id, a direct `pdf_url`, or just
   the title). Prefer DOI or arXiv id.
2. Run `fetch_pdf.py` (see SKILL.md for flags). It returns `text`, `pages[]`,
   `page_count`, and `truncated`.
3. If `resolved_pdf_url` is null, the paper is almost certainly paywalled with
   no OA copy. Tell the user plainly and offer to (a) try a different
   identifier, or (b) work from the abstract instead. Do not fabricate.
4. If `truncated` is true, the report covers only the analysed excerpt
   (the first ~8 pages). Disclose this in the output.

## Deep-read analysis prompt (apply to the extracted text)

```
You are reading one academic paper and producing a compact, evidence-aware deep reading report.

{coverage_note}   # e.g. "PARTIAL INPUT: only the first N of M pages were analysed."

User query (what the reader cares about): {user_query}

Paper metadata:
Title: {title}
Authors: {authors}
Year: {year}
Source: {source}

Extracted paper text:
{text}

Return JSON only in this format:
{
  "academic_summary": "1-2 readable paragraphs",
  "study_snapshot": {
    "research_question": "1 sentence",
    "study_design": "1 sentence",
    "sample_or_material": "1 sentence",
    "core_claim": "1 sentence"
  },
  "core_contribution": "1-3 sentences",
  "theoretical_or_conceptual_frame": "1-3 sentences",
  "key_findings": ["...", "...", "..."],
  "evidence_chain": ["claim/result + page", "claim/result + page"],
  "relevance_to_query": "1-3 sentences",
  "relevance_score": 72,
  "methodological_notes": ["...", "..."],
  "practical_implications": ["...", "..."],
  "limitations_or_cautions": ["...", "..."]
}

Rules:
- relevance_score is an integer 0-100 (0=unrelated, 100=perfectly on-topic).
- Use ONLY the supplied paper text. Do NOT add facts, numbers, findings, or
  claims from your own knowledge of this paper or its authors.
- If the excerpt does not contain what a field asks for (common with partial
  input), say so explicitly — e.g. "Not covered in the analysed excerpt".
  Never fabricate a plausible-sounding finding to fill a field.
- Keep claims conservative. Mention page numbers when clear.
- Return valid JSON only.
```

You may render the JSON as readable Markdown for the user, but keep every field
grounded in the text. The `evidence_chain` (claim → page number) is the most
valuable part — it lets the reader verify each claim against the source.

## Claim extraction (optional, for synthesis hand-off)

When the reader plans to write something and wants reusable, typed claims,
extract 1–3 per paper from the abstract/core text:

```
Extract 1–3 high-value, synthesis-ready research claims from the paper.

Each claim:
- claim_text: a precise, typed research assertion — not a generic summary
- claim_type: finding | method | framing | limitation
- support_level: strong (directly stated, likely replicated) |
                 moderate (implied, not central) | weak (speculative/partial)
- scope_note: what population, context, or condition the claim holds for
- evidence_basis: the study design, sample, or reported metric behind it
  (do not invent specifics not present in the text)
- claim_confidence: high | medium | low (your epistemic confidence, distinct
  from support_level)

Rules:
- Fewer, higher-quality claims beat more.
- Do not invent causal conclusions beyond what the text reports.
- If evidence is weak or the text is vague, set support_level=weak and
  claim_confidence=low.
Return JSON: {"claims": [ ... ]}
```

These claims feed directly into the Synthesis Lab planner (see
`references/synthesis.md`) as grounded, pre-vetted evidence.

## Translation

`fetch_pdf.py` already gives you clean per-page text. To produce a translated
reading (e.g. Chinese/Japanese/Korean for a non-English reader), translate the
extracted text page by page, locking technical terms and proper nouns
(method names, gene symbols, model names) in their original form. State that
the translation is of the analysed excerpt, not necessarily the full paper.
