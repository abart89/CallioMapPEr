#!/usr/bin/env python3
"""
Standalone validator for ontology/ontocal.yaml.

Usage:
    python scripts/validate_schema.py
    # or, from repo root:
    dev_calliomapper/bin/python scripts/validate_schema.py

Exits 0 and prints "Schema is valid" if all checks pass.
Exits 1 and prints a failure report otherwise.
"""

import os
import subprocess
import sys
import warnings
warnings.filterwarnings("ignore")  # suppress urllib3/requests version mismatch in venv
from pathlib import Path

import yaml
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.linkml_model import SchemaDefinition

REPO_ROOT    = Path(__file__).parent.parent
SCHEMA_PATH  = REPO_ROOT / "ontology" / "ontocal_core.yaml"
INDIVIDUALS  = REPO_ROOT / "ontology" / "individuals.ttl"
GEN_PYTHON   = REPO_ROOT / "dev_calliomapper" / "bin" / "gen-python"

OEO_STUBS      = {"SoftwareFramework", "EnergySystemModel", "ModelComponent", "Optimisation"}
EXTERNAL_SLOTS = {"has_part", "part_of"}

# Suppress the urllib3/requests version mismatch emitted by linkml CLI tools.
_ENV = {**os.environ, "PYTHONWARNINGS": "ignore"}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


# ---------------------------------------------------------------------------

print(f"Validating {SCHEMA_PATH.relative_to(REPO_ROOT)}\n")

# 1. File exists
if not SCHEMA_PATH.exists():
    fail("ontocal.yaml not found")
    sys.exit(1)
ok("file exists")

# 2. Parseable YAML
try:
    with open(SCHEMA_PATH) as f:
        raw: dict = yaml.safe_load(f)
    assert isinstance(raw, dict)
    ok("valid YAML")
except Exception as e:
    fail(f"YAML parse error: {e}")
    sys.exit(1)

# 3. Required header fields
for field in ("id", "name"):
    if field not in raw:
        fail(f"missing top-level '{field}'")
    else:
        ok(f"header '{field}' present")

imports = raw.get("imports", [])
if not any("linkml:types" in str(i) for i in imports):
    fail("'linkml:types' missing from imports — built-in datatypes will be undefined")
else:
    ok("imports linkml:types")

# 4. LinkML SchemaLoader
try:
    schema: SchemaDefinition = yaml_loader.load(str(SCHEMA_PATH), target_class=SchemaDefinition)
    assert schema.name == "ontocal"
    ok("LinkML SchemaLoader accepts schema")
except Exception as e:
    fail(f"LinkML SchemaLoader error: {e}")

# 5. OEO stubs have class_uri
classes = raw.get("classes", {})
for stub in sorted(OEO_STUBS):
    if stub not in classes:
        fail(f"OEO stub '{stub}' missing from classes")
    elif "class_uri" not in classes[stub]:
        fail(f"OEO stub '{stub}' has no class_uri — will be treated as a local ontocal class")
    else:
        ok(f"OEO stub '{stub}' has class_uri")

# 6. External slots have slot_uri
slots = raw.get("slots", {})
for slot in sorted(EXTERNAL_SLOTS):
    if slot not in slots:
        fail(f"slot '{slot}' missing")
    elif "slot_uri" not in slots[slot]:
        fail(f"slot '{slot}' has no slot_uri — will not map to its BFO/OEO property")
    else:
        ok(f"slot '{slot}' has slot_uri")

# 7. Calliope individual typed in individuals.ttl
if not INDIVIDUALS.exists():
    fail("ontology/individuals.ttl not found")
else:
    g = Graph()
    g.parse(INDIVIDUALS, format="turtle")
    calliope = URIRef("https://w3id.org/ontocal/Calliope")
    sw_framework = URIRef("http://openenergy-platform.org/ontology/oeo/OEO_00000382")
    if (calliope, RDF.type, sw_framework) in g:
        ok("ontocal:Calliope typed as oeo:SoftwareFramework in individuals.ttl")
    else:
        fail("ontocal:Calliope not typed as oeo:OEO_00000382 in individuals.ttl")

# 8. gen-python round-trip (output goes to stdout; we capture and discard it)
result = subprocess.run(
    [str(GEN_PYTHON), str(SCHEMA_PATH)],
    capture_output=True,
    text=True,
    env=_ENV,
)
if result.returncode == 0:
    ok("gen-python round-trip succeeded")
else:
    fail(f"gen-python failed:\n    {result.stderr.strip()}")

# ---------------------------------------------------------------------------

print()
if failures:
    print(f"Schema is INVALID  ({len(failures)} failure(s))")
    sys.exit(1)
else:
    print("Schema is valid")
    sys.exit(0)
