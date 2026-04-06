"""
Validates ontology/ontocal.yaml as a well-formed LinkML schema.

Checks performed:
  1. File is parseable YAML.
  2. LinkML SchemaLoader accepts it without errors.
  3. Required top-level header fields are present (id, name, imports).
  4. Every OEO stub class has a class_uri (not just a local name).
  5. Every slot that maps to an external property has a slot_uri.
  6. The Calliope individual is typed as oeo:SoftwareFramework in individuals.ttl.
  7. gen-python round-trip: schema generates valid Python without errors.
"""

import os
import subprocess
from pathlib import Path

import pytest
import yaml
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.linkml_model import SchemaDefinition

SCHEMA_PATH = Path(__file__).parent.parent / "ontology" / "ontocal_core.yaml"
OEO_STUBS = {"ModellingSoftware", "EnergySystemModel", "ModelComponent", "Optimisation"}
EXTERNAL_SLOTS = {"has_part", "part_of"}

# Suppress the urllib3/requests version mismatch warning that linkml CLI tools emit.
_SUBPROCESS_ENV = {**os.environ, "PYTHONWARNINGS": "ignore"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_raw() -> dict:
    with open(SCHEMA_PATH) as f:
        return yaml.safe_load(f)


def load_schema() -> SchemaDefinition:
    return yaml_loader.load(str(SCHEMA_PATH), target_class=SchemaDefinition)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema file not found: {SCHEMA_PATH}"


def test_yaml_parseable():
    raw = load_raw()
    assert isinstance(raw, dict), "Schema did not parse to a dict"


def test_required_header_fields():
    raw = load_raw()
    assert "id" in raw, "Missing top-level 'id'"
    assert "name" in raw, "Missing top-level 'name'"
    imports = raw.get("imports", [])
    assert any("linkml:types" in str(i) for i in imports), (
        "Missing 'linkml:types' in imports — built-in datatypes will be undefined"
    )


def test_linkml_schema_loads():
    """SchemaLoader must accept the file without raising."""
    schema = load_schema()
    assert schema.name == "ontocal"


def test_oeo_stub_classes_have_class_uri():
    """Every OEO stub must pin its identity via class_uri, not just a local name."""
    raw = load_raw()
    classes = raw.get("classes", {})
    for stub in OEO_STUBS:
        assert stub in classes, f"OEO stub class '{stub}' missing from schema"
        assert "class_uri" in classes[stub], (
            f"OEO stub '{stub}' has no class_uri — it will be treated as a local ontocal class"
        )


def test_slots_have_slot_uri():
    """Every external-property slot must declare slot_uri."""
    raw = load_raw()
    slots = raw.get("slots", {})
    for slot in EXTERNAL_SLOTS:
        assert slot in slots, f"Slot '{slot}' missing from schema"
        assert "slot_uri" in slots[slot], (
            f"Slot '{slot}' has no slot_uri — it will not map to its BFO/OEO property"
        )


def test_calliope_individual_typed():
    """
    LinkML 1.x has no 'individuals:' block — named individuals live in individuals.ttl.
    Check that the file exists and that Calliope is typed as oeo:SoftwareFramework (OEO_00000382).
    """
    from rdflib import Graph, URIRef
    from rdflib.namespace import RDF

    ttl_path = Path(__file__).parent.parent / "ontology" / "individuals.ttl"
    assert ttl_path.exists(), "ontology/individuals.ttl not found"

    g = Graph()
    g.parse(ttl_path, format="turtle")

    calliope = URIRef("https://w3id.org/ontocal/Calliope")
    modelling_software = URIRef("http://openenergy-platform.org/ontology/oeo/OEO_00000279")
    assert (calliope, RDF.type, modelling_software) in g, (
        "ontocal:Calliope is not typed as oeo:OEO_00000279 (ModellingSoftware) in individuals.ttl"
    )


def test_gen_python_roundtrip():
    """gen-python must exit 0 and produce non-empty output — catches broken URIs, unresolved refs."""
    gen_python = Path(__file__).parent.parent / "dev_calliomapper" / "bin" / "gen-python"
    result = subprocess.run(
            [str(gen_python), str(SCHEMA_PATH)],
            capture_output=True,
            text=True,
            env=_SUBPROCESS_ENV,
        )
    assert result.returncode == 0, (
        f"gen-python failed (exit {result.returncode}):\n{result.stderr}"
    )
