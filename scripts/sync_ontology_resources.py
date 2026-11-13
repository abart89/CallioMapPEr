"""Copy a reviewed OntoCal snapshot; never generate or edit its ontology."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from rdflib import Graph, OWL, RDF


def sync(source, destination):
    ontology = Graph().parse(source / "ontocal.ttl")
    ontology_id = next(ontology.subjects(RDF.type, OWL.Ontology))
    version = str(ontology.value(ontology_id, OWL.versionIRI))
    if set(map(str, ontology.objects(ontology_id, OWL.imports))) != {
        "https://openenergyplatform.org/ontology/oeo/releases/2.12.0/oeo.owl"
    }:
        raise ValueError("This package snapshot must import the unchanged OEO 2.12.0 release only")
    names = ["ontocal.ttl", "catalog-v001.xml"]
    names += [str(path.relative_to(source)) for path in sorted((source / "shapes").glob("*.ttl"))]
    names += ["dependencies/" + name for name in (
        "oeo-full.owl", "OEO-CITATION.cff", "OEO-LICENSE-CC0.txt", "OEO-REUSE.toml",
    )]
    upstream = json.loads((source / "dependencies/manifest.json").read_text())
    bundled = {Path(name).name for name in names if name.startswith("dependencies/")}
    records = [record for record in upstream["files"] if record["path"] in bundled]
    for record in records:
        actual = hashlib.sha256((source / "dependencies" / record["path"]).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            raise ValueError(f"Changed upstream dependency: {record['path']}")
    if {record["path"] for record in records} != bundled:
        raise ValueError("A bundled dependency is missing from the source provenance record")
    # Remove only files listed by the previous generated snapshot. Their history
    # remains in Git and in the ontology repository's earlier investigation.
    previous = destination / "snapshot.json"
    if previous.is_file():
        for name in json.loads(previous.read_text())["sha256"]:
            if name not in names:
                (destination / name).unlink(missing_ok=True)
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    dependency_manifest = {
        "oeo_version": upstream["oeo_version"],
        "retrieved_utc": upstream["retrieved_utc"],
        "files": records,
        "notes": ["These are unchanged upstream files. The merged OEO release includes its BFO/IAO/RO dependencies and has no further imports."],
    }
    (destination / "dependencies/manifest.json").write_text(json.dumps(dependency_manifest, indent=2) + "\n")
    names.append("dependencies/manifest.json")
    manifest = {
        "ontology_version": version,
        "description": "OntoCal local first-version candidate with unchanged OEO 2.12.0; no PROV dependency. This is not a published OntoCal release.",
        "sha256": {name: hashlib.sha256((destination / name).read_bytes()).hexdigest() for name in names},
    }
    (destination / "snapshot.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ontology_directory", type=Path)
    args = parser.parse_args()
    sync(args.ontology_directory, Path(__file__).resolve().parents[1] / "calliomapper/resources")
