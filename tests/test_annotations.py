"""Supplied context is independently attributed and cannot alter source values."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote

import pytest
import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

from calliomapper.mapper.annotations import AnnotationError, OC, OBO, OEO, PROV, add_annotations

ROOT = Path(__file__).resolve().parents[1]


def context():
    iri = lambda kind, *keys: URIRef("https://example.org/test/" + "/".join(quote(str(key), safe="") for key in (kind, *keys)))
    ctx = SimpleNamespace(graph=Graph(), iri=iri, report={}, configuration=iri("configuration"),
                          model=iri("model"), execution=iri("execution"), nodes={"region1": iri("node", "region1")},
                          components={("region1", "ccgt"): iri("component", "region1", "ccgt"),
                                      ("region2", "battery"): iri("component", "region2", "battery")})
    graph = ctx.graph
    graph.add((ctx.configuration, RDF.type, OC.ConfigurationSpecification))
    graph.add((ctx.execution, RDF.type, PROV.Activity))
    graph.add((ctx.execution, OC.usesConfiguration, ctx.configuration))
    graph.add((ctx.model, RDF.type, OEO.OEO_00000274))
    node = ctx.nodes["region1"]
    graph.add((node, RDF.type, OEO.OEO_00000276))
    for component in ctx.components.values():
        graph.add((component, RDF.type, OEO.OEO_00000276))
        graph.add((component, OC.inConfiguration, ctx.configuration))
    for kind, var, tech, value, carrier in ((OC.InputAssignment, "flow_cap_max", "ccgt", "30000", None),
                                            (OC.ResultRecord, "flow_cap", "ccgt", "30000", "power"),
                                            (OC.InputAssignment, "flow_in_eff", "battery", "0.95", None)):
        record = iri("record", var)
        datum = iri("datum", var)
        graph.add((record, RDF.type, kind))
        graph.add((record, OC.forComponent, ctx.components["region2" if tech == "battery" else "region1", tech]))
        graph.add((record, OC.sourceKey, Literal(var, datatype=XSD.string)))
        graph.add((record, OC.inConfiguration, ctx.configuration))
        graph.add((record, OC.hasDatum, datum))
        graph.add((datum, OC.reportedNumericValue, Literal(value, datatype=XSD.decimal)))
        graph.add((record, OC.quantityDimension, Literal("dimensionless" if var == "flow_in_eff" else "power", datatype=XSD.string)))
        if carrier:
            graph.add((record, OC.carrierIndex, Literal(carrier, datatype=XSD.string)))
            graph.add((record, PROV.wasGeneratedBy, ctx.execution))
            graph.add((ctx.execution, OEO.OEO_00140094, datum))
    return ctx


def annotation(ctx, identifier):
    return ctx.graph.value(predicate=DCTERMS.identifier, object=Literal(identifier, datatype=XSD.string), any=False)


@pytest.fixture
def document():
    return yaml.safe_load((ROOT / "examples/annotations/national.yaml").read_text())


def test_example_preserves_numbers_and_distinguishes_context_from_source_evidence(document):
    ctx = context()
    original = set(ctx.graph.triples((None, OC.reportedNumericValue, None)))
    add_annotations(ctx, document)
    assert original == set(ctx.graph.triples((None, OC.reportedNumericValue, None)))
    scenario = annotation(ctx, "reference_future")
    assumption = annotation(ctx, "capacity_assumption")
    reason = annotation(ctx, "capacity_reason")
    assert (ctx.configuration, OC.implementsScenario, scenario) in ctx.graph
    assert (ctx.iri("record", "flow_cap_max"), OC.implementsAssumption, assumption) in ctx.graph
    assert (assumption, OC.hasRationale, reason) in ctx.graph
    assert (reason, PROV.wasAttributedTo, annotation(ctx, "demonstration_contributor")) in ctx.graph
    assert not list(ctx.graph.objects(annotation(ctx, "unexplained_efficiency_assumption"), OC.hasRationale))
    assert "Synthetic" in str(ctx.graph.value(assumption, OC.evidenceStatus))
    quantity = annotation(ctx, "bound_unit_interpretation")
    assert "Interpretation grounded" in str(ctx.graph.value(quantity, OC.evidenceStatus))
    assert (quantity, PROV.wasDerivedFrom, annotation(ctx, "capacity_comment")) in ctx.graph
    assert ctx.graph.value(quantity, OEO.OEO_00140178).toPython() == 30000
    revision = URIRef("https://example.org/calliomapper/tutorial/dataset/capacity/revision-2")
    assert (ctx.execution, PROV.used, revision) in ctx.graph
    assert (ctx.iri("datum", "flow_cap_max"), PROV.wasDerivedFrom, revision) in ctx.graph
    assert (revision, PROV.wasGeneratedBy, annotation(ctx, "invented_preparation")) in ctx.graph
    target = URIRef("https://example.org/calliomapper/tutorial/proposed-plant-description")
    assert (target, RDF.type, OBO.IAO_0000030) in ctx.graph
    assert (target, RDF.type, OBO.BFO_0000040) not in ctx.graph
    assert ctx.report["annotations"]["assumptions"] == 2


def test_annotation_example_conforms_to_all_bundled_shapes(document):
    import importlib.resources
    from pyshacl import validate
    ctx = context()
    add_annotations(ctx, document)
    # All profiles are tested together; no ontology checkout or inferred fixes.
    resource_root = importlib.resources.files("calliomapper") / "resources"
    paths = list((resource_root / "shapes").iterdir())
    assert len([path for path in paths if path.name.endswith(".ttl")]) == 4
    shapes = Graph()
    for path in paths:
        if path.name.endswith(".ttl"):
            shapes.parse(data=path.read_text(), format="turtle")
    conforms, _, report = validate(ctx.graph, shacl_graph=shapes)
    assert conforms, report


def test_empty_template_does_not_invent_context():
    ctx = context()
    original = set(ctx.graph)
    add_annotations(ctx, ROOT / "calliomapper/templates/annotations.yaml")
    # The empty supplied document has provenance, but adds no scientific claims.
    assert original <= set(ctx.graph)
    assert not list(ctx.graph.subjects(RDF.type, OEO.OEO_00000364))
    assert not list(ctx.graph.subjects(RDF.type, OEO.OEO_00000063))


@pytest.mark.parametrize("change, message", [
    (lambda doc: doc.update(schema_version=2), "schema_version"),
    (lambda doc: doc.update(default_supplier="unknown"), "default_supplier"),
    (lambda doc: doc["study"].update(queston="typo"), "unknown fields"),
    (lambda doc: doc["assumptions"][0]["targets"][0].update(node="missing"), "Unknown component"),
    (lambda doc: doc["units"][0]["target"].update(carriers="nonexistent"), "exactly one"),
    (lambda doc: doc["units"][0].update(evidence=[]), "non-empty"),
    (lambda doc: doc["scenarios"][0].update(implemented_by_configuration="yes"), "true or false"),
    (lambda doc: doc["study"].update(reference_scenario="unknown"), "reference_scenario"),
    (lambda doc: doc["assumptions"][0]["reasons"][0].update(id="capacity_assumption"), "Repeated annotation id"),
    (lambda doc: doc["physical_correspondences"][0].update(kind="real"), "kind must"),
    (lambda doc: doc["datasets"][0].update(evidence=["unknown"]), "unknown evidence"),
])
def test_invalid_document_is_rejected_without_partial_graph_mutation(document, change, message):
    ctx = context()
    original = set(ctx.graph)
    change(document)
    with pytest.raises(AnnotationError, match=message):
        add_annotations(ctx, document)
    assert set(ctx.graph) == original
    assert not ctx.report


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    path = tmp_path / "annotations.yaml"
    path.write_text("schema_version: 1\nschema_version: 1\n")
    with pytest.raises(AnnotationError, match="repeated"):
        add_annotations(context(), path)


def test_ambiguous_carriers_and_second_units_are_rejected(document):
    ctx = context()
    result = ctx.iri("record", "flow_cap")
    other = ctx.iri("other", "flow_cap")
    for _, predicate, value in list(ctx.graph.triples((result, None, None))):
        ctx.graph.add((other, predicate, Literal("heat", datatype=XSD.string) if predicate == OC.carrierIndex else value))
    del document["units"][1]["target"]["carriers"]
    with pytest.raises(AnnotationError, match="found 2"):
        add_annotations(ctx, document)
    document["units"][1]["target"]["carriers"] = "power"
    duplicate = deepcopy(document["units"][0])
    duplicate["id"] = "other_unit"
    document["units"].append(duplicate)
    with pytest.raises(AnnotationError, match="already has"):
        add_annotations(ctx, document)


def test_all_physical_kinds_remain_separate_and_external_pair_is_explicit(document):
    ctx = context()
    actual = deepcopy(document["physical_correspondences"][0])
    actual.update(id="actual_claim", kind="actual", target_uri="https://example.org/actual", target_label="Synthetic actual asset")
    aggregate = deepcopy(actual)
    aggregate.update(id="aggregate_claim", kind="aggregate", target_uri="https://example.org/portfolio", target_label="Synthetic portfolio description")
    document["physical_correspondences"] += [actual, aggregate]
    document["component_correspondences"] = [{"id": "pair", "source": {"node": "region1", "technology": "ccgt"},
        "target": {"uri": "https://another.example/model/component"}, "reason": "Explicit synthetic pairing for a comparison"}]
    add_annotations(ctx, document)
    assert (URIRef(actual["target_uri"]), RDF.type, OBO.BFO_0000040) in ctx.graph
    assert (URIRef(aggregate["target_uri"]), RDF.type, OBO.IAO_0000030) in ctx.graph
    assert (annotation(ctx, "pair"), OC.targetComponent, URIRef("https://another.example/model/component")) in ctx.graph
    assert not list(ctx.graph.triples((None, URIRef("http://www.w3.org/2002/07/owl#sameAs"), None)))


def test_physical_target_cannot_reuse_a_component_or_change_kind(document):
    ctx = context()
    document["physical_correspondences"][0]["target_uri"] = str(ctx.components["region1", "ccgt"])
    with pytest.raises(AnnotationError, match="cannot reuse"):
        add_annotations(ctx, document)
    document["physical_correspondences"][0]["target_uri"] = "https://example.org/physical"
    ctx.graph.add((URIRef("https://example.org/physical"), RDF.type, OBO.BFO_0000040))
    with pytest.raises(AnnotationError, match="material"):
        add_annotations(ctx, document)


@pytest.mark.parametrize("unit_class,label,message", [
    ("https://openenergyplatform.org/ontology/oeo/OEO_00000031", "plant", "Unsupported unit_class"),
    ("http://purl.obolibrary.org/obo/UO_0000224", "kWh", "quantity dimension"),
    ("https://openenergyplatform.org/ontology/oeo/OEO_00390000", "MW", "requires label"),
])
def test_units_require_verified_class_label_and_matching_dimension(document, unit_class, label, message):
    document["units"][0].update(unit_class=unit_class, label=label)
    with pytest.raises(AnnotationError, match=message):
        add_annotations(context(), document)


def test_explicit_study_and_scenario_uris_can_be_shared_across_exports(document):
    study = URIRef("https://example.org/research/study")
    future = URIRef("https://example.org/research/future")
    document["study"]["uri"] = str(study)
    document["scenarios"][0]["uri"] = str(future)
    ctx = context()
    add_annotations(ctx, document)
    assert (study, OBO.BFO_0000051, ctx.execution) in ctx.graph
    assert (study, OC.referenceScenario, future) in ctx.graph
    assert (ctx.configuration, OC.implementsScenario, future) in ctx.graph


def test_national_annotation_file_with_real_default_export_preserves_values():
    from calliomapper import Translator
    plain = Translator(ROOT / "examples/national_scale/results_directory", namespace="https://example.org/integration/")
    annotated = Translator(ROOT / "examples/national_scale/results_directory", namespace="https://example.org/integration/",
                           annotations=ROOT / "examples/annotations/national.yaml")
    plain.translate()
    after = annotated.translate()
    def numerical_records(graph):
        return {(str(graph.value(record, OC.sourceKey)), str(graph.value(record, OC.forComponent)),
                 str(graph.value(record, OC.carrierIndex)), str(graph.value(record, OC.costIndex)),
                 str(graph.value(record, OC.timeIndexLabel)), str(graph.value(datum, OC.reportedNumericValue)))
                for record, datum in graph.subject_objects(OC.hasDatum)}
    # Aggregation activities have new identifiers on each export, while the
    # component, coordinates and numerical content remain the same.
    assert numerical_records(plain.context.graph) == numerical_records(annotated.context.graph)
    assert annotated.report["annotations"]["assumptions"] == 2
    assert len(list(after.subjects(RDF.type, OC.PhysicalCorrespondenceAssertion))) == 1
    assert list(after.triples((None, OC.hasRationale, None)))


@pytest.mark.parametrize("section,field,identifier", [
    ("sources", "uri", "execution"),
    ("agents", "uri", "configuration"),
    ("scenarios", "uri", "model"),
    ("datasets", "revision_uri", "execution"),
    ("physical_correspondences", "target_uri", "execution"),
])
def test_annotation_uris_cannot_reclassify_core_entities(document, section, field, identifier):
    ctx = context()
    document[section][0][field] = str(getattr(ctx, identifier))
    if section == "physical_correspondences":
        document[section][0]["kind"] = "actual"
    original = set(ctx.graph)
    with pytest.raises(AnnotationError, match="cannot reuse"):
        add_annotations(ctx, document)
    assert set(ctx.graph) == original


def test_shared_annotation_uri_cannot_mix_information_and_activity(document):
    document["sources"][0]["uri"] = "https://example.org/one-entity"
    document["study"]["uri"] = "https://example.org/one-entity"
    ctx = context()
    original = set(ctx.graph)
    with pytest.raises(AnnotationError, match="incompatible"):
        add_annotations(ctx, document)
    assert set(ctx.graph) == original


def test_editing_annotation_text_keeps_prior_claim_identifiers_distinct(document):
    first, second = context(), context()
    add_annotations(first, document)
    changed = deepcopy(document)
    changed["assumptions"][0]["reasons"][0]["statement"] = "A different, explicitly supplied explanation."
    add_annotations(second, changed)
    assert annotation(first, "capacity_reason") != annotation(second, "capacity_reason")
    assert first.report["annotation_sha256"] != second.report["annotation_sha256"]


def test_annotation_file_revision_hashes_original_bytes():
    import hashlib
    ctx = context()
    ctx.export_activity = ctx.iri("export-activity")
    path = ROOT / "examples/annotations/national.yaml"
    add_annotations(ctx, path)
    revision = ctx.graph.value(ctx.export_activity, PROV.used)
    assert str(ctx.graph.value(revision, OC.contentSHA256)) == hashlib.sha256(path.read_bytes()).hexdigest()
    assert str(ctx.graph.value(revision, OC.sourcePath)) == "national.yaml"
    assert "canonical parsed JSON" in ctx.report["annotation_digest_representation"]


def test_two_saved_executions_keep_quantity_interpretations_distinct(tmp_path):
    import csv
    import shutil
    from calliomapper import Translator
    from calliomapper.utils.validation import validate
    source = ROOT / "examples/national_scale/results_directory"
    second_source = tmp_path / "synthetic-second-execution"
    shutil.copytree(source, second_source)
    result_path = second_source / "results_flow_cap.csv"
    with result_path.open() as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    for row in rows:
        if row["nodes"] == "region1" and row["techs"] == "ccgt":
            row["flow_cap"] = "29999"
    with result_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    # This changed saved result is a controlled test fixture, not an optimisation.
    first = Translator(source, namespace="https://example.org/repeated/", groups={"capacities"},
                       annotations=ROOT / "examples/annotations/national.yaml")
    second = Translator(second_source, namespace="https://example.org/repeated/", groups={"capacities"},
                        annotations=ROOT / "examples/annotations/national.yaml")
    first.translate()
    second.translate()
    assert first.context.configuration == second.context.configuration
    assert first.context.execution != second.context.execution
    first_quantity = annotation(first.context, "result_unit_interpretation")
    second_quantity = annotation(second.context, "result_unit_interpretation")
    assert first_quantity != second_quantity
    assert first.context.graph.value(first_quantity, OEO.OEO_00140178).toPython() == 30000
    assert second.context.graph.value(second_quantity, OEO.OEO_00140178).toPython() == 29999
    combined = first.context.graph + second.context.graph
    validate(combined)
