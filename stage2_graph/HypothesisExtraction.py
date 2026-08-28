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

