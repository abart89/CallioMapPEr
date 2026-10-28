# Changes

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
