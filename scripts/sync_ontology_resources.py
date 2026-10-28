"""Copy a reviewed OntoCal snapshot; never generate or edit its ontology."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sync(source, destination):
    names = ["ontocal.ttl", "catalog-v001.xml"]
    names += [str(path.relative_to(source)) for path in sorted((source / "shapes").glob("*.ttl"))]
    names += [str(path.relative_to(source)) for path in sorted((source / "dependencies/derived").iterdir()) if path.is_file()]
    names += ["dependencies/" + name for name in (
        "oeo-full.owl", "prov-o-20130430.owl", "derive_oeo.py", "derive_prov.py",
        "manifest.json", "attribution-metadata.json", "OEO-CITATION.cff", "OEO-LICENSE-CC0.txt", "OEO-REUSE.toml",
    )]
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    manifest = {
        "ontology_version": "https://w3id.org/ontocal/draft/2026-10-22-stage1",
        "description": "Reviewed local OntoCal snapshot, including our explicitly derived OEO/PROV-O copies; not an upstream release.",
        "sha256": {name: hashlib.sha256((destination / name).read_bytes()).hexdigest() for name in names},
    }
    (destination / "snapshot.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ontology_directory", type=Path)
    args = parser.parse_args()
    sync(args.ontology_directory, Path(__file__).resolve().parents[1] / "calliomapper/resources")
