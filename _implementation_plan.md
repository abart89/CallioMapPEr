# CallioMapper Showcase — Implementation Plan

## Context
The goal is to build dissemination materials (notebooks, polished README) proving that CallioMapper
produces useful, queryable Knowledge Graphs from Calliope energy models. The primary audiences are
academic supervisors and potential open-source contributors.

**Rule**: no showcase material is built on top of an unverified pipeline. Each phase gates the next.

---

## Phase 0 — Verify the end-to-end pipeline (CURRENT)
Run the actual `translate` command on `examples/national_scale/` and confirm:
1. `Translator` runs without error on real Calliope output files
2. An `.nq` file is produced and parses as valid RDF
3. SHACL validation passes against `ontocal_core_shapes.ttl`
4. Identify which CLI commands/code paths are stubs vs. working

**Success criterion**: `calliomapper translate examples/national_scale/ --out /tmp/test.nq` exits 0
and `/tmp/test.nq` contains valid N-Quads.

---

## Phase 1 — Fix the README
- Restore the architecture section and named-graph table (technical credibility)
- Keep the elevator-pitch language but only show CLI examples that actually work
- Remove `--type total_system_emissions` (flag does not exist yet)

---

## Phase 2 — Notebook A: 10-Minute Semantic Model
Only started once Phase 0 passes cleanly.
- Use `Translator` in Python (not CLI) on `examples/national_scale/`
- Render the topology as a static `networkx` graph
- No `pyvis`, no GIFs until this simpler version is validated

---

## Phase 3 — Notebook B: SPARQL to Pandas
Only started once Phase 2 produces a real, content-rich `.nq`.
- Canned SPARQL queries that return data from the national_scale graph
- Convert results to Pandas DataFrames and plot with matplotlib/seaborn

---

## Out of scope (for now)
- GraphDB / Metaphactory guide
- Animated GIFs
- mkdocs / GitHub Pages

---

## What the previous agent implemented (status at plan creation: 2026-04-07)
| File | Change | Status |
|---|---|---|
| README.md | Replaced with marketing version | Partial — lost architecture docs |
| calliomapper/mapper/core.py | Migrated dummy_schema → ontocal_core, typed tech dispatch | Good |
| calliomapper/translator.py | Switched default shapes to ontocal_core_shapes.ttl | Good |
| tests/test_core.py | Updated assertions for new typed classes | Good |

All 22 tests pass as of 2026-04-07.
