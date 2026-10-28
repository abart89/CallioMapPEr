"""Independent synthetic expectations for reusable questions and refusal cases."""

from decimal import Decimal

import pytest
from rdflib import Dataset, Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD

from calliomapper.queries import QUERY_REQUIREMENTS, run_query
from calliomapper.vocabulary import OC, OEO, OBO, PROV, DCT

A = Namespace("https://example.org/query-test/a/")
B = Namespace("https://example.org/query-test/b/")
C = Namespace("https://example.org/query-test/context/")
CAT = Namespace("https://example.org/query-test/catalogue/")


@pytest.fixture
def dataset():
    """Invented data patterned after OntoCal's two-export worked example."""
    dataset = Dataset(default_union=False)
    context = dataset.graph(URIRef("urn:query-test:context"))
    catalogue = dataset.graph(URIRef("urn:query-test:catalogue"))
    for namespace, input_number, result_number, scenario in ((A, 30, 28, C.reference), (B, 25, 24, C.alternative)):
        graph = dataset.graph(URIRef(f"urn:query-test:{'a' if namespace == A else 'b'}"))
        triples = [
            (namespace.model, RDF.type, OEO.OEO_00000274),
            (namespace.node, RDF.type, OEO.OEO_00000276),
            (namespace.node, OC.sourceKey, Literal("region")),
            (namespace.component, RDF.type, OEO.OEO_00000276),
            (namespace.component, RDF.type, OC.CalliopeSupplyTechnology),
            (namespace.component, OC.sourceKey, Literal("same-local-name")),
            (namespace.component, OC.atNode, namespace.node),
            (namespace.component, OC.inConfiguration, namespace.configuration),
            (namespace.component, OC.carrierOut, Literal("electricity")),
            (namespace.run, RDF.type, OEO.OEO_00000275),
            (namespace.run, OC.usesConfiguration, namespace.configuration),
            (namespace.run, OC.executionStatus, Literal("solved")),
            (namespace.run, OBO.RO_0000057, namespace.model),
            (namespace.run, OEO.OEO_00140094, namespace.resultDatum),
            (namespace.run, PROV.wasAssociatedWith, namespace.solver),
            (namespace.solver, RDF.type, PROV.SoftwareAgent),
            (namespace.configuration, OC.hasTemporalDescription, C.horizon),
            (namespace.bound, RDF.type, OC.InputAssignment),
            (namespace.bound, OC.inConfiguration, namespace.configuration),
            (namespace.bound, OC.forComponent, namespace.component),
            (namespace.bound, OC.sourceKey, Literal("flow_cap_max")),
            (namespace.bound, OC.hasDatum, namespace.inputDatum),
            (namespace.inputDatum, OC.reportedNumericValue, Literal(Decimal(input_number))),
            (namespace.inputDatum, OBO.IAO_0000136, namespace.inputQuantity),
            (namespace.inputDatum, OEO.OEO_00020189, namespace.run),
            (namespace.inputQuantity, RDF.type, OEO.OEO_00000350),
            (namespace.inputQuantity, OEO.OEO_00040010, namespace.unit),
            (namespace.result, RDF.type, OC.ResultRecord),
            (namespace.result, OC.inConfiguration, namespace.configuration),
            (namespace.result, OC.forComponent, namespace.component),
            (namespace.result, OC.sourceKey, Literal("flow_cap")),
            (namespace.result, OC.carrierIndex, Literal("electricity")),
            (namespace.result, OC.hasDatum, namespace.resultDatum),
            (namespace.result, PROV.wasGeneratedBy, namespace.run),
            (namespace.resultDatum, OC.reportedNumericValue, Literal(Decimal(result_number))),
            (namespace.resultDatum, OBO.IAO_0000136, namespace.resultQuantity),
            (namespace.resultQuantity, RDF.type, OEO.OEO_00000350),
            (namespace.resultQuantity, OEO.OEO_00040010, namespace.unit),
            (namespace.unit, RDF.type, OEO.OEO_00390000),
            (namespace.unit, RDFS.label, Literal("kW")),
        ]
        for triple in triples:
            graph.add(triple)
        # Supplied context deliberately lives outside the numerical export graph.
        for triple in [
            (namespace.run, OBO.BFO_0000050, C.study),
            (namespace.run, PROV.used, CAT.weatherRevision2),
            (namespace.configuration, OC.implementsScenario, scenario),
            (namespace.bound, OC.implementsAssumption, namespace.assumption),
            (namespace.assumption, RDFS.comment, Literal(f"Synthetic bound {input_number}")),
            (namespace.assumption, PROV.wasAttributedTo, namespace.author),
            (graph.identifier, PROV.wasGeneratedBy, namespace.translation),
            (namespace.translation, PROV.wasAssociatedWith, namespace.exportSoftware),
            (graph.identifier, PROV.wasAttributedTo, namespace.author),
        ]:
            context.add(triple)
    for triple in [
        (C.study, RDF.type, OEO.OEO_00010252),
        (C.study, DCT.title, Literal("Synthetic comparison study")),
        (C.study, OC.referenceScenario, C.reference),
        (C.study, OEO.OEO_00020226, C.reference),
        (C.study, OEO.OEO_00020226, C.alternative),
        (C.studyDescription, OBO.IAO_0000136, C.study),
        (C.studyDescription, DCT.description, Literal("How do these invented values differ?")),
        (C.horizon, OC.firstIndexLabel, Literal("2030-01-01")),
        (C.horizon, OC.lastIndexLabel, Literal("2030-01-02")),
        (C.horizon, OC.indexCount, Literal(2)),
        (C.correspondence, RDF.type, OC.ComponentCorrespondence),
        (C.correspondence, OC.sourceComponent, A.component),
        (C.correspondence, OC.targetComponent, B.component),
        (C.correspondence, PROV.wasAttributedTo, A.author),
        (A.assumption, OC.hasRationale, A.reason),
        (A.reason, RDFS.comment, Literal("An explicitly invented justification.")),
        (A.reason, PROV.wasAttributedTo, A.author),
        (A.reason, DCT.references, C.report),
        (C.physicalClaim, RDF.type, OC.PhysicalCorrespondenceAssertion),
        (C.physicalClaim, OC.forComponent, A.component),
        (C.physicalClaim, OC.correspondenceKind, Literal("hypothetical")),
        (C.physicalClaim, OC.correspondenceTarget, C.proposedAssetDescription),
        (C.physicalClaim, OC.correspondenceScope, Literal("Illustrative capacity only")),
        (C.physicalClaim, PROV.wasAttributedTo, A.author),
        (C.physicalClaim, PROV.wasDerivedFrom, C.report),
    ]:
        context.add(triple)
    catalogue.add((CAT.weatherRevision2, DCT.publisher, CAT.publisher))
    catalogue.add((CAT.weatherRevision1, DCT.publisher, CAT.publisher))
    return dataset


def test_all_eight_queries_have_independent_expected_answers(dataset):
    assert len(list(run_query(dataset, "cq01"))) == 2
    contexts = list(run_query(dataset, "cq02"))
    assert {str(row.role) for row in contexts} == {"reference", "alternative"}
    quantities = list(run_query(dataset, "cq03"))
    assert {row.value.toPython() for row in quantities} == {Decimal(30), Decimal(25), Decimal(28), Decimal(24)}
    provenance = list(run_query(dataset, "cq04"))
    assert any(row.entity == A.result and row.activity == A.run for row in provenance)
    justifications = list(run_query(dataset, "cq05"))
    assert len(justifications) == 2
    assert {row.assignment for row in justifications if row.reason is None} == {B.bound}
    comparison, = run_query(dataset, "cq06")
    assert comparison.inputDifference.toPython() == Decimal(-5)
    assert comparison.resultDifference.toPython() == Decimal(-4)
    integration = list(run_query(dataset, "cq07"))
    assert {row.run for row in integration} == {A.run, B.run}
    assert {row.dataset for row in integration} == {CAT.weatherRevision2}
    correspondence = list(run_query(dataset, "cq08"))
    assert len(correspondence) == 4
    assert {row.component for row in correspondence if row.assertion} == {A.component}


def test_named_graphs_are_preserved_and_parameters_filter_by_value(dataset):
    names = {graph.identifier for graph in dataset.graphs()}
    assert len(list(run_query(dataset, "cq01", {"component": A.component}))) == 1
    assert len(list(run_query(dataset, "cq03", {"variable": Literal("flow_cap", datatype=XSD.string)}))) == 2
    assert len(list(run_query(dataset, "cq03", {"technology": "same-local-name"}))) == 4
    assert {graph.identifier for graph in dataset.graphs()} == names
    assert dataset.default_union is True


def test_comparison_requires_explicit_component_pairing(dataset):
    dataset.remove((C.correspondence, OC.sourceComponent, A.component))
    assert not list(run_query(dataset, "cq06"))


@pytest.mark.parametrize("failure", ["unit", "carrier", "missing_unit", "execution"])
def test_comparison_refuses_incompatible_or_missing_information(dataset, failure):
    graph = dataset.graph(URIRef("urn:query-test:b"))
    if failure == "unit":
        graph.remove((B.unit, RDF.type, OEO.OEO_00390000))
        graph.add((B.unit, RDF.type, OEO.OEO_00390001))
        graph.set((B.unit, RDFS.label, Literal("MW")))
    elif failure == "carrier":
        graph.set((B.result, OC.carrierIndex, Literal("heat")))
    elif failure == "missing_unit":
        graph.remove((B.resultQuantity, OEO.OEO_00040010, B.unit))
    else:
        graph.set((B.run, OC.executionStatus, Literal("failed")))
    assert not list(run_query(dataset, "cq06"))


def test_distinct_horizons_need_full_matching_temporal_files(dataset):
    context = dataset.graph(URIRef("urn:query-test:context"))
    graph_b = dataset.graph(URIRef("urn:query-test:b"))
    graph_b.set((B.configuration, OC.hasTemporalDescription, B.horizon))
    for predicate in (OC.firstIndexLabel, OC.lastIndexLabel, OC.indexCount):
        context.add((B.horizon, predicate, context.value(C.horizon, predicate)))
    assert not list(run_query(dataset, "cq06"))
    for namespace, horizon in ((A, C.horizon), (B, B.horizon)):
        for variable, checksum in (("weights", "a" * 64), ("resolution", "b" * 64)):
            revision = namespace[f"{variable}Revision"]
            context.add((horizon, OC.sourceRevision, revision))
            context.add((revision, OC.sourcePath, Literal(f"inputs_timestep_{variable}.csv")))
            context.add((revision, OC.contentSHA256, Literal(checksum)))
    assert len(list(run_query(dataset, "cq06"))) == 1
    context.set((B.weightsRevision, OC.contentSHA256, Literal("c" * 64)))
    assert not list(run_query(dataset, "cq06"))


def test_integration_joins_revision_identity_not_repeated_labels(dataset):
    rows = list(run_query(dataset, "cq07", {"dataset": CAT.weatherRevision1}))
    assert rows == []
    assert len(list(run_query(dataset, "cq07", {"dataset": CAT.weatherRevision2}))) == 2


def test_source_revision_without_recorded_generation_does_not_invent_an_activity(dataset):
    context = dataset.graph(URIRef("urn:query-test:context"))
    context.add((A.inputDatum, OC.sourceRevision, A.fileRevision))
    rows = list(run_query(dataset, "cq04", {"entity": A.inputDatum}))
    assert len(rows) == 1
    assert rows[0].activity is None and rows[0].agent is None
    assert str(rows[0].sourceRelation) == "sourceRevision"


def test_capacity_and_cost_aliases_are_filtered_without_inventing_totals(dataset):
    assert {row.value.toPython() for row in run_query(dataset, "installed_capacity")} == {Decimal(28), Decimal(24)}
    assert not list(run_query(dataset, "system_costs"))
    graph = dataset.graph(URIRef("urn:query-test:a"))
    for triple in [
        (A.cost, RDF.type, OC.ResultRecord), (A.cost, OC.inConfiguration, A.configuration),
        (A.cost, OC.forComponent, A.component), (A.cost, OC.sourceKey, Literal("cost")),
        (A.cost, OC.costIndex, Literal("monetary")), (A.cost, OC.hasDatum, A.costDatum),
        (A.costDatum, OC.reportedNumericValue, Literal(Decimal("42"))),
    ]:
        graph.add(triple)
    cost, = run_query(dataset, "system_costs")
    assert cost.value.toPython() == 42 and cost.unit is None


def test_missing_context_remains_missing_and_query_requirements_explain_it(dataset):
    for graph in list(dataset.graphs()):
        if graph.identifier in {URIRef("urn:query-test:context"), URIRef("urn:query-test:catalogue")}:
            dataset.remove_graph(graph.identifier)
    assert not list(run_query(dataset, "cq05"))
    assert not list(run_query(dataset, "cq06"))
    assert not list(run_query(dataset, "cq07"))
    assert all(row.study is None for row in run_query(dataset, "cq02"))
    assert all(row.assertion is None for row in run_query(dataset, "cq08"))
    assert "supplied" in QUERY_REQUIREMENTS["cq05"]


def test_query_name_and_parameter_errors_are_explicit(dataset):
    with pytest.raises(ValueError, match="Unknown query"):
        run_query(dataset, "not-a-question")
    with pytest.raises(ValueError, match="Unknown query variables"):
        run_query(dataset, "cq01", {"typo": "x"})
    with pytest.raises(ValueError, match="Dataset"):
        run_query(Graph(), "cq07")


def test_worked_example_uses_actual_saved_exports_and_rejects_invalid_comparisons(tmp_path):
    import runpy
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "examples/annotations/compare_exports.py"
    demonstration = runpy.run_path(str(script))
    report = demonstration["build_demo"](tmp_path)
    assert all(report["checks"].values())
    assert report["comparison_rows"] == 1
    assert report["source_format_versions"] == {"a": "0.7.0", "b": "0.7.0"}
    assert report["recorded_producing_versions"] == {"a": None, "b": None}
    assert (tmp_path / "annotations-a.yaml").is_file()
    assert (tmp_path / "annotations-b.yaml").is_file()
    assert (tmp_path / "cq06-comparison.csv").is_file()
    assert (tmp_path / "cq07-integration.csv").is_file()
