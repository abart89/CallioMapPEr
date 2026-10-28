"""Check an installed distribution from a directory outside the source checkout.

Run with the clean environment's Python and ``-I``. The supplied examples are
saved exports; this script never imports Calliope or runs an optimiser.
"""

import argparse
import csv
import hashlib
from importlib import metadata, resources, util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples", type=Path, required=True,
                        help="Directory containing the genuine stable 0.7.0 examples, manifest and annotations")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    examples = args.examples.resolve()
    os.chdir(output)
    import calliomapper
    from rdflib import Dataset, Graph, RDF, URIRef
    from calliomapper.utils.validation import ValidationError, validate
    from calliomapper.vocabulary import OC, OEO

    package = Path(calliomapper.__file__).resolve().parent
    assert package.is_relative_to(Path(sys.prefix).resolve()), "Imported package is outside the clean environment"
    forbidden = ("calliope", "linkml", "linkml_runtime", "xarray", "netCDF4")
    for name in forbidden:
        assert util.find_spec(name) is None, f"Unexpected runtime dependency: {name}"
    distribution = metadata.distribution("calliomapper")
    installed_files = [str(path) for path in distribution.files]
    assert not any("calliomapper/generated/" in path for path in installed_files)
    resource_root = resources.files("calliomapper").joinpath("resources")
    snapshot = json.loads(resource_root.joinpath("snapshot.json").read_text())
    for name, checksum in snapshot["sha256"].items():
        actual = hashlib.sha256(resource_root.joinpath(name).read_bytes()).hexdigest()
        assert actual == checksum, f"Changed or missing bundled resource: {name}"

    commands, checks = [], []
    fixture_manifest_path = examples / "manifest.json"
    fixture_manifest = json.loads(fixture_manifest_path.read_text())
    assert fixture_manifest["calliope_version"] == "0.7.0"
    for name, fixture in fixture_manifest["examples"].items():
        for filename, checksum in fixture["result_files_sha256"].items():
            actual = hashlib.sha256((examples / name / "results_directory" / filename).read_bytes()).hexdigest()
            assert actual == checksum, f"Changed or missing stable fixture: {name}/{filename}"
    checks.append("Stable reference exports match their independently recorded preparation manifest")
    environment = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    executable = Path(sys.executable).with_name("calliomapper")

    def run(arguments, expected=0):
        command = [str(executable), *map(str, arguments)]
        result = subprocess.run(command, cwd=output, env=environment, capture_output=True, text=True, timeout=180)
        commands.append({"command": command, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        assert result.returncode == expected, f"Command failed: {command}\n{result.stdout}\n{result.stderr}"
        return result

    def load_graph(path):
        return Dataset(default_union=True).parse(str(path), format="nquads")

    reports = {}
    for name, expected_nodes, expected_components in (("national_scale", 5, 15), ("urban_scale", 4, 26)):
        path = output / f"{name}.nq"
        run(["translate", examples / name / "results_directory", "--out", path])
        report = json.loads(Path(str(path) + ".report.json").read_text())
        reports[name] = report
        assert report["nodes"] == expected_nodes and report["components"] == expected_components
        assert report["calliope_format_version"] == "0.7.0" and report["real_fixture_tested_version"]
        assert report["calliope_version"] is None, "An omitted runtime version must remain unknown"
        assert report["calliope_configured_version"] == "0.7.0"
        assert "producing version not recorded" in report["calliope_version_evidence"]
        assert report["shacl"] == "passed"
        graph = load_graph(path)
        assert not list(graph.objects(None, OC.timeIndexLabel)), "Default export expanded time points"
        assert not list(graph.objects(None, OEO.OEO_00040010)), "Default export invented concrete units"
        summaries = set(graph.subjects(RDF.type, OC.AggregatedResultRecord))
        series = set(graph.subjects(RDF.type, OC.TimeSeriesRecord))
        if name == "national_scale":
            assert len(summaries) == len(series) == 13
        else:
            assert not summaries and len(series) == 21
            assert any("custom mathematics" in item["reason"] for item in report["omissions"])
        checks.append(f"{name}: default graph and SHACL validation")

    national = output / "national_scale.nq"
    manifest = Path(str(national) + ".manifest.json")
    structure = output / "structure.nq"
    run(["translate", examples / "national_scale/results_directory", "--out", structure,
         "--groups", "structure", "--identity-file", manifest])
    structure_report = json.loads(Path(str(structure) + ".report.json").read_text())
    assert structure_report["configuration"] == reports["national_scale"]["configuration"]
    assert structure_report["execution"] == reports["national_scale"]["execution"]
    graph = load_graph(structure)
    assert not list(graph.objects(None, OC.reportedNumericValue))
    checks.append("Structure-only selection retains configuration/execution identity and omits quantities")

    selection = output / "time-points.yaml"
    selection.write_text("""- group: inputs
  variable: sink_use_equals
  nodes: region1
  techs: demand_power
  timesteps: ['2005-01-01 00:00:00']
- group: results
  variable: flow_out
  nodes: region1
  techs: ccgt
  carriers: power
  timesteps: ['2005-01-01 00:00:00']
""")
    selected = output / "selected-time-points.nq"
    run(["translate", examples / "national_scale/results_directory", "--out", selected,
         "--groups", "structure", "--time-points", selection])
    graph = load_graph(selected)
    assert len(set(graph.subjects(OC.timeIndexLabel, None))) == 2
    assert not list(graph.subjects(RDF.type, OC.AggregatedResultRecord))
    checks.append("Two explicitly requested time points with no unrequested summaries")

    annotated = output / "annotated.nq"
    run(["translate", examples / "national_scale/results_directory", "--out", annotated,
         "--annotations", examples / "annotations/national.yaml", "--identity-file", manifest])
    graph = load_graph(annotated)
    assert list(graph.triples((None, OC.implementsAssumption, None)))
    assert list(graph.triples((None, OC.hasRationale, None)))
    assert list(graph.triples((None, OEO.OEO_00040010, None)))
    checks.append("Supplied, explicitly labelled example context and evidenced units")

    template = output / "annotations.yaml"
    run(["init-annotations", "--out", template])
    original = template.read_bytes()
    assert b"schema_version: 1" in original
    run(["init-annotations", "--out", template], expected=1)
    assert template.read_bytes() == original
    checks.append("Installed annotation template is created and protected against overwrite")

    answer = output / "installed-capacity.csv"
    run(["query", national, "--preset", "installed_capacity", "--out", answer])
    with answer.open() as stream:
        answers = list(csv.DictReader(stream))
    assert len(answers) == 15
    run(["query", national, "--preset", "unknown"], expected=1)
    checks.append("Installed capacity query returns 15 records; unknown queries fail")

    invalid = Graph()
    for subject, predicate, obj, _ in load_graph(national).quads():
        invalid.add((subject, predicate, obj))
    invalid.remove((URIRef(reports["national_scale"]["execution"]), OC.usesConfiguration, None))
    try:
        validate(invalid)
    except ValidationError:
        checks.append("Installed SHACL rules reject a result without its execution configuration")
    else:
        raise AssertionError("Invalid graph incorrectly passed installed SHACL validation")

    report = {
        "python": platform.python_version(), "platform": platform.platform(),
        "executable": sys.executable, "package_location": str(package),
        "versions": dict(sorted((item.metadata["Name"], item.version) for item in metadata.distributions())),
        "declared_runtime_dependencies": [item for item in distribution.requires or [] if "extra ==" not in item],
        "absent_optional_model_libraries": list(forbidden),
        "generated_modules_shipped": False,
        "verified_resource_count": len(snapshot["sha256"]), "ontology_version": snapshot["ontology_version"],
        "runtime_package_sha256": {
            str(path.relative_to(package)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(package.rglob("*")) if path.is_file() and "__pycache__" not in path.parts
        },
        "checks": checks, "calliope_fixture_versions": [fixture_manifest["calliope_version"]],
        "fixture_preparation_manifest": str(fixture_manifest_path),
        "fixture_preparation_manifest_sha256": hashlib.sha256(fixture_manifest_path.read_bytes()).hexdigest(),
        "version_evidence": "Fixture production version comes from the preparation manifest. The normal CSV exports omit runtime.calliope_version_initialised; their graph and report retain that uncertainty.",
        "stable_calliope_0_7_0_fixture": "passed: genuine national and urban saved exports",
        "owl_reasoning": "not performed by this installation check",
    }
    (output / "installation-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks_passed": len(checks), "resources_verified": report["verified_resource_count"], "versions": report["versions"]}, indent=2))


if __name__ == "__main__":
    main()
