# .agent/ Index

Quick reference for agent and developer orientation.

```
.agent/
├── contexts/     # decisions, rationale, diary — what we know and decided
└── operational/  # workflow, structure, skills — how to work
```

---

## contexts/ — What We Know and Decided

Files are listed in recommended reading order for a new context.

| File                                                            | Purpose                                                                                                                                                                                                                                             | Status                                         |
| :-------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------- |
| [manifesto.md](contexts/manifesto.md)                           | Project mission, value propositions, target audience, design principles, impact goal. The "why" of the project.                                                                                                                                     | Stable                                         |
| [scientific_positioning.md](contexts/scientific_positioning.md) | Scientific and academic positioning: related work, differentiation, publication target, research contributions.                                                                                                                                     | Current                                        |
| [ontocal_rationale.md](contexts/ontocal_rationale.md)           | Scope reckoning (Path A vs B decision), OEO fitness assessment, `ontocal:` class hierarchy, predicate table, provenance module spec, SOSA/M3 design, extensions architecture, namespace policy, SPARQL examples. The definitive ontology reference. | Current and authoritative                      |
| [ontocal_dev_diary.md](contexts/ontocal_dev_diary.md)           | Chronological decision log for ontocal core development: scope, BFO alignment, process/data separation, parameter handling, scenario/override labelling. **Primary record of why decisions were made about the core.**                              | Active — add new entries at top (newest first) |
| [extensions_dev_diary.md](contexts/extensions_dev_diary.md)     | Chronological decision log for extension modules (epistemic/provenance, results, future extensions). Separate from the core diary because extensions capture knowledge outside Calliope's own files.                                                | Active — add new entries at top (newest first) |
| [implementation_notes.md](contexts/implementation_notes.md)     | Ideas and decisions captured during ontology work for use in the Python implementation phase. Organized by component (StructuralMapper, EpistemicEngine, etc.). **Read this before implementing any mapper.**                                       | Active scratchpad — add entries as ideas arise |
| [attrs_structure.yaml](contexts/attrs_structure.yaml)           | Skeleton of the Calliope v0.7 `attrs.yaml` structure: top-level keys, node/tech names, config blocks. Reference for understanding what the input parser reads.                                                                                      | Stable reference                               |

### Partially Superseded

| File                                                | What's Still Useful                                                                                                                          | What's Outdated                                                                                                                                                   |
| :-------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [development_plan.md](contexts/development_plan.md) | Tech stack table (Section 1), profile system overview, feature priority tiers (MVT vs OPTIONAL), M1–M4 milestone deliverables as a checklist | Section 2 (TTL as source of truth — superseded: YAML-first is the decision); M3 deliverables reference `results.nc` via Xarray — superseded by CSV-first decision |

---

## operational/ — How to Work

| File                                                                 | Purpose                                                                                                                                                                                                                                | Status                                                                        |
| :------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| [workflow.md](operational/workflow.md)                               | Logical pipeline description: what CallioMapper does and why, inputs, three processing stages (M1/M2/M3), validation gate, output format. No implementation details.                                                                   | Current and authoritative                                                     |
| [workflow_implementation.md](operational/workflow_implementation.md) | Technical counterpart to workflow.md: Python API, CLI, input parsing decisions, internal pipeline component names, key design decisions, schema/namespace resolution, known issues. **Primary reference for any implementation work.** | Current for design decisions; implementation state section updated 2026-04-07 |
| [project_structure.md](operational/project_structure.md)             | Repository layout reference: directory tree, file naming conventions, ontology module/profile structure, test fixtures, named graph conventions, namespace prefixes.                                                                   | Mostly current; ontology/ section describes the *planned* module layout       |
| [skills.md](operational/skills.md)                                   | Planned Claude slash commands (`/validate-model`, `/generate-ontology-artifacts`): what they do and implementation notes.                                                                                                              | Planned — not yet implemented                                                 |
