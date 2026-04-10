#!/usr/bin/env python3
"""
Semantic validator for ontocal/ontocal_core.yaml using owlready2.

This script tests true semantic/logical compliance. It verifies that Calliope's schema definitions correctly align with OEO abstract categories without triggering contradictions or violating disjointness axioms.

Usage:
    python scripts/test_oeo_compliance.py
"""
import os
import sys
import subprocess
from pathlib import Path
from owlready2 import get_ontology, sync_reasoner, default_world
import logging

# owlready2 is noisy, suppress unless critical
logging.getLogger("owlready2").setLevel(logging.CRITICAL)

REPO_ROOT     = Path(__file__).parent.parent
SCHEMA_PATH   = REPO_ROOT / "ontocal" / "ontocal_core.yaml"
OEO_PATH      = REPO_ROOT / "oeo-2" / "oeo.owl"
GEN_OWL       = REPO_ROOT / "dev_calliomapper" / "bin" / "gen-owl"
TEMP_OWL      = REPO_ROOT / "_temp_schema.owl"

def main():
    if not OEO_PATH.exists():
        print(f"  FAIL  OEO ontology not found at {OEO_PATH}")
        sys.exit(1)
        
    print(f"Validating {SCHEMA_PATH.relative_to(REPO_ROOT)} semantics against OEO...")
    
    print("  ... generating OWL structure from LinkML schema")
    res = subprocess.run([str(GEN_OWL), str(SCHEMA_PATH)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  FAIL  gen-owl failed:\n    {res.stderr.strip()}")
        sys.exit(1)
        
    print("  ... converting LinkML Turtle output to RDF/XML for reasoner")
    from rdflib import Graph
    g = Graph()
    g.parse(data=res.stdout, format="turtle")
    g.serialize(destination=str(TEMP_OWL), format="xml")
        
    print("  ... loading knowledge base (this may take a moment due to OEO scale)")
    try:
        onto_oeo = get_ontology(f"file://{OEO_PATH}").load()
        onto_schema = get_ontology(f"file://{TEMP_OWL}").load()
    except Exception as e:
        print(f"  FAIL  Error loading ontology files:\n{e}")
        sys.exit(1)
        
    print("  ... running HermiT DL reasoner")
    try:
        with onto_schema:
            sync_reasoner()
    except Exception as e:
        print(f"  FAIL  Reasoner encountered mathematical contradiction or error:\n    {e}")
        TEMP_OWL.unlink(missing_ok=True)
        sys.exit(1)
        
    # Check for unsatisfiable classes (asserted to owl:Nothing)
    inconsistent = list(default_world.inconsistent_classes())
    
    # Cleanup temp OWL file
    TEMP_OWL.unlink(missing_ok=True)
    
    if inconsistent:
        print(f"  FAIL  Schema is Logically Inconsistent. Derived {len(inconsistent)} unsatisfiable class(es):")
        for cls in inconsistent:
            print(f"    - {cls}")
        sys.exit(1)
        
    print("  ok    Schema is fully compliant and logically consistent with OEO.")
    sys.exit(0)

if __name__ == "__main__":
    main()
