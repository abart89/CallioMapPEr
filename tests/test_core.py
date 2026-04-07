"""
Tests for CoreMapper using the dummy schema.
"""

from pathlib import Path

import pytest
from rdflib import BNode, Dataset, Graph, URIRef
from rdflib.namespace import RDF, RDFS

from calliomapper import Translator
from calliomapper.mapper.core import CoreMapper
from calliomapper.ontology.namespaces import ONTOCAL
from calliomapper.utils.io import serialize_nq  # noqa: F401
from calliomapper.utils.validation import ValidationError, validate

SHAPES = Path(__file__).parent.parent / "ontology" / "dummy_shapes.ttl"
RUN_ID = "https://w3id.org/ontocal/runs/test-run-001"


# ---------------------------------------------------------------------------
# CoreMapper unit tests
# ---------------------------------------------------------------------------


class TestCoreMapper:
    def test_single_entity_type_triple(self):
        g = CoreMapper(RUN_ID).map(nodes={"region_a": {}})
        entity = URIRef(RUN_ID + "/region_a")
        assert (entity, RDF.type, ONTOCAL.CalliopeThing) in g

    def test_single_entity_label_triple(self):
        g = CoreMapper(RUN_ID).map(nodes={"region_a": {"name": "Region A"}})
        entity = URIRef(RUN_ID + "/region_a")
        labels = list(g.objects(entity, RDFS.label))
        assert len(labels) == 1
        assert str(labels[0]) == "Region A"

    def test_label_falls_back_to_key_name(self):
        g = CoreMapper(RUN_ID).map(nodes={"wind_onshore": {}})
        entity = URIRef(RUN_ID + "/wind_onshore")
        assert str(list(g.objects(entity, RDFS.label))[0]) == "wind_onshore"

    def test_multiple_nodes_and_techs(self):
        g = CoreMapper(RUN_ID).map(
            nodes={"region_a": {}, "region_b": {}},
            techs={"wind": {}, "solar": {}},
        )
        assert len(list(g.subjects(RDF.type, ONTOCAL.CalliopeThing))) == 4

    def test_graph_identifier_default(self):
        g = CoreMapper(RUN_ID).map(nodes={"region_a": {}})
        assert str(g.identifier) == RUN_ID + "/core"

    def test_graph_identifier_custom(self):
        custom = RUN_ID + "/scenario-high-renewables"
        g = CoreMapper(RUN_ID, graph_id=custom).map(nodes={"region_a": {}})
        assert str(g.identifier) == custom

    def test_custom_graph_id_does_not_affect_entity_uris(self):
        # Entity URIs are always anchored to run_id, not graph_id
        custom = RUN_ID + "/scenario-high-renewables"
        g = CoreMapper(RUN_ID, graph_id=custom).map(nodes={"region_a": {}})
        entity = URIRef(RUN_ID + "/region_a")
        assert (entity, RDF.type, ONTOCAL.CalliopeThing) in g

    def test_empty_input_produces_empty_graph(self):
        g = CoreMapper(RUN_ID).map()
        assert len(g) == 0


# ---------------------------------------------------------------------------
# SHACL validation
# ---------------------------------------------------------------------------


class TestSHACLValidation:
    def test_valid_graph_passes(self):
        g = CoreMapper(RUN_ID).map(nodes={"region_a": {}})
        cg = Dataset()
        cg.add_graph(g)
        validate(cg, SHAPES)  # must not raise

    def test_invalid_graph_raises(self):
        # Blank node subject violates sh:nodeKind sh:IRI
        bad = Graph(identifier=URIRef(RUN_ID + "/bad"))
        bad.add((BNode(), RDF.type, ONTOCAL.CalliopeThing))
        cg = Dataset()
        cg.add_graph(bad)
        with pytest.raises(ValidationError):
            validate(cg, SHAPES)


# ---------------------------------------------------------------------------
# Round-trip: dict → RDF → SHACL validation → .nq → reload
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_translator_produces_nq_file(self, tmp_path):
        out = tmp_path / "test_output.nq"
        Translator(
            nodes={"test_calliope_thing": {"name": "Test Calliope Thing"}},
            run_id=RUN_ID,
        ).save(out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_nq_file_is_valid_rdf(self, tmp_path):
        out = tmp_path / "test_output.nq"
        Translator(
            nodes={"test_calliope_thing": {"name": "Test Calliope Thing"}},
            run_id=RUN_ID,
        ).save(out)
        loaded = Dataset()
        loaded.parse(str(out), format="nquads")
        entity = URIRef(RUN_ID + "/test_calliope_thing")
        # Search across all named graphs in the dataset
        assert any(
            (entity, RDF.type, ONTOCAL.CalliopeThing) in g
            for g in loaded.graphs()
        )

    def test_nq_contains_default_named_graph(self, tmp_path):
        out = tmp_path / "test_output.nq"
        Translator(nodes={"test_calliope_thing": {}}, run_id=RUN_ID).save(out)
        loaded = Dataset()
        loaded.parse(str(out), format="nquads")
        graph_names = [str(g.identifier) for g in loaded.graphs()]
        assert RUN_ID + "/core" in graph_names

    def test_nq_contains_custom_named_graph(self, tmp_path):
        out = tmp_path / "test_output.nq"
        custom = RUN_ID + "/scenario-high-renewables"
        Translator(nodes={"test_calliope_thing": {}}, run_id=RUN_ID, graph_id=custom).save(out)
        loaded = Dataset()
        loaded.parse(str(out), format="nquads")
        graph_names = [str(g.identifier) for g in loaded.graphs()]
        assert custom in graph_names
        assert RUN_ID + "/core" not in graph_names
