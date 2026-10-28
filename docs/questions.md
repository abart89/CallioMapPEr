# What each question can answer, and what information it needs

CallioMapper includes eight queries corresponding to the OntoCal competency questions. They ask different kinds of question, so they do not all have the same information requirements. Some can be answered from the saved Calliope export. Others need information supplied by a modeller or another system.

The queries inspect statements actually present in the graphs. They do not run an OWL reasoner, infer a modeller's intentions, identify physical plants from names, or convert numerical units. A query with no matching answer does not establish that the requested fact is false. The export report explains omitted source quantities; the requirements printed by each query explain what information the question needs.

| Query | Question and supported answer | Content required from the saved export | Additional information required |
|---|---|---|---|
| `cq01` | Which technology components occur at which nodes, with which carriers and transmission endpoints? | System structure. | None for model structure. A physical interpretation needs separate evidence. |
| `cq02` | Which execution, configuration, modelled period, study and future scenario are described? | Structure and recorded execution/time metadata. | The study purpose, spatial interpretation and future-scenario meaning when these are absent from the saved files. Executions still appear when these fields are unavailable. |
| `cq03` | What selected inputs, saved results and calculated summaries are recorded? | The requested capacity, energy or cost groups, or explicitly selected time points. | A particular unit, such as kW, needs an evidenced unit interpretation when the saved file does not establish it. Numbers remain queryable with an empty unit field. |
| `cq04` | What sources, generating activities and responsible agents are recorded? | File references, execution metadata and automatic graph-generation provenance. | Earlier dataset preparation and responsibility when not recorded in the source. A file reference identifies where information was represented; it does not by itself establish causal derivation. |
| `cq05` | Which supplied assumptions explain an input, and what reasons were recorded? | The selected input assignment. | An attributed assumption connected to that assignment. Reasons and citations can be supplied independently. An assumption with no reason still appears. |
| `cq06` | How do explicitly paired capacity bounds and calculated capacities differ between a reference and alternative scenario? | Successful executions, selected capacity inputs/results and compatible modelled-time descriptions. | A common study, explicit reference/alternative scenarios, component correspondence and supported concrete unit interpretations. The exact comparison restrictions are explained below. |
| `cq07` | Which independently identified exports report using an explicitly shared dataset revision, and what does a separate catalogue say about its publisher? | Named graphs retaining model, execution, result and graph-generation identities. | Explicit dataset-revision use, study metadata and a separately identified catalogue graph with publisher metadata. A repeated local name does not establish shared identity. |
| `cq08` | What actual, aggregate or hypothetical physical correspondence has been supplied for a model component? | Component identifiers. | An attributed correspondence, its target, scope, interpretation and evidence. Components with no supplied assertion remain visible with empty claim fields. |

For example, a default export can answer the structural part of CQ-01 and the supported numerical part of CQ-03. It cannot explain why a modeller chose a capacity bound unless that explanation was recorded and supplied. Providing the annotation file extends the available information; it does not turn a supplied explanation into a fact extracted automatically from Calliope.

## Running and narrowing a question

The command below writes the available numerical answers as a table:

```bash
calliomapper query build/national.nq --preset cq03 --out build/quantities.csv
```

The query names are `cq01` through `cq08`. Two additional names select common numerical results: `installed_capacity` returns saved `flow_cap` records, and `system_costs` returns saved component `cost` records. The latter name does not mean that the query calculates a system-wide total. It preserves the component and cost category, and leaves the unit empty when no currency interpretation is established.

In Python, `run_query` returns an RDFLib query result. You can narrow an answer by binding variables used in the query:

```python
from rdflib import Dataset, URIRef
from calliomapper.queries import run_query

data = Dataset(default_union=True)
data.parse("build/national.nq", format="nquads")

for row in run_query(data, "cq03", {"technology": "ccgt", "variable": "flow_cap"}):
    print(row.node, row.value, row.unit)
```

Strings select literal values, such as a Calliope technology name. Use `URIRef` when selecting an entity identifier, for example `{"runA": URIRef("..."), "runB": URIRef("...")}` for a particular comparison pair. Unknown variable names produce an error. Parameter values are passed as RDF terms rather than inserted into query text.

Each query is also available as a readable SPARQL file in [`calliomapper/query_files`](../calliomapper/query_files/). These files use vocabulary identifiers but contain no fixed example entity identifiers. The Python helper queries the union of the named graphs while preserving those graphs. CQ-07 explicitly inspects the named export and catalogue graphs so that their identities remain part of its answer.

## What a capacity comparison establishes

CQ-06 is deliberately bounded. It compares `flow_cap_max` with `flow_cap`, or `storage_cap_max` with `storage_cap`. It does not promise to compare arbitrary numerical variables or infer which outputs should be compared because they have similar names.

The two runs must have successful status, belong to the same supplied study, and use configurations associated with that study's reference and alternative scenarios. A supplied component-correspondence assertion identifies the two components. If several runs satisfy these conditions, the query shows their identifiers separately; bind `runA` and `runB` when a particular pair is intended.

Inputs are compared with inputs having the same variable and coordinate structure; results are compared with corresponding results. A carrier coordinate absent from both input arrays stays absent. A coordinate present on only one side does not count as a match. The selected pattern excludes records with a timestep coordinate.

All four values need supported interpretations using the same concrete unit class and label: kW, MW, kWh or MWh, as appropriate. Two independently created unit individuals can therefore both represent kW without needing the same identifier. A kW/MW pair does not pass, even though a person could convert it. Generic unit or currency labels are insufficient. No unit conversion occurs.

Both configurations also need the same first and last model-time labels and coordinate count. Beyond those summary fields, the query requires either an explicitly shared temporal-description identifier or equal checksums for the complete saved timestep-weight and timestep-duration files. Equal endpoints and counts alone do not demonstrate equal temporal treatment. This deliberately conservative check can reject scientifically equivalent files with different encodings; no automatic equivalence claim is made.

A resulting numerical difference is descriptive. It does not establish that the supplied assumption caused the difference or that the two model configurations differ only in that assumption.

## Worked comparison and integration example

From the repository root, with CallioMapper installed, run:

```bash
python examples/annotations/compare_exports.py build/independent-exports
```

The script reads the stable 0.7.0 national example's existing results directory (`examples/calliope-0.7.0-glpk/national_scale/results_directory`) and creates two independently identified exports. It writes a source-only version and an annotated version for each producer, together with the exact annotation files, a small catalogue, comparison/integration answer tables and a `checks.json` report.

**Both exports describe the same saved Calliope execution.** The script neither solves a model nor changes a number. The reference and alternative future descriptions are invented tutorial context. The expected capacity differences are therefore zero. This checks that independently identified records can be compared when the required context is supplied; it is not evidence from a real two-scenario experiment.

The producers retain distinct component identifiers despite repeated names. They share a dataset-revision identifier only because the annotations deliberately supply that same identifier. A separately identified, explicitly fictional catalogue supplies its publisher metadata. The source-only export has no assumption answers; the annotated export does.

The script also checks three deliberately altered copies in memory: one with an incompatible unit, one with a missing unit and one with a different time horizon. CQ-06 must refuse all three comparisons. These copies are test cases and are not saved as valid exports.

The generated files remain local build outputs. The saved Calliope example files are unchanged. Repeating the script reuses the export identity manifests, so it does not allocate a new producer identity every time the demonstration is refreshed.
