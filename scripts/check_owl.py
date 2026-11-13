#!/usr/bin/env python3
"""Check generated examples with the bundled imports and ROBOT/HermiT.

Run after installing CallioMapper, with Java and ROBOT available. This developer
check uses the stable 0.7.0 examples by default and writes evidence under
build/evaluation/stable-0.7.0-glpk/owl; ordinary export needs neither.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import yaml

from rdflib import Graph, RDF, URIRef
from calliomapper import Translator
from calliomapper.vocabulary import OBO, OEO, OC

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--robot", default=shutil.which("robot"))
    parser.add_argument("--examples", type=Path, default=ROOT / "examples/calliope-0.7.0-glpk",
                        help="Directory containing national_scale, urban_scale and annotations/national.yaml")
    parser.add_argument("--out", type=Path, default=ROOT / "build/evaluation/stable-0.7.0-glpk/owl")
    args = parser.parse_args()
    if not args.robot:
        parser.error("ROBOT is required; supply --robot /path/to/robot")
    out = args.out.resolve()
    examples = args.examples.resolve()
    out.mkdir(parents=True, exist_ok=True)
    resources = Path(str(files("calliomapper") / "resources"))
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "scope": "Generated national supplier-only, national with explicit fictional authors/contributors, and urban default graphs, with unchanged OEO and the bundled OntoCal",
              "examples_directory": str(examples), "source_formats": {},
              "checks": [], "input_sha256": {},
              "interpretation": "False expected type checks establish non-entailment; the separate negative cases test OWL inconsistency."}

    def save_report():
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    def command(name, arguments, *, expect_inconsistent=False, executable=None):
        invocation = [str(executable or args.robot), *map(str, arguments)]
        try:
            result = subprocess.run(invocation, capture_output=True, text=True, timeout=300)
            log = result.stdout + result.stderr
            (out / f"{name}.log").write_text(log)
            passed = (result.returncode == 0 and "CONSISTENT\tfalse" in log) if expect_inconsistent else result.returncode == 0
            report["checks"].append({"name": name, "status": "passed" if passed else "failed",
                                     "command": invocation, "exit_code": result.returncode,
                                     "expected_inconsistency": expect_inconsistent, "log": f"{name}.log"})
        except subprocess.TimeoutExpired as exc:
            log = (exc.stdout or b"") + (exc.stderr or b"")
            (out / f"{name}.log").write_bytes(log)
            report["checks"].append({"name": name, "status": "unexecuted to completion", "reason": "300-second timeout", "command": invocation})
            passed = False
        save_report()
        print(f"{name}: {report['checks'][-1]['status']}", flush=True)
        if not passed:
            raise RuntimeError(f"{name} did not meet its expected outcome; see {out / (name + '.log')}")

    version = subprocess.run([str(args.robot), "--version"], capture_output=True, text=True, check=True)
    report["robot"] = version.stdout.strip()
    combined = Graph()
    contexts = {}
    inputs = [examples / "annotations/national.yaml", Path(__file__), ROOT / "scripts/CheckGeneratedOWL.java"]
    if (examples / "manifest.json").is_file():
        inputs.append(examples / "manifest.json")
    # These extra facts are explicitly fictional. The saved model data and the
    # supplier-only tutorial remain unchanged.
    role_document = yaml.safe_load((examples / "annotations/national.yaml").read_text())
    role_document["agents"].extend([
        {"id": "original_author", "kind": "person", "label": "Fictional original report author"},
        {"id": "annotation_software", "kind": "software", "label": "Fictional annotation-creation software"},
    ])
    role_document["sources"][0]["authors"] = ["original_author"]
    role_document["assumptions"][0]["reasons"][0]["contributor"] = ["demonstration_contributor", "annotation_software"]
    role_document["study"]["responsible"] = "original_author"
    role_document["study"]["participants"] = ["annotation_software"]
    role_annotations = out / "fictional-author-and-contributor-annotations.yaml"
    role_annotations.write_text(yaml.safe_dump(role_document, sort_keys=False))
    inputs.append(role_annotations)
    cases = (("national_scale", "national_scale", examples / "annotations/national.yaml"),
             ("urban_scale", "urban_scale", None),
             ("national_with_roles", "national_scale", role_annotations))
    for example, source_example, annotation in cases:
        source = examples / source_example / "results_directory"
        translator = Translator(source, annotations=annotation, namespace=f"https://example.org/ontology-check/{example}/")
        dataset = translator.translate()
        for triple in dataset.triples((None, None, None)):
            combined.add(triple)
        contexts[example] = translator.context
        saved = translator.context.source
        report["source_formats"][example] = {
            "format_version": saved.version, "recorded_initialisation_version": saved.recorded_version,
            "configured_version": saved.configured_version, "version_evidence": saved.version_evidence,
        }
        inputs.extend(path for path in source.iterdir() if path.is_file())
    inputs.extend(path for path in resources.rglob("*") if path.is_file())
    inputs.extend(path for path in (ROOT / "calliomapper").rglob("*.py"))
    for path in inputs:
        report["input_sha256"][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    combined.serialize(out / "asserted.ttl", format="turtle")
    report["asserted_triples"] = len(combined)
    save_report()
    command("merge", ["merge", "--catalog", resources / "catalog-v001.xml", "--input", resources / "ontocal.ttl",
                      "--input", out / "asserted.ttl", "--collapse-import-closure", "true", "--output", out / "merged.owl"])
    command("profile", ["validate-profile", "--input", out / "merged.owl", "--profile", "DL", "--output", out / "profile.txt"])
    # The ROBOT jar supplies OWLAPI/HermiT. Check the full generated ABox,
    # local class satisfiability and selected entailments without materialising
    # every individual type or class in the imported ontology hierarchy.
    jar = Path(args.robot).resolve().with_name("robot.jar")
    classes = out / "java"
    classes.mkdir(exist_ok=True)
    command("compile-helper", ["-cp", jar, "-d", classes, ROOT / "scripts/CheckGeneratedOWL.java"], executable="javac")
    ctx = contexts["national_scale"]
    component = ctx.components["region1", "ccgt"]
    scenario = next(ctx.graph.subjects(RDF.type, OEO.OEO_00000364))
    study = next(ctx.graph.subjects(RDF.type, OEO.OEO_00010252))
    summary = next(ctx.graph.subjects(RDF.type, OC.AggregatedResultRecord))
    targets = [
        (True, ctx.execution, OBO.BFO_0000015, "execution is a process"),
        (False, ctx.execution, OBO.IAO_0000030, "execution is not an information artifact"),
        (True, ctx.configuration, OBO.BFO_0000002, "configuration is a continuant"),
        (False, ctx.configuration, OBO.BFO_0000015, "configuration is not a process"),
        (True, component, OBO.BFO_0000002, "model component is a continuant"),
        (False, component, OBO.BFO_0000040, "model component is not a material entity"),
        (True, scenario, OBO.IAO_0000030, "scenario is an information artifact"),
        (False, scenario, OBO.BFO_0000040, "scenario is not a material entity"),
        (True, study, OBO.BFO_0000015, "study is a process"),
        (False, study, OBO.IAO_0000030, "study is not its information description"),
        (True, summary, OBO.IAO_0000030, "summary is an information artifact"),
        (False, summary, OBO.BFO_0000015, "summary is not its aggregation activity"),
    ]
    target_file = out / "targets.tsv"
    target_file.write_text("".join("\t".join([str(expected).lower(), str(subject), str(cls), label]) + "\n"
                                   for expected, subject, cls, label in targets))
    java_prefix = ["-Xmx2G", "-cp", str(jar) + os.pathsep + str(classes), "CheckGeneratedOWL"]
    command("reason", [*java_prefix, out / "merged.owl", "positive", target_file, out / "selected-inferred.ttl"], executable="java")
    observations = [line.split("\t") for line in (out / "reason.log").read_text().splitlines()]
    report["local_class_satisfiability"] = [row for row in observations if row[0] == "SATISFIABLE"]
    report["selected_entailments"] = [row for row in observations if row[0] == "ENTAILMENT"]
    if len(report["local_class_satisfiability"]) != 14 or len(report["selected_entailments"]) != len(targets):
        raise RuntimeError("The helper did not report the complete expected class/entailment checks")
    negatives = {
        "execution-as-material": contexts["national_scale"].execution,
        "hypothetical-description-as-material": URIRef("https://example.org/calliomapper/tutorial/proposed-plant-description"),
    }
    for name, subject in negatives.items():
        invalid = Graph()
        invalid.add((subject, RDF.type, OBO.BFO_0000040))
        invalid.serialize(out / f"{name}.ttl", format="turtle")
        command(f"{name}-merge", ["merge", "--input", out / "merged.owl", "--input", out / f"{name}.ttl", "--output", out / f"{name}.owl"])
        command(f"{name}-profile", ["validate-profile", "--input", out / f"{name}.owl", "--profile", "DL", "--output", out / f"{name}-profile.txt"])
        command(f"{name}-reason", [*java_prefix, out / f"{name}.owl", "negative"], expect_inconsistent=True, executable="java")
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    report["status"] = "passed"
    save_report()
    print(f"Evidence: {out / 'report.json'}")


if __name__ == "__main__":
    main()
