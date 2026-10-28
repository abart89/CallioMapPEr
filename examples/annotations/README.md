# Adding information that is not recorded in the saved model

The saved Calliope files describe model structure, numerical inputs, calculated results and some execution metadata. They do not normally explain the study question, the future being investigated, or why someone selected an input. An optional annotation file supplies these statements explicitly. CallioMapper checks the structure of this file, identifies its referenced components and values, and writes the existing OntoCal relationships. It cannot establish whether a supplied scientific explanation is true.

[The stable national example](../calliope-0.7.0-glpk/annotations/national.yaml) is a complete demonstration. Its contributor, study, future scenario, reasons, dataset history and proposed plant are **invented for the tutorial**. They are not attributed to the original Calliope authors. Its two kW interpretations cite the original example's capacity comment and saved mathematical bound; those interpretations have their own evidence description. The earlier [dev7 annotation file](national.yaml) remains available for the preserved original outputs. Annotation processing never changes the saved numerical values or runs a model.

The example deliberately contains an assumption with no recorded reason. Missing explanations remain absent. Its future description does not reinterpret the saved 2005 model-time labels as evidence that a real future study took place. Use the default numerical content when trying this annotation file: a structure-only graph does not contain the quantities that its selectors require.

## Starting a real annotation file

The distributed [template](../../calliomapper/templates/annotations.yaml) is an empty, valid version-1 document. Add the sections you need; all sections except `schema_version: 1` are optional. The following tables describe the fields in full. Unknown fields, repeated YAML keys, repeated record identifiers and unresolved references are errors, rather than silently ignored text. Quote dates and coordinate labels so YAML reads them as text.

Every record has an `id` unique within the entire document. Local identifiers name the annotation records; they do not replace model component identifiers. Generated annotation identifiers also include the saved execution and a digest of the complete parsed annotation document. Consequently, editing an explanation or annotating another execution creates separate records. Explicit shared URIs for a study, scenario or dataset revision remain an intentional choice by the supplier. `uri` and fields ending in `_uri` require an absolute identifier, such as a producer-controlled HTTPS URI or a URN. Supplying an external identifier does not cause a network download.

Each export records that graph generation used a particular annotation revision. For a file, the revision digest identifies its exact YAML bytes. The export report separately records a digest of canonical JSON for the parsed document, so formatting-only YAML edits do not change the scientific annotation identifiers. An in-memory dictionary is represented by those canonical JSON bytes.

Every supplied claim identifies its `supplier` and `evidence_status`. The supplier is the `id` of one of the declared agents. `default_supplier` and `default_evidence_status` at the top of the document provide defaults, with individual records able to override them. The evidence status is a plain-English description such as “synthetic tutorial statement” or “supplied by the modeller from the cited report”; it is not a confidence score. Source and agent descriptions themselves do not require a supplier.

The optional `evidence` list names source records by `id`. Unit interpretations, dataset-use claims and physical correspondence require at least one evidence source. Other claims may lack a recorded source, but still require a supplier and an explicit evidence status.

## Declaring people and evidence sources

| Section | Required fields | Optional fields and meaning |
|---|---|---|
| `agents` | `id`, `label` | `kind`: `agent` (default), `person`, `organization` or `software`. `uri`: an existing identifier for the contributor. |
| `sources` | `id`, `title` | `uri`: identifier for the source. `locator`: passage, file location or other description of where to inspect it. `sha256`: 64 lowercase hexadecimal digits identifying recorded bytes. The mapper does not download a source or independently verify a supplied digest. |

An `evidence` reference identifies the source that supports a statement. A source title alone does not establish that it is empirical evidence. The tutorial therefore calls its invented report invented in both its title and the claims that cite it.

## Selecting model components and numerical records

A component selector is `{node: region1, technology: ccgt}`. For a node itself, omit `technology`. Alternatively, `{uri: 'https://…'}` identifies an already exported component. Names are interpreted within this export, so a repeated name in another model does not identify the same component.

A numerical selector contains `group`, `variable`, `node` and `technology`. `group` is `inputs` or `results`; `variable` is the exact saved variable name. Optional `carriers`, `costs` and `timesteps` supply the corresponding exact source coordinates. For example:

```yaml
target:
  group: results
  variable: flow_cap
  node: region1
  technology: ccgt
  carriers: power
```

The selector must find exactly one exported record. If two carriers match, specify `carriers`; if time points match, specify `timesteps`. An annotation cannot silently request a quantity that the selected export groups omit. For an output-series descriptor or a computed summary, add `kind: series` or `kind: summary`. The default `kind: record` selects an ordinary input assignment or result. Unit interpretations require a numerical record or summary, because a series descriptor has no single numerical value to interpret.

## Recording a study, scenarios and assumptions

| Section | Required fields | Optional fields and meaning |
|---|---|---|
| `scenarios` | `id`, `label`, `description` | `uri` can identify a shared scenario across exports. `implemented_by_configuration`: `true` explicitly says this saved configuration implements the described future. The default is `false`. Supplier and evidence fields apply. |
| `study` | `id`, `title`, `question`, `scenarios` | This is one mapping, not a list. `uri` can identify the same study in multiple exports; each supplied study record then includes its own saved execution. `scenarios` names declared scenario IDs. `reference_scenario` designates one of them as the reference for this study. Supplier and evidence fields apply. |
| `assumptions` | `id`, `statement`, `scenario`, `targets` | `scenario` names one declared future. `targets` is a non-empty list of numerical input selectors. `reasons` optionally contains separately attributed explanations. Supplier and evidence fields apply. |
| Each item in `reasons` | `id`, `statement` | Supplier and evidence fields apply independently, so different people can supply different reasons. |

The study includes the saved execution. Its question is represented as information about the study, while the study itself is an activity. A scenario is an information representation of a future; it is not a new run or another name for the configuration. An assumption explains a supplied input choice. A calculated result cannot be selected as the input that implements an assumption.

## Giving a numerical value an evidenced unit

Each item in `units` requires `id`, `target`, `unit_class`, `label` and a non-empty `evidence` list, together with supplier and evidence status. The unit class is the ontology identifier for the unit, such as `https://openenergyplatform.org/ontology/oeo/OEO_00390000` for kW. The mapper creates a quantity interpretation with the original numeral and that unit. It does not convert the number, overwrite the raw value or infer a currency from the word `monetary`.

The first version accepts only these verified unit classes, with the exact labels shown:

| Meaning | `unit_class` | `label` |
|---|---|---|
| Kilowatt | `https://openenergyplatform.org/ontology/oeo/OEO_00390000` | `kW` |
| Megawatt | `https://openenergyplatform.org/ontology/oeo/OEO_00390001` | `MW` |
| Kilowatt-hour | `http://purl.obolibrary.org/obo/UO_0000224` | `kWh` |
| Megawatt-hour | `https://openenergyplatform.org/ontology/oeo/OEO_00050008` | `MWh` |
| Dimensionless ratio | `http://purl.obolibrary.org/obo/UO_0000190` | `1` |

The selected record must already have the corresponding power, energy or dimensionless quantity dimension from the saved mathematical metadata. Currency and compound cost-unit interpretations are outside this initial implementation; cost numbers remain available with their reported dimension and cost category. A general currency class does not identify a concrete currency, price year or accounting basis.

A second interpretation of the same datum is rejected, so contradictory unit claims cannot accumulate silently. Evidence is still needed when the intended unit seems obvious from a variable name. A label such as “kW” alone is not sufficient evidence.

## Recording dataset use and preparation

Each item in `datasets` requires `id`, `title`, `revision_uri`, a non-empty list of input `targets`, and non-empty `evidence`. Supplier and evidence fields apply. `family_uri` optionally identifies the dataset across revisions; `previous_revision_uri` identifies a previous revision. Neither may equal the selected revision. The mapper records that the targeted input data derive from this revision and that the saved execution used it. This is a supplied history assertion, distinct from the automatically identified revision of a CSV file.

An optional `preparation` mapping has its own `id`, `description` and non-empty `inputs` list of source IDs, with supplier and evidence status. It records an activity that used those sources and generated the selected dataset revision. It does not perform that activity, fabricate dates, or imply that CallioMapper observed it. Two exports can refer to the same explicitly identified dataset revision without merging their configurations or results.

## Recording correspondence

Each item in `physical_correspondences` requires `id`, `component`, `kind`, `scope`, `target_uri`, `target_label`, and non-empty `evidence`, plus supplier and evidence status.

- `actual` records a supplied claim about a material target. It is not independent verification that an asset exists.
- `aggregate` identifies an information description of an aggregate, such as a portfolio description. It does not create a material collection from a name.
- `hypothetical` identifies an information description of a proposed arrangement. It never asserts a physically existing plant.

The scope states which aspect is represented, such as installed capacity only. Model and target identifiers remain distinct. A single identifier cannot be used as both a material target and an information description. Supplied annotation URIs cannot reuse identifiers for the current model, configuration, components or executions. Checks also reject a shared annotation URI that would acquire both activity and information/material types.

Each item in `component_correspondences` requires `id`, `source`, `target` and `reason`, together with supplier and evidence status. The source is a local component selector. The target may be another local selector or an explicit external `{uri: 'https://…'}`. An external URI is a supplied assertion that the target is a model component; no other facts are invented for it. This relation records a pairing for a stated reason. It does not assert identity, matching units, matching time periods or a causal explanation for a difference. Comparisons must check those conditions separately.

## What errors mean

If one record is invalid, CallioMapper rejects the annotation document without adding part of it to the graph. Typical corrections are to declare the missing supplier, fix a misspelled coordinate, request the numerical export group containing the target, or separate a proposed plant description from an actual asset identifier. A successful validation checks that the supplied statements fit the supported representation; it does not replace review of their scientific meaning.
