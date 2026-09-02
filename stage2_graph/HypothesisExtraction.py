"""
HypothesisExtraction.py

For each citation edge (source paper -> target paper, same cluster) this
module decides WHAT the source paper did to the target paper's idea:

    extends    - builds on / generalizes the prior idea
    improves   - same idea, but better result (accuracy, speed, complexity,
                 lower error, higher throughput, etc.)
    disproves  - contradicts, refutes, or shows the prior claim fails
    uses       - just uses the prior method/result as a building block,
                 no explicit comparison

It works in two layers so it degrades gracefully:

  1. Lexical/pattern layer (always available, no API key needed): scores
     the citation-context sentence(s) against keyword families and, when
     present, pulls out any quantitative comparison ("2x faster",
     "reduces error by 10%", "O(n log n) vs O(n^2)").

  2. Optional LLM layer: if ANTHROPIC_API_KEY is set in the environment,
     ambiguous edges (lexical layer unsure) are sent to Claude for a
     structured judgement. This is optional -- comment out `use_llm=True`
     if you don't want API calls.

Output: hypothesis_edges.json -- same edges as citation_contexts.json,
each annotated with `relation`, `confidence`, `evidence`, and
`quant_signal` (any extracted numeric comparison string).
"""

import os
import re
import json

# --- keyword families -------------------------------------------------

DISPROVE_WORDS = [
    "however", "in contrast", "contrary to", "fails to", "does not hold",
    "we show that .* does not", "disprove", "refute", "contradicts",
    "overturns", "invalidates", "no longer holds", "counterexample",
    "unlike", "fails when", "breaks down", "is insufficient",
    "cannot explain", "inconsistent with",
]

IMPROVE_WORDS = [
    "outperform", "faster", "improves upon", "improve upon", "achieves better",
    "higher accuracy", "lower error", "reduces", "state-of-the-art",
    "sota", "surpasses", "more efficient", "speeds up", "fewer parameters",
    "better than", "superior to", "significant improvement", "gains over",
]

EXTEND_WORDS = [
    "extend", "generalize", "building on", "build on", "based on",
    "following", "inspired by", "we adapt", "we modify", "augment",
    "incorporate", "combine .* with", "leverage", "expand upon",
]

USE_WORDS = [
    "we use", "utilizing", "employ", "adopt", "apply", "as in",
    "following the approach of", "using the method of",
]

QUANT_PATTERN = re.compile(
    r"(\d+(\.\d+)?\s*[xX%]|"
    r"O\([^)]+\)\s*(vs\.?|versus|compared to)\s*O\([^)]+\)|"
    r"\d+(\.\d+)?\s*(times|percent|pp)\b)"
)


def _score(text, word_list):
    text_l = text.lower()
    score = 0
    hits = []
    for w in word_list:
        if re.search(w, text_l):
            score += 1
            hits.append(w)
    return score, hits


def classify_lexical(evidence_text):
    """Rule-based classification of a single evidence string."""
    if not evidence_text:
        return None, 0.0, [], None

    quant_match = QUANT_PATTERN.search(evidence_text)
    quant_signal = quant_match.group(0) if quant_match else None

    scores = {
        "disproves": _score(evidence_text, DISPROVE_WORDS),
        "improves": _score(evidence_text, IMPROVE_WORDS),
        "extends": _score(evidence_text, EXTEND_WORDS),
        "uses": _score(evidence_text, USE_WORDS),
    }

    # quantitative comparison language strongly implies "improves"
    if quant_signal:
        scores["improves"] = (scores["improves"][0] + 2, scores["improves"][1])

    best_label, (best_score, hits) = max(scores.items(), key=lambda kv: kv[1][0])

    if best_score == 0:
        return "uses", 0.3, [], quant_signal  # default: weak/no signal -> plain citation

    total_hits = sum(s for s, _ in scores.values())
    confidence = min(0.95, 0.4 + 0.15 * best_score) if total_hits else 0.3

    return best_label, confidence, hits, quant_signal


def classify_lexical_multi(contexts):
    """Combine multiple evidence snippets for one edge into one verdict."""
    if not contexts:
        return "uses", 0.2, [], None

    best = ("uses", 0.0, [], None)
    for ctx in contexts:
        label, conf, hits, quant = classify_lexical(ctx)
        if conf > best[1]:
            best = (label, conf, hits, quant)
    return best


