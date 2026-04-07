#!/usr/bin/env python3
"""
Standalone validator for ontology/ontocal_core.yaml.

Checks:
  1. File exists and is valid YAML
  2. Required header fields present
  3. LinkML SchemaLoader accepts the schema
  4. Every external class_uri / slot_uri resolves to a real IRI in oeo-full.yaml
     (covers OEO, BFO, IAO, RO — anything imported by oeo-full)
  5. Calliope individual typed correctly in ontocal_individuals.ttl
  6. gen-python round-trip

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
warnings.filterwarnings("ignore")
from pathlib import Path

import yaml
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.linkml_model import SchemaDefinition

REPO_ROOT      = Path(__file__).parent.parent
SCHEMA_PATH    = REPO_ROOT / "ontology" / "ontocal_core.yaml"
OEO_FULL_PATH  = REPO_ROOT / "docs" / "ontologies" / "oeo-full.yaml"
INDIVIDUALS    = REPO_ROOT / "ontology" / "ontocal_individuals.ttl"
GEN_PYTHON     = REPO_ROOT / "dev_calliomapper" / "bin" / "gen-python"

# Local namespace — IRIs under this prefix are defined by us, not by OEO/BFO/IAO.
ONTOCAL_NS = "https://w3id.org/ontocal/"

# BFO properties are authoritative by definition but not re-enumerated inside oeo-full.yaml
# (OEO imports BFO axiomatically rather than listing every BFO property as a slot).
# Slot URIs under this prefix are exempt from the OEO IRI check.
BFO_PROPERTY_NS = "http://purl.obolibrary.org/obo/BFO_"

_ENV = {**os.environ, "PYTHONWARNINGS": "ignore"}

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def expand_curie(curie: str, prefixes: dict[str, str]) -> str | None:
    """
    Expand a 'prefix:local' CURIE using the given prefixes dict.
    Returns the full IRI, or None if the prefix is not in the dict.
    """
    if ":" not in curie:
        return None
    prefix, local = curie.split(":", 1)
    ns = prefixes.get(prefix)
    if ns is None:
        return None
    return ns + local


def collect_prefixes(raw: dict) -> dict[str, str]:
    """
    Return a flat {prefix: namespace_uri} dict from a LinkML YAML prefixes block.
    LinkML allows both the compact form  (prefix: uri)  and the verbose form
    (prefix: {prefix_prefix: ..., prefix_reference: uri}).
    """
    result: dict[str, str] = {}
    for key, val in raw.get("prefixes", {}).items():
        if isinstance(val, str):
            result[key] = val
        elif isinstance(val, dict):
            ref = val.get("prefix_reference")
            if ref:
                result[key] = ref
    return result


# ---------------------------------------------------------------------------
print(f"Validating {SCHEMA_PATH.relative_to(REPO_ROOT)}\n")

# 1. File exists
if not SCHEMA_PATH.exists():
    fail("ontocal_core.yaml not found")
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

# ---------------------------------------------------------------------------
# 5. Load oeo-full.yaml and build the set of all known external IRIs.
#    Every class_uri and slot_uri in oeo-full is an authoritative IRI we can
#    use to validate references from ontocal_core.yaml.
# ---------------------------------------------------------------------------
if not OEO_FULL_PATH.exists():
    fail(f"oeo-full.yaml not found at {OEO_FULL_PATH.relative_to(REPO_ROOT)} — skipping IRI checks")
    oeo_iris: set[str] = set()
else:
    with open(OEO_FULL_PATH) as f:
        oeo_raw: dict = yaml.safe_load(f)

    oeo_prefixes = collect_prefixes(oeo_raw)

    oeo_iris = set()
    for cls_def in oeo_raw.get("classes", {}).values():
        if isinstance(cls_def, dict) and "class_uri" in cls_def:
            iri = expand_curie(cls_def["class_uri"], oeo_prefixes)
            if iri:
                oeo_iris.add(iri)
    for slot_def in oeo_raw.get("slots", {}).values():
        if isinstance(slot_def, dict) and "slot_uri" in slot_def:
            iri = expand_curie(slot_def["slot_uri"], oeo_prefixes)
            if iri:
                oeo_iris.add(iri)

    ok(f"oeo-full.yaml loaded  ({len(oeo_iris)} known IRIs)")

# ---------------------------------------------------------------------------
# 5b. For every class / slot in ontocal that carries an external URI,
#     check the expanded IRI exists in oeo_iris.
# ---------------------------------------------------------------------------
ontocal_prefixes = collect_prefixes(raw)

def check_external_iri(entity_kind: str, entity_name: str, raw_uri: str) -> None:
    """Expand raw_uri and verify it is known to oeo-full (if it is external)."""
    if not raw_uri:
        return
    iri = expand_curie(raw_uri, ontocal_prefixes)
    if iri is None:
        fail(f"{entity_kind} '{entity_name}': cannot expand CURIE '{raw_uri}' — unknown prefix")
        return
    if iri.startswith(ONTOCAL_NS):
        return  # locally defined — nothing to verify against OEO
    if iri.startswith(BFO_PROPERTY_NS):
        return  # BFO properties are authoritative but not re-listed inside oeo-full.yaml
    if not oeo_iris:
        return  # oeo-full not loaded — already reported above
    if iri in oeo_iris:
        ok(f"{entity_kind} '{entity_name}': {raw_uri} → found in oeo-full")
    else:
        fail(
            f"{entity_kind} '{entity_name}': {raw_uri} expands to\n"
            f"      {iri}\n"
            f"      but this IRI does not exist in oeo-full.yaml"
        )

classes = raw.get("classes", {})
for cls_name, cls_def in sorted(classes.items()):
    if not isinstance(cls_def, dict):
        continue
    raw_uri = cls_def.get("class_uri", "")
    if raw_uri:
        check_external_iri("class", cls_name, raw_uri)

slots = raw.get("slots", {})
for slot_name, slot_def in sorted(slots.items()):
    if not isinstance(slot_def, dict):
        continue
    raw_uri = slot_def.get("slot_uri", "")
    if raw_uri:
        check_external_iri("slot", slot_name, raw_uri)

# ---------------------------------------------------------------------------
# 6. Calliope individual typed in ontocal_individuals.ttl
# ---------------------------------------------------------------------------
if not INDIVIDUALS.exists():
    fail("ontology/ontocal_individuals.ttl not found")
else:
    g = Graph()
    g.parse(INDIVIDUALS, format="turtle")
    calliope          = URIRef("https://w3id.org/ontocal/Calliope")
    modelling_software = URIRef("http://openenergy-platform.org/ontology/oeo/OEO_00000279")
    if (calliope, RDF.type, modelling_software) in g:
        ok("ontocal:Calliope typed as oeo:ModellingSoftware in ontocal_individuals.ttl")
    else:
        fail("ontocal:Calliope not typed as oeo:OEO_00000279 (ModellingSoftware) in ontocal_individuals.ttl")

# ---------------------------------------------------------------------------
# 7. gen-python round-trip
# ---------------------------------------------------------------------------
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
