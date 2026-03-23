# .agent/ Contexts Index

Quick reference for agent and developer orientation. Files are listed in recommended reading order for a new context.

---

## Active / Authoritative

| File | Purpose | Status |
| :--- | :--- | :--- |
| [manifesto.md](manifesto.md) | Project mission, value propositions, target audience, design principles, impact goal. The "why" of the project. | Stable — unlikely to change |
| [ontology_rationale.md](ontology_rationale.md) | Scope reckoning (Path A vs B decision), OEO fitness assessment, `ontocal:` class hierarchy, predicate table, provenance module spec, SOSA/M3 design, extensions architecture, namespace policy, SPARQL examples. The definitive ontology reference. | Current and authoritative |
| [workflow.md](workflow.md) | Logical pipeline description: what CallioMapper does and why, inputs, three processing stages (M1/M2/M3), validation gate, output format. No implementation details. | Current and authoritative |
| [workflow_implementation.md](workflow_implementation.md) | Technical counterpart to workflow.md: current implementation state, class/file inventory, Python API, CLI, input parsing decisions (CSV-first rationale), internal pipeline component names, key design decisions, schema/namespace resolution, next planned work (real ontology → M2 → M3 → M4), known issues. **Primary reference for any implementation work.** | Current and authoritative — updated 2026-03-20 |
| [project_structure.md](project_structure.md) | Repository layout reference: directory tree, file naming conventions, ontology module/profile structure, test fixtures, named graph conventions, namespace prefixes. | Mostly current; two known stale items: (1) references deleted `handoff.md`; (2) data flow diagram says `ConjunctiveGraph` — should be `Dataset` |

---

## Partially Superseded

| File | Original Purpose | What's Still Useful | What's Outdated |
| :--- | :--- | :--- | :--- |
| [development_plan.md](development_plan.md) | Technical stack, feature priority table, MVT milestones, developer guidelines | Tech stack table (Section 1), profile system overview, feature priority tiers (MVT vs OPTIONAL), M1–M4 milestone deliverables as a checklist | Section 2 (TTL as source of truth — superseded: YAML-first is the decision); Section 5 developer guidelines (same TTL-authority conflict); M3 says `results.nc` via Xarray — superseded by CSV-first decision |
| [skills.md](skills.md) | Planned Claude slash commands (`/validate-model`, `/generate-ontology-artifacts`) | Describes intent and what the skills should do | References old file name `calliope_oeo.linkml.yaml`; both skills are still unimplemented (waiting on M1 real schema) |
| [ontologynotes.md](ontologynotes.md) | Active working notes for ontology drafting (class definitions, taxonomy sketches, informal decisions). Not authoritative — `ontology_rationale.md` is the clean version. | In-progress / informal |