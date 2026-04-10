from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, OWL  # noqa: F401 — re-exported for convenience

# BFO — Basic Formal Ontology (OBO PURL namespace)
BFO = Namespace("http://purl.obolibrary.org/obo/BFO_")

# OEO — Open Energy Ontology (IRI TBD; placeholder until ontologist input)
OEO = Namespace("http://openenergy-platform.org/ontology/oeo/")

# PROV — W3C PROV-O
PROV = Namespace("http://www.w3.org/ns/prov#")

# ONTOCAL — CallioMapper default namespace for tool-specific classes and predicates
ONTOCAL = Namespace("https://w3id.org/ontocal/")
