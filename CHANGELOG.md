# Changes

## 0.1.0rc3 — local candidate, 13 November 2026

This is an internal evaluation candidate and has not been published as a new release.

- Adopt OntoCal `2026-11-13-stage1` with unchanged OEO 2.12.0, replacing the active OEO/PROV derivative combination.
- Generate OEO information-input/output relationships and describe software as IAO software participating in processes. Preserve source revisions and actual process timestamps through the documented metadata and OntoCal properties.
- Introduce annotation schema 2. Contributors, suppliers, source authors, process participants and responsible people/organisations have separate fields and meanings. Schema 1 is rejected with explicit migration guidance.
- Preserve existing supplier-only tutorial facts and add checks for contributor-only records, known source authors and responsibility that is supplied explicitly.
- Update bundled queries, validation requirements, documentation and notebooks for the new representation. Source Calliope examples and saved numerical outputs remain unchanged.

The [evaluation report](docs/evaluation.md) records the current checks and distinguishes them from the earlier candidate results below. A general PROV export remains future work.

## 0.1.0rc2 — 27 October 2026

- Use GLPK 5.0 through Pyomo to prepare the primary saved Calliope 0.7.0
  examples. Preserve earlier HiGHS and development-preview snapshots.
  Ordinary package use remains independent of a solver.
- Update the public tutorials to use those GLPK outputs and retain checks
  against the earlier examples.
- Add a README diagram distinguishing saved files, supplied context and OntoCal.

The mapping rules, ontology axioms and validation constraints are unchanged.
This remains a release candidate for research trials.

## 0.1.0rc1 — 27 October 2026

This is the first packaged release candidate for research trials. It provides a
fixed version for testing the documented workflow on other modelling studies.
Feedback may still change the interface and representation before a final 0.1.0
release. No PyPI publication or DOI is claimed.

- Read successful saved CSV exports from stable Calliope 0.7.0 and the preserved
  0.7.0.dev7 examples, without importing Calliope or running an optimiser.
- Represent model structure, selected capacities and costs, external output
  series and supported energy summaries using the reviewed OntoCal snapshot.
- Add explicitly attributed study, scenario, assumption, dataset and physical
  correspondence information through optional annotations.
- Provide the eight bounded competency-question queries and explicit omission
  and validation reports.
- Include three executed Jupyter tutorials, a Python quickstart, source examples
  and reproducible verification commands.
- Include package and notebook checks for future GitHub runs, contribution
  guidance, the software license and third-party attribution.

The stable-example reader and numerical interpretation retain the behaviour
verified in 0.1.0.dev1. The ontology and bundled dependency axioms are unchanged.
The [evaluation report](docs/evaluation.md) separates executed local checks from
checks configured for GitHub that have not yet run there.

## Earlier local development

`0.1.0.dev0` established the saved-export workflow using the historical dev7
examples. `0.1.0.dev1` added genuine stable 0.7.0 examples and the corresponding
reader and mathematical interpretation. The [version comparison](docs/calliope-version-comparison.md)
records changes in the Calliope sources, saved formats and numerical results.
