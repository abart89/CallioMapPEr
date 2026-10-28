"""Demonstrate independent exports of ONE saved execution, with supplied context.

No model is constructed or solved. The two future-scenario descriptions are
invented tutorial context applied to unchanged numerical information. A zero
comparison therefore verifies graph handling; it is not scenario-analysis evidence.
"""

import argparse
import csv
import json
from pathlib import Path

import yaml
from rdflib import Dataset, Literal, RDF, RDFS, URIRef

from calliomapper import Translator
from calliomapper.queries import run_query
from calliomapper.vocabulary import OC, OEO, OBO, PROV, DCT


TUTORIAL = "https://example.org/calliomapper/independent-exports/"


def annotations_for(producer, annotations_path):
    document = yaml.safe_load(Path(annotations_path).read_text())
    document["default_evidence_status"] = (
        "Synthetic context for two independent exports of the SAME saved Calliope execution. "
        "No alternative scenario was simulated and the numerical values were not changed."
    )
    document["scenarios"] = [
        {
            "id": name, "uri": TUTORIAL + name,
            "label": f"Invented {name.replace('_', ' ')}",
            "description": "Illustrative supplied future scenario. Both exports reuse identical numerical information; no scenario experiment was performed.",
            "implemented_by_configuration": name == ("reference_future" if producer == "a" else "alternative_future"),
            "evidence": ["invented_report"],
        }
        for name in ("reference_future", "alternative_future")
    ]
    document["study"].update({
        "uri": TUTORIAL + "study", "title": "Synthetic study for testing independently identified exports",
        "question": "Can explicitly paired records from two exports of one saved execution be compared without merging their identities?",
        "scenarios": ["reference_future", "alternative_future"], "reference_scenario": "reference_future",
    })
    for assumption in document["assumptions"]:
        assumption["scenario"] = "reference_future" if producer == "a" else "alternative_future"
    return document


def copy_dataset(source):
    result = Dataset(default_union=True)
    for subject, predicate, value, graph in source.quads():
        result.graph(graph).add((subject, predicate, value))
    return result


def write_answers(dataset, preset, destination):
    result = run_query(dataset, preset)
    rows = list(result)
    with destination.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(result.vars)
        writer.writerows([[str(value) if value is not None else "" for value in row] for row in rows])
    return rows


def build_demo(destination, results_directory=None, annotations_path=None):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    examples = Path(__file__).resolve().parents[1] / "calliope-0.7.0-glpk"
    source = Path(results_directory) if results_directory else examples / "national_scale/results_directory"
    annotations_path = annotations_path or examples / "annotations/national.yaml"
    source_exports = {}
    for producer in ("a", "b"):
        translator = Translator(source, groups={"structure", "capacities"})
        translator.save(destination / f"source-{producer}.nq")
        source_exports[producer] = translator
    annotations = {producer: annotations_for(producer, annotations_path) for producer in ("a", "b")}
    target = source_exports["b"].context.components["region1", "ccgt"]
    annotations["a"]["component_correspondences"] = [{
        "id": "explicit_ccgt_pair", "source": {"node": "region1", "technology": "ccgt"},
        "target": {"uri": str(target)},
        "reason": "Explicit tutorial pairing of two independently identified representations of the same saved component, not a name-based identity inference.",
        "evidence": ["invented_report"],
    }]
    annotated = {}
    combined = Dataset(default_union=True)
    for producer in ("a", "b"):
        annotation_path = destination / f"annotations-{producer}.yaml"
        annotation_path.write_text(yaml.safe_dump(annotations[producer], sort_keys=False))
        translator = Translator(source, groups={"structure", "capacities"}, annotations=annotation_path,
                                identity_file=destination / f"source-{producer}.nq.manifest.json")
        output_path = destination / f"annotated-{producer}.nq"
        translator.save(output_path)
        annotated[producer] = translator
        combined.parse(str(output_path), format="nquads")
    catalogue = Dataset(default_union=True)
    catalogue_graph = catalogue.graph(URIRef(TUTORIAL + "catalogue-graph"))
    revision = URIRef(annotations["a"]["datasets"][0]["revision_uri"])
    publisher = URIRef(TUTORIAL + "fictional-publisher")
    catalogue_graph.add((revision, DCT.publisher, publisher))
    catalogue_graph.add((revision, RDF.type, PROV.Entity))
    catalogue_graph.add((publisher, RDF.type, PROV.Agent))
    catalogue_graph.add((publisher, RDFS.label, Literal("Fictional publisher for the integration example")))
    catalogue_graph.add((catalogue_graph.identifier, OC.evidenceStatus, Literal("Synthetic catalogue metadata; no actual publisher is asserted.")))
    catalogue_path = destination / "catalogue.nq"
    catalogue.serialize(destination=catalogue_path, format="nquads")
    combined.parse(str(catalogue_path), format="nquads")
    combined.serialize(destination=destination / "combined.nq", format="nquads")
    comparison = write_answers(combined, "cq06", destination / "cq06-comparison.csv")
    integration = write_answers(combined, "cq07", destination / "cq07-integration.csv")

    # These deliberately edited copies test refusal; they are never saved as valid exports.
    bad_units = copy_dataset(combined)
    component_b = annotated["b"].context.components["region1", "ccgt"]
    result_b = next(record for record in bad_units.subjects(OC.forComponent, component_b)
                    if (record, RDF.type, OC.ResultRecord) in bad_units and str(bad_units.value(record, OC.sourceKey)) == "flow_cap")
    datum = bad_units.value(result_b, OC.hasDatum)
    quantity = bad_units.value(datum, OBO.IAO_0000136)
    unit = bad_units.value(quantity, OEO.OEO_00040010)
    bad_units.remove((unit, RDF.type, OEO.OEO_00390000))
    bad_units.graph(URIRef(TUTORIAL + "deliberately-invalid-units")).add((unit, RDF.type, OEO.OEO_00390001))
    bad_units.remove((unit, RDFS.label, None))
    bad_units.graph(URIRef(TUTORIAL + "deliberately-invalid-units")).add((unit, RDFS.label, Literal("MW")))
    missing_units = copy_dataset(combined)
    missing_units.remove((quantity, OEO.OEO_00040010, unit))
    bad_horizon = copy_dataset(combined)
    horizon_b = bad_horizon.value(annotated["b"].context.configuration, OC.hasTemporalDescription)
    bad_horizon.remove((horizon_b, OC.lastIndexLabel, None))
    bad_horizon.graph(URIRef(TUTORIAL + "deliberately-invalid-horizon")).add((horizon_b, OC.lastIndexLabel, Literal("2099-01-01")))

    checks = {
        "distinct_component_identifiers": annotated["a"].context.components["region1", "ccgt"] != component_b,
        "same_saved_execution_digest": source_exports["a"].source.execution_digest == source_exports["b"].source.execution_digest,
        "source_only_has_no_assumption_answers": not list(run_query(source_exports["a"].translate(), "cq05")),
        "one_explicit_comparison_with_zero_differences": len(comparison) == 1 and comparison[0].inputDifference.toPython() == 0 and comparison[0].resultDifference.toPython() == 0,
        "integration_retains_both_export_run_identifiers": {row.run for row in integration} == {annotated["a"].context.execution, annotated["b"].context.execution},
        "different_units_refused": not list(run_query(bad_units, "cq06")),
        "missing_unit_refused": not list(run_query(missing_units, "cq06")),
        "different_horizon_refused": not list(run_query(bad_horizon, "cq06")),
    }
    report = {"interpretation": __doc__.strip(), "checks": checks,
              "comparison_rows": len(comparison), "integration_rows": len(integration),
              "source_format_versions": {producer: translator.source.version for producer, translator in annotated.items()},
              "recorded_producing_versions": {producer: translator.source.recorded_version for producer, translator in annotated.items()}}
    (destination / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
    if not all(checks.values()):
        raise RuntimeError(f"Demonstration checks failed: {[name for name, passed in checks.items() if not passed]}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--results-directory", type=Path)
    parser.add_argument("--annotations", type=Path, help="Annotation document appropriate to the selected saved example.")
    arguments = parser.parse_args()
    report = build_demo(arguments.destination, arguments.results_directory, arguments.annotations)
    print(f"Wrote examples, annotation files and query answers to {arguments.destination}. {len(report['checks'])} checks passed.")
