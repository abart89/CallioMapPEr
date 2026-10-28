"""Verify the shipped ontology snapshot rather than regenerating historical LinkML."""
import hashlib
from importlib.resources import files
import json
from rdflib import Graph, RDF, OWL, URIRef
from calliomapper.vocabulary import OC, ONTOLOGY_VERSION


def test_all_bundled_snapshot_hashes():
    root = files('calliomapper').joinpath('resources')
    manifest = json.loads(root.joinpath('snapshot.json').read_text())
    for name, expected in manifest['sha256'].items():
        assert hashlib.sha256(root.joinpath(name).read_bytes()).hexdigest() == expected, name
    ontology = Graph().parse(data=root.joinpath('ontocal.ttl').read_text(), format='turtle')
    assert (OC[''], OWL.versionIRI, URIRef(ONTOLOGY_VERSION)) in ontology
    assert (OC.InputAssignment, RDF.type, OWL.Class) in ontology
    assert len(list(ontology.objects(OC[''], OWL.imports))) == 2
