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

