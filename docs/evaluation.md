# Installation and saved-example evaluation

## Current review candidate: 0.1.0rc3

The source, documentation and executed notebooks are shared for review in the 16 November repository update. The results below describe the completed local evaluation on 13 November. Subsequent hosted checks are listed in [GitHub Actions](https://github.com/abart89/CallioMapPEr/actions/workflows/checks.yml); this repository update is not a PyPI or tagged GitHub release.

The 13 November candidate adopts the OEO-based OntoCal draft `https://w3id.org/ontocal/draft/2026-11-13-stage1`. Its bundled OEO 2.12.0 file is unchanged; PROV-O is not imported. The generated representation and annotation interface have changed, so this candidate received fresh checks rather than inheriting the results of rc2.

| Check | Result on 13 November 2026 |
|---|---|
| Source tests on Python 3.10.21 and 3.13.2 | All 147 passed on each version |
| Three public notebooks on Python 3.13.2 | All 20 code cells executed successfully |
| Clean wheel installation on Python 3.13.2 | All nine workflow groups passed; all eleven bundled-resource hashes matched |
| Clean source-distribution installation on Python 3.10.21 | All nine workflow groups passed; all eleven bundled-resource hashes matched |
| OWL checks on three generated graphs | All ten command stages passed; fourteen local class definitions remained usable, twelve selected logical expectations matched, and two deliberately contradictory cases were rejected |
| GitHub-hosted verification or publication as of 13 November | Not performed during the local evaluation |

The source tests include the stable national and urban saved examples and the preserved earlier outputs. They test explicit annotation roles: supplier-only information remains valid, contributor-only records are accepted, and a cited report can have an author different from the person creating the annotation. Process responsibility must be supplied explicitly; participation or supply of a description does not establish it. Schema 1 is rejected with migration guidance. Tests also verify that known software-version information remains visible and repeated citation paths do not duplicate an explanation answer.

The notebooks read the existing saved models, inspect generated graphs and execute the queries. The context notebook demonstrates a fictional source-report author, a contributor to an explanation and a supplier as three separately identified roles. The integration notebook also retrieves useful model, calculation, result, study and catalogue information using OEO, its foundations and Dublin Core alone. Its full competency-question answer can additionally use local supplier attribution. The notebook environment used nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.2.0 and pandas 3.0.1; these optional tools are separate from ordinary package requirements.

The clean installation checks installed the wheel and source distribution into separate environments. They confirmed the imported package location, verified the eleven copied ontology resources, and exercised translation, annotations, queries and invalid-data rejection. They did not obtain runtime code from an editable checkout. The final distributions exclude obsolete generated Python modules and the earlier PROV and modified-OEO dependency files. Calliope, xarray and LinkML were not installed in these runtime-check environments.

The formal check used three generated graphs: the national model with its preserved supplier-only tutorial annotations, the default urban model, and a national export with additional explicitly fictional report authorship, contribution and process-responsibility information. These three graphs are test exports, not three newly solved scenarios. The reasoner found no contradiction between their statements and the bundled definitions. A separate check found no local class whose definition made it impossible to have members. The deliberately wrong statements tested that an execution cannot also be a material object, and that a hypothetical asset description cannot also be material. These procedures detect specified formal mistakes; they do not establish the scientific truth of the supplied annotations.

The underlying Calliope sources and saved numerical outputs remain unchanged. The package reads existing CSV files and does not reconstruct a model or run a solver. Earlier preparation records below identify the Calliope and GLPK executions that produced those files.

### Repeating the current verification

With the development and notebook dependencies installed, run:

```sh
python -m pytest
python scripts/check_notebooks.py --output build/evaluation/2026-11-13-oeo/notebooks
python scripts/check_owl.py --out build/evaluation/2026-11-13-oeo/owl
```

The OWL command requires Java and ROBOT separately. The recorded run used ROBOT 1.9.7 and HermiT with the fixed local imports. The ordinary Python libraries were RDFLib 7.6.0, pySHACL 0.31.0 and PyYAML 6.0.3.

Build a wheel and source distribution, install each into a fresh environment, then run the installed-package check with that environment's Python:

```sh
/path/to/clean-environment/bin/python -I scripts/check_installation.py \
  --examples examples/calliope-0.7.0-glpk \
  --output /path/to/a/new/installation-check-directory
```

The local evaluation records are under `build/evaluation/2026-11-13-oeo/`: the notebook report, OWL report, test logs, and separate `wheel-install/` and `source-install/` reports. They record exact versions, commands and file hashes and are regenerated by the checks. These local results are distinct from subsequent GitHub-hosted checks. The historical results below retain their original versions and are not additional passes for rc3.

## Earlier release candidate: 0.1.0rc2

This candidate makes GLPK the solver used to prepare the primary examples and
updates the public notebooks to read those saved results. It also adds the README
workflow diagram. The package mapping rules, ontology axioms and SHACL constraints
remain unchanged. CallioMapper itself neither imports a solver nor runs Calliope.
The earlier candidate and its evidence remain available below.

| Local check | Result on 27 October 2026 |
|---|---|
| Source tests on Python 3.10.21 and 3.13.2 | All 129 passed on each version, including earlier HiGHS and dev7 regression examples |
| Three public notebooks on Python 3.13.2 | All 18 code cells executed successfully; saved outputs now describe the GLPK examples |
| Clean wheel installation | All nine workflow groups passed; all 29 bundled-resource hashes matched |
| Clean source-distribution installation | All nine workflow groups passed; all 29 bundled-resource hashes matched |
| OWL checks on the generated GLPK example graphs | All ten command stages passed with ROBOT 1.9.7 and HermiT |
| GitHub-hosted workflow | Configured; not yet run on GitHub |

The new [preparation record](../examples/calliope-0.7.0-glpk/README.md) identifies
Calliope 0.7.0, Pyomo 6.10.1 and GLPK 5.0. Both examples reported optimal
termination. All 15 model source files and 133 saved-export files have recorded
checksums. The original dev7 files and the earlier HiGHS source and results remain
unchanged.

The GLPK and HiGHS runs have identical source files, saved input arrays and saved
mathematical definitions, but some numerical answers differ. The preparation
record gives the objective values and selected result differences. These checks
verify that CallioMapper accurately represents the chosen saved results; they do
not establish solver equivalence or identify the numerical cause of the differences.

The new formal check combined 5,330 asserted triples from the annotated national
graph and the default urban graph. OWL 2 DL conformance and consistency passed;
all fourteen local classes remained satisfiable; twelve selected entailment and
non-entailment expectations matched; both deliberately contradictory additions
were inconsistent, as expected. This is a fresh check of the new generated graphs,
separate from the earlier HiGHS evidence.

To repeat the current checks, run the test suite and notebook runner described
below. For the installed-distribution check, select the GLPK directory:

```sh
/path/to/clean-environment/bin/python -I scripts/check_installation.py \
  --examples examples/calliope-0.7.0-glpk \
  --output /path/to/a/new/installation-check-directory
python scripts/check_owl.py
```

The OWL command requires Java and ROBOT. Its default is now the GLPK examples,
and its detailed evidence is written to `build/evaluation/stable-0.7.0-glpk/owl/`.
The rc2 tests, notebooks and installation evidence are retained separately under
`build/evaluation/0.1.0rc2/`. The recorded notebook versions are unchanged from rc1
except for CallioMapper itself. No GitHub push, hosted CI result or public release
is implied by these local checks.

## Earlier release candidate: 0.1.0rc1

The release candidate packages the existing saved-file workflow for research
trials and adds maintained public notebooks. It changes the package version and
distribution/documentation files; the mapping rules, ontology axioms and SHACL
constraints are unchanged from the stable-example implementation below.

| Local check | Result on 27 October 2026 |
|---|---|
| Source tests, Python 3.10.21 | All 121 passed |
| Source tests, Python 3.13.2 | All 121 passed |
| Three public notebooks, Python 3.13.2 | All 18 code cells executed successfully from fresh kernels; saved tables and assertions reflect the included stable examples |
| Clean wheel installation | All nine workflow groups passed; all 29 bundled-resource hashes and 55 runtime files matched |
| Clean source-distribution installation | All nine workflow groups passed; all 29 bundled-resource hashes and 55 runtime files matched |
| GitHub-hosted workflow | Configured for Python 3.10 and 3.13; not yet run on GitHub |

The notebook environment used JupyterLab 4.6.4, nbclient 0.11.0, nbformat 5.11.1,
ipykernel 7.4.0 and pandas 3.1.0. Those optional dependencies are separate from
the three libraries needed by ordinary translation. The notebooks read saved
examples, exercise the Python interface and inspect real query answers. Their
scientific context is explicitly synthetic where supplied; they do not run
Calliope or an optimiser.

Run `python scripts/check_notebooks.py` to execute all tutorials, or add `--write`
to refresh their public saved outputs. Local candidate evidence is retained under
`build/evaluation/0.1.0rc1/`. Notebook execution, declared assertions and package
checks do not establish scientific adequacy for an arbitrary modelling study.

The formal OWL evidence below comes from the preceding 0.1.0.dev1 evaluation.
It has not been relabelled as a new reasoner run for the release candidate.
No ontology or mapping change was made that would require repeating those checks.

## Stable-example implementation: 0.1.0.dev1

This report records checks of CallioMapper `0.1.0.dev1` performed on 27 October 2026. The package reads existing Calliope exports. None of these checks reconstructs a Calliope model or runs an optimiser.

## Clean installation

Both a wheel and a source distribution were built from a copy of the working source outside the development checkout. Each was installed in its own newly created Python environment, with the declared dependencies resolved. The checks used copied examples and an isolated Python interpreter. They confirmed that the imported package came from the new environment and that no editable installation or development-checkout import supplied missing files.

| Item | Observed version or result |
|---|---|
| Python | 3.13.2 |
| CallioMapper | 0.1.0.dev1 |
| RDFLib | 7.6.0 |
| pySHACL | 0.31.0 |
| PyYAML | 6.0.3 |
| Build tools | build 1.6.1; setuptools 84.2.1; wheel 0.48.0 |
| Wheel installation and workflow checks | Passed |
| Source-distribution installation and workflow checks | Passed |
| Bundled resource checksums | All 29 records matched the package snapshot |
| Installed runtime files | All 55 files matched the tested source copy |

The resolved environments also contained html5rdf 1.2.1, owlrl 7.6.2, packaging 26.3, prettytable 3.18.0, pyparsing 3.3.3 and wcwidth 0.9.4. Calliope, LinkML, LinkML Runtime, xarray and netCDF4 were absent. The distributions did not contain the prototype's generated Python model classes.

The resource checks cover the authoritative OntoCal snapshot, the four SHACL profiles, dependency files, identifiers and accompanying change records. The ontology version is `https://w3id.org/ontocal/draft/2026-10-22-stage1`. The OEO and PROV-O files include the project's documented local derivatives; these are not official upstream releases. See [the dependency explanation](dependencies.md).

## Workflows checked in each installation

The same nine groups of checks ran against each installed distribution, using genuine stable 0.7.0 saved examples.

| Check | Observed result |
|---|---|
| Stable example integrity | All 133 saved-export file hashes matched the independent preparation manifest. The graph report retained the distinction between the recognised format and an omitted runtime software version. |
| National example, ordinary default export | Five nodes and fifteen node-specific technology components; thirteen external output series and thirteen supported energy summaries. No individual timestep records or invented concrete units. SHACL passed. |
| Urban example, ordinary default export | Four nodes and twenty-six node-specific technology components; twenty-one external output series. Its custom mathematical configuration is outside the automatic summary rule, so summaries were omitted with an explicit reason. SHACL passed. |
| Structure-only selection | No numerical records. Reusing the identity manifest retained the default export's configuration and execution identifiers. |
| Explicit time-point selection | Exactly the requested input and output points were represented, without unrequested summaries. |
| National example with supplied annotations | The prepared example added attributed assumptions, reasons and evidenced unit interpretations. Invented demonstration context remained labelled. |
| Annotation-template command | Created the installed template and refused to overwrite an existing file. |
| Installed-capacity query | Returned fifteen national-example records. An unknown query name produced an error rather than a successful empty result. |
| Invalid graph | Removing the execution's configuration relationship caused the installed SHACL validation to fail, as required. |

Stable **Calliope 0.7.0** is now the primary tested target. Both supplied examples were actually built and solved with that release and HiGHS 1.15.1 in a separate preparation environment. Both terminated optimally. Their complete source and saved-output snapshots, hashes and environment record are under [examples/calliope-0.7.0](../examples/calliope-0.7.0/README.md). These two preparation runs are separate from ordinary translation and evaluation, which only read saved files.

The stable native CSV export omits `runtime.calliope_version_initialised` by default. A requested configuration version does not establish the producing executable version. Reports therefore distinguish the selected format, the configured target and the recorded runtime version, leaving the last unknown when absent. The preparation manifest independently records the actual software used for these particular examples.

Andrea’s original **0.7.0.dev7** snapshots remain unchanged: all 139 recorded file hashes still match. They remain covered by regression tests. The [comparison report](calliope-version-comparison.md) explains the source syntax and mathematics changes, unchanged numerical source data, small differences in saved effective arrays and selected result differences. This evidence does not establish compatibility with other Calliope versions, arbitrary custom arrays or mathematical extensions.

## Repeating the installation checks

Use [the installation instructions](usage.md) to create an environment containing the wheel or source distribution, then run the checked-in script with that environment's Python:

```sh
/path/to/clean-environment/bin/python -I scripts/check_installation.py \
  --examples examples/calliope-0.7.0 \
  --output /path/to/a/new/installation-check-directory
```

The script changes into the output directory before checking the installed package. It writes `installation-report.json`, the exact command results in `commands.json`, generated graphs and their reports, and query answers. Use a fresh output directory because the checks deliberately verify that the annotation-template command refuses overwriting. The machine-readable report includes all installed package versions and checksums of the runtime files. Run it separately for the wheel and source-distribution environments.

These are installation and workflow checks, not a claim that every scientifically meaningful assertion has been verified. SHACL checks whether required information and relationships are present. It does not replace OWL reasoning, source-value checks or review of scientific interpretations. The ordinary translation report explicitly states that it has not run OWL reasoning. The checks below provide separate evidence.

## Source tests and competency questions

The complete Python test suite passed **121 tests**. It covers source reading, entity identities, numerical interpretation, annotations, query answers, validation, resource integrity and command-line behaviour. The query tests exercise all eight competency questions, including missing context and cases where a comparison must be refused. Stable-specific checks cover the real activation and carrier arrays, retained inactive components, the changed flow mathematics, omitted software defaults, numerical expectations read independently from the saved CSV files, and refusal to interpret a dev7 file layout as stable merely because its version label changes. The tests do not promise complete coverage of every Calliope feature or every possible annotation.

Run the source tests in a development environment containing the package and its test dependencies:

```sh
python -m pytest tests/ -q
```

The [worked comparison and integration example](questions.md#worked-comparison-and-integration-example) also passed all eight of its own checks. Those eight checks are conditions within that demonstration; they are distinct from the eight competency questions. The demonstration used the stable national example and produced one comparison row with zero input and output differences and thirty-eight integration rows retaining two separately assigned export-run identifiers. Both exports describe the same saved execution, with invented tutorial scenario descriptions. The zero differences verify graph handling; they do not constitute a real two-scenario experiment.

The example additionally verifies that source-only graphs do not acquire invented assumption answers, that independently assigned component identities remain distinct, and that comparisons are refused when units are missing, units differ or time horizons differ. Run it with:

```sh
python examples/annotations/compare_exports.py build/independent-exports
```

## Separate OWL checks on generated graphs

The developer's formal check combined the generated annotated national graph and default urban graph with the bundled ontology and exact local dependencies. It passed all ten command stages using ROBOT 1.9.7 and its HermiT reasoner. The combined graph contained 5,330 asserted triples before imports were added.

- The combined ontology and generated assertions passed the OWL 2 DL structural check and were logically consistent.
- All fourteen local OntoCal classes were satisfiable: each could have an instance without contradiction.
- Twelve selected classification or non-classification expectations matched the reasoner's answers. These cover executions, configurations, model components, scenarios, studies and computed summaries.
- Two deliberately invalid additions were inconsistent, as expected: treating an execution as a material entity, and treating an explicitly hypothetical information description as a material entity.

An inference that does not follow is not automatically a proof of its negation. The non-entailment checks and deliberately contradictory examples therefore answer different questions. The run did not attempt to materialise every inferred class or individual type in the imported ontologies, or repeat the ontology project's exhaustive imported-class evaluation. Ordinary graph generation does not require Java or ROBOT.

With the developer prerequisites available, repeat the earlier HiGHS formal checks using:

```sh
python scripts/check_owl.py --examples examples/calliope-0.7.0 \
  --out build/evaluation/stable-0.7.0/owl
```

The report records source checksums, exact invocations, exit codes, selected inference results and any unfinished checks. Local machine-readable evidence is written to `build/evaluation/stable-0.7.0/owl/report.json`. Installation reports are retained at `build/evaluation/stable-0.7.0/installations/wheel/installation-report.json` and `build/evaluation/stable-0.7.0/installations/sdist/installation-report.json`; the command logs and artifact hashes are kept beside them. These generated files are untracked. The maintained report records the observed outcome, while the scripts regenerate the detailed evidence.

Earlier dev7 evaluation logs remain under the original `build/evaluation/` paths. They were not overwritten or relabelled as stable evidence. The authoritative OntoCal ontology and dependency files did not change for this alignment; the stable generated graphs were checked against the same reviewed snapshot.
