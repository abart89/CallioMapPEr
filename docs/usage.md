# Using CallioMapper

CallioMapper `0.1.0rc3` is a local candidate for internal research trials. It uses the OEO-based OntoCal draft and annotation schema 2; this local update is not a public release. It reads a saved, successful Calliope CSV export and represents selected information using OntoCal. The primary target is stable Calliope 0.7.0; the included 0.7.0.dev7 exports provide historical regression cases. The supported variables and tests are bounded. This release does not claim to translate every Calliope model or mathematical extension.

## Install and open the examples

Use Python 3.10 or later. The [evaluation record](evaluation.md) identifies the versions used for the current and earlier checks. From the repository directory, create and activate an environment, then install the package:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
```

The activation command above is for a Unix-like shell; Windows environments use the `Scripts` directory. If you have been given a built wheel, you can install that instead:

```sh
python -m pip install /path/to/calliomapper-0.1.0rc3-py3-none-any.whl
```

Keep a copy of the repository or accompanying source archive for the saved examples and notebooks. They are not installed into the current directory by the wheel. No PyPI publication is assumed by these instructions.

For the interactive examples, install the optional notebook dependencies from the repository and open JupyterLab:

```sh
python -m pip install '.[notebooks]'
jupyter lab notebooks
```

Start with [saved results](../notebooks/01_saved_results.ipynb), then [supplied context](../notebooks/02_supplied_context.ipynb), then [comparison and integration](../notebooks/03_comparison_and_integration.ipynb). The notebook dependencies include pandas for displaying tables. The package's Python API itself does not require pandas.

## Required saved files

The input directory must contain `attrs.yaml` and Calliope's saved `inputs_*.csv` and `results_*.csv` files. It can have any directory name. These files are produced by Calliope's explicit CSV export operation after a successful solve; solving alone does not create them automatically.

The reader requires saved definition, configuration, mathematics and execution metadata. The termination condition must be `optimal`, and the saved execution must include timestamps that distinguish that run. A directory missing those records is rejected. NetCDF, unsolved models and failed-run exports are not implemented in this reader.

The input files remain unchanged. Every recognised input/result CSV participates in the appropriate configuration or execution fingerprint, including arrays not selected for representation. Other files are not read as model facts. Unsupported dimensions in a selected array are an error. An absent supported variable or a non-finite numerical value produces an omission entry in the report.

Neither Calliope nor a solver is imported during translation. The included stable examples were prepared separately using Calliope 0.7.0 and GLPK 5.0; ordinary use and tests read their saved outputs. Optional regeneration is described in [the example documentation](../examples/calliope-0.7.0-glpk/README.md).

## Translate and query in Python

From the repository directory:

```python
from calliomapper import Translator
from calliomapper.queries import run_query

translator = Translator(
    "examples/calliope-0.7.0-glpk/national_scale/results_directory",
    groups={"structure", "capacities"},
)
translator.save("build/capacities.nq")
dataset = translator.translate()

answers = run_query(dataset, "installed_capacity")
for answer in answers:
    print(answer.node, answer.technology, answer.carrier,
          answer["value"], answer.unit)

print(translator.report["omissions"])
```

`save()` creates the graph, validates it and writes it with two companion JSON files. Calling `translate()` afterward returns the same RDFLib `Dataset`; it does not repeat the conversion. If you only need an in-memory graph, call `translate()` without `save()`. When replacing an existing saved graph, call `save()` first so it can read the existing identity manifest before generating identifiers.

`run_query()` returns an RDFLib SELECT result. Each row exposes named columns; use `answer["value"]` to access a column explicitly. RDF terms can be converted to Python strings or ordinary Python values when needed. An unbound column is `None`. For example, a missing unit means no concrete unit has been asserted, rather than a claim that the quantity is dimensionless.

A query can restrict named variables without building SPARQL text:

```python
answers = run_query(
    dataset, "installed_capacity", bindings={"technology": "ccgt"}
)
columns = ("node", "technology", "carrier", "value", "unit")
rows = [
    {column: str(answer[column]) if answer[column] is not None else None
     for column in columns}
    for answer in answers
]
```

For the supplied national export, this produces one row with node `region1`, technology `ccgt`, carrier `power`, value `30000.0` and unit `None`. Removing the filter returns fifteen capacity records. The resulting `rows` is a list of dictionaries and can be passed to another application without pandas.

The installed presets are `cq01` to `cq08`, `installed_capacity` and `system_costs`. Their prerequisites are described in [the question guide](questions.md). `system_costs` returns saved component costs; it does not invent a currency or calculate a system-wide sum. For entity-identifier bindings, use RDFLib `URIRef` values. Python strings are interpreted as literal values.

## Choose the information to include

All four groups are selected by default. Structure is always included. These are export options, not separate ontology modules.

| Group | Saved input variables | Saved result variables |
|---|---|---|
| `structure` | Active node–technology combinations, base technologies, carrier membership and transmission endpoints, with relevant metadata | Execution metadata |
| `capacities` | `flow_cap_max`, `storage_cap_max`, `flow_in_eff`, `flow_out_eff` | `flow_cap`, `storage_cap` |
| `costs` | `cost_flow_cap`, `cost_storage_cap` | `cost` |
| `energy` | Weight and duration metadata used to interpret the output | `flow_out` series references and supported weighted totals |

Use `groups={"structure"}` for a graph without numerical records, or select any combination of the other groups. The names are checked, so an unknown group is an error.

Inputs represent effective values in the saved arrays. For example, the national `region1/ccgt` capacity bound is 30000. The general technology definition has a separate information identity and a locator in `attrs.yaml`, but this release does not separately expand its original 40000 bound or reconstruct the sequence of overrides. The effective assignment therefore does not describe the complete history of that choice.

Each scalar record retains its node, technology, available carrier/cost coordinates, source revision and source selector. Input records belong to the configuration; result records belong to the recorded execution. A reported number can be retained without unit evidence. The reader then does not claim a fully interpreted physical quantity or silently compare it with an incompatible quantity.

Energy totals use `sum(flow_out[i] * timestep_weights[i])` only when the saved mathematics agrees with the evaluated energy-per-timestep interpretation and the complete time indices, weights and durations match. The interpretation has been checked separately for 0.7.0 and 0.7.0.dev7. Duration is not multiplied again, and no automatic annualisation is performed. The aggregation is recorded as an activity separate from the original optimisation.

Custom mathematics or incomplete metadata cause the total to be omitted, while retaining the source series reference. The stable national example supports these totals. The stable urban example includes custom mathematics and therefore produces series references without automatic totals. This omission is explained in the report.

## Select individual timesteps

Time series remain in their external files by default. To include selected cells, supply a list of selections:

```python
selection = [{
    "group": "results",
    "variable": "flow_out",
    "nodes": "region1",
    "techs": "ccgt",
    "carriers": "power",
    "timesteps": ["2005-01-01 00:00:00"],
}]
translator = Translator(
    "examples/calliope-0.7.0-glpk/national_scale/results_directory",
    groups={"structure"},
    time_points=selection,
)
translator.save("build/selected-times.nq")
```

The timestamp above exists in the national example. For your own export, copy the text exactly from its saved CSV. Supported selections are `results.flow_out` and `inputs.sink_use_equals`. Node, technology and carrier fields restrict the selection; omitting them selects all matching source coordinates at the requested times. A requested timestamp that matches no row is rejected. Output points retain their external-series link.

For the command-line interface, save the same list as YAML and pass it through `--time-points selections.yaml`.

## Supply study context and unit interpretations

An annotation file can add study and future-scenario descriptions, attributed assumptions and reasons, dataset history, unit interpretations and physical correspondences. These statements are not recovered automatically from ordinary numerical exports. The [annotation guide](../examples/annotations/README.md) explains the supported fields, required attribution and treatment of invalid input.

```python
annotated = Translator(
    "examples/calliope-0.7.0-glpk/national_scale/results_directory",
    annotations="examples/calliope-0.7.0-glpk/annotations/national.yaml",
    identity_file="build/capacities.nq.manifest.json",
)
annotated.save("build/annotated.nq")
reasons = run_query(annotated.translate(), "cq05")
```

This reuses the namespace of the earlier capacity export, so unchanged model components retain their identifiers. The example annotation file contains invented tutorial context with explicit labels. It is not evidence about the original authors' research process. Its capacity-unit interpretation has separate evidence in source comments.

Use `schema_version: 2` for annotations. A `contributor` helped create the information being recorded; a `supplier` supplied it. Defaults for these roles are separate, and neither assigns responsibility for a study or preparation process. A source report can identify its own `authors`, independently of the people adding annotations that cite it. See the [annotation guide](../examples/annotations/README.md) for examples and schema-1 migration instructions.

Supplied statements are checked for their required structure and relationships. Passing those checks does not establish their scientific truth. An empty answer may mean that the needed context was never supplied; consult the information requirements for that query before interpreting it.

## Understand the graph, manifest and report

Saving `build/model.nq` produces:

| File | Purpose |
|---|---|
| `model.nq` | The RDF dataset in N-Quads format. It can be read without the companion JSON files. |
| `model.nq.manifest.json` | A small record of the identifier namespace, configuration and execution fingerprints, and package and ontology versions. It supports deliberate reuse of identifiers when exporting again. |
| `model.nq.report.json` | Details of extracted content, omissions and their reasons, source checksums, available version evidence, selected groups and validation results. |

The graph uses the unchanged OEO distribution bundled with OntoCal. OEO relationships connect information to the processes that use and produce it; IAO software and RO participation describe the program involved. Actual saved execution times and the export's own times use OntoCal `startedAtTime` and `endedAtTime`. The model's simulated time labels remain separate. Source/version references are metadata and do not reproduce PROV derivation or specialisation rules.

The graph contains asserted statements. Source and computed statements, supplied annotation additions, and graph-generation provenance occupy separate named graphs. Ordinary queries use their union; queries about graph provenance retain the graph identifiers. Runtime SHACL validation checks the combined assertions against the packaged OntoCal profile. It does not add OWL-inferred triples or run the separate OWL reasoning evaluation.

A configuration fingerprint is a hash calculated from the saved definition, configuration, mathematics and input files. An execution fingerprint also includes recorded run metadata and result files. The manifest records these fingerprints, but reusing a manifest does not force two different configurations or executions to become the same entity. The same namespace and unchanged source content reproduce their respective identifiers.

The manifest is not a substitute for the source files, and it does not contain the graph. A valid graph remains readable after the manifest is removed. Keep both files when you intend to produce related exports with consistent identifiers; keep the detailed report to inspect what each export included.

## Identifiers across exports and repeated executions

A new export receives a random UUID namespace unless you supply one. The namespace gives its identifiers an independently generated prefix. Equal local names in unrelated exports therefore do not identify the same entity. Saving again to the same output path reuses the namespace from its companion manifest.

For a new output that should use an existing namespace:

```python
rerun = Translator(
    "saved-run-2",
    identity_file="build/model.nq.manifest.json",
)
rerun.save("build/run-2.nq")
```

The referenced identity file is updated with the latest export's fingerprints when saving. Alternatively, supply an absolute namespace you control through `namespace="https://example.org/my-study/"`. Keep distinct namespaces for independent studies unless you intend to coordinate their identifiers.

A technology identifier includes its configuration, node and technology name. A node and a technology with the same name remain distinct. An unchanged configuration retains its identifier across runs when the same namespace is used, while different recorded executions have different identifiers. Identical numerical results alone do not establish that two exports describe the same run.

A new translation also records its own graph-generation activity. Reusing model identifiers therefore does not merge the provenance of separately generated exports.

Fingerprints describe saved representations. They do not prove scientific equivalence between different byte encodings or differently organised exports. Preserve the original source files if you need to reproduce the identifiers.

## Supported formats and software-version evidence

The primary examples are under `examples/calliope-0.7.0-glpk/national_scale/results_directory/` and `examples/calliope-0.7.0-glpk/urban_scale/results_directory/`. Earlier exports under `examples/national_scale/` and `examples/urban_scale/` were produced by 0.7.0.dev7, a development preview. They remain distinct regression examples; their results have not been relabelled as stable outputs.

Stable 0.7.0 records component activation in `inputs_active.csv`; dev7 uses `inputs_definition_matrix.csv`. The reader handles the different dimensions and explicitly false carrier entries. Stable exports can retain inactive component definitions, which are not represented as active graph components. Transmission endpoints come from the applicable saved representation.

Stable `attrs.yaml` omits some values when they are software defaults. One is `runtime.calliope_version_initialised`, which records the version that initialised the model. In contrast, `config.init.calliope_version` is the version the configuration was intended for. The reader can use the intended version and available arrays to identify a supported format, but does not present that as evidence of the executable that produced the results.

The report distinguishes these fields:

| Report field | Meaning |
|---|---|
| `calliope_version` | The saved runtime initialisation version, or `null` when it was not recorded. |
| `calliope_configured_version` | The intended version stated in the configuration, when available. |
| `calliope_format_version` | The supported saved-array format selected by the reader. |
| `calliope_version_evidence` | The metadata or array layout used to select that format. |

The included examples' separate [preparation manifest](../examples/calliope-0.7.0-glpk/manifest.json) independently records the actual Calliope and GLPK versions used for those runs, together with source and result checksums. The unchanged native CSV exports retain their original omissions.

## Command-line equivalent

The command-line interface uses the same translator and query functions:

```sh
calliomapper translate examples/calliope-0.7.0-glpk/national_scale/results_directory \
  --groups capacities costs --out build/model.nq
calliomapper query build/model.nq --preset installed_capacity --out build/capacities.csv
calliomapper init-annotations --out annotations.yaml
```

Use `--annotations` to supply a YAML annotation file, `--identity-file` to reuse an identifier namespace, or `--namespace` to supply one explicitly. `init-annotations` refuses to overwrite an existing file.

The earlier `nodes=`, `techs=`, `run_id=`, `extension=` and custom-shapes prototype arguments have been replaced by this saved-export workflow. `init-extension` was an earlier placeholder and is not a supported compatibility interface. See the [change history](../CHANGELOG.md) and [evaluation](evaluation.md) for the scope of this release candidate.
