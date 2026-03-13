# Translator — main orchestration class.
#
# Accepts a Calliope model (as a directory path or in-memory object) plus an optional
# epistemic sidecar, and coordinates the StructuralMapper, EpistemicEngine, and
# ResultsMapper to produce a validated N-Quads (.nq) knowledge graph.
#
# Must remain decoupled from filesystem logic so it can be used inside Jupyter notebooks
# by passing in-memory objects directly.
#
# Public interface (to be implemented):
#   Translator(model, sidecar=None, results=None)
#   Translator.translate() -> rdflib.ConjunctiveGraph
#   Translator.save(path: str) -> None          # serializes to .nq
#   Translator.push(endpoint: str) -> None      # optional: SPARQL UPDATE to endpoint
