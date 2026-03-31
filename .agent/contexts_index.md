# .agent/ Contexts Index

Quick reference for agent and developer orientation. Files are listed in recommended reading order for a new context.

---

## Active / Authoritative

| File | Purpose | Status |
| :--- | :--- | :--- |
| [manifesto.md](manifesto.md) | Project mission, value propositions, target audience, design principles, impact goal. The "why" of the project. | Stable — unlikely to change |
| [ontology_rationale.md](ontology_rationale.md) | Scope reckoning (Path A vs B decision), OEO fitness assessment, `ontocal:` class hierarchy, predicate table, provenance module spec, SOSA/M3 design, extensions architecture, namespace policy, SPARQL examples. The definitive ontology reference. | Current and authoritative |
| [ontologynotes.md](ontologynotes.md) | Compact structured taxonomy reference: class hierarchy (bfo/iao/oeo/ontocal), object attributes table, data attributes table. Refined companion to `ontology_rationale.md` — useful for quickly looking up class/predicate assignments. | Current — reflects decisions from dev diary through 2026-03-25 |
| [ontology_dev_diary.md](ontology_dev_diary.md) | Chronological decision log for ontology development: scope, BFO alignment, process/data separation, parameter handling, scenario/override labelling. **Primary record of why decisions were made.** | Active — add new entries at top (newest first) |
| [workflow.md](workflow.md) | Logical pipeline description: what CallioMapper does and why, inputs, three processing stages (M1/M2/M3), validation gate, output format. No implementation details. | Current and authoritative |
| [workflow_implementation.md](workflow_implementation.md) | Technical counterpart to workflow.md: Python API, CLI, input parsing decisions (CSV-first rationale), internal pipeline component names, key design decisions, schema/namespace resolution, known issues. **Primary reference for any implementation work.** | Current for design decisions; implementation state section updated 2026-03-27 |
| [project_structure.md](project_structure.md) | Repository layout reference: directory tree, file naming conventions, ontology module/profile structure, test fixtures, named graph conventions, namespace prefixes. | Mostly current; ontology/ section describes the *planned* module layout — actual current files are just `ontocal.yaml` + `individuals.ttl` |
| [attrs_structure.yaml](attrs_structure.yaml) | Skeleton of the Calliope v0.7 `attrs.yaml` structure: top-level keys (`definition`, `config`, `math`), node/tech names, config blocks. Reference for understanding what the input parser reads. | Stable reference |
| [implementation_notes.md](implementation_notes.md) | Ideas and decisions captured during ontology work for use in the Python implementation phase. Organized by component (StructuralMapper, EpistemicEngine, etc.). **Read this before implementing any mapper.** | Active scratchpad — add entries as ideas arise |

---

## Partially Superseded

| File | Original Purpose | What's Still Useful | What's Outdated |
| :--- | :--- | :--- | :--- |
| [development_plan.md](development_plan.md) | Technical stack, feature priority table, MVT milestones, developer guidelines | Tech stack table (Section 1), profile system overview, feature priority tiers (MVT vs OPTIONAL), M1–M4 milestone deliverables as a checklist | Section 2 (TTL as source of truth — superseded: YAML-first is the decision); Section 5 developer guidelines (same TTL-authority conflict); M3 deliverables say `results.nc` via Xarray — superseded by CSV-first decision |
| [skills.md](skills.md) | Planned Claude slash commands (`/validate-model`, `/generate-ontology-artifacts`) | Describes intent and what the skills should do | Both skills are still unimplemented; `/generate-ontology-artifacts` trigger description references old file name |