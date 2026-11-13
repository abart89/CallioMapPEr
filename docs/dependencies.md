# Ontology dependencies and the OEO-based representation

CallioMapper `0.1.0rc3` includes the OntoCal draft `https://w3id.org/ontocal/draft/2026-11-13-stage1`. That draft imports the complete publisher distribution of OEO 2.12.0 unchanged. It includes the BFO, IAO, RO and other definitions selected in that OEO release. This package candidate does not import PROV-O or the modified dependency copies used by rc2.

The authoritative editable ontology belongs to the separate OntoCal project. Files under `calliomapper/resources/` are distribution copies, not another authoring source. [snapshot.json](../calliomapper/resources/snapshot.json) identifies the copied files and their SHA-256 checksums. The local import catalogue directs ontology software to the saved OEO file, rather than downloading an unspecified later version.

Ordinary translation uses RDFLib, pySHACL and PyYAML. It requires neither Calliope nor LinkML, Java, an ontology server or network downloads. Java and ROBOT are separate developer requirements for the formal reasoning checks.

## What the current representation says about provenance

Suppose a model calculation uses a configuration and produces a capacity result. OEO information-input and information-output relationships connect those records. A known preparation process or the package's later summary calculation can be recorded in the same way. The package does not invent an earlier preparation process merely because a source report is named.

A modeller who creates an explanation citing a report can be recorded as a contributor to the explanation through OEO `has contributor`. The report can separately identify its known author through OEO `has author`. Someone who only supplies information can instead be recorded through OntoCal `suppliedBy`. These roles are not interchangeable. The [annotation guide](../examples/annotations/README.md) explains the schema-2 fields and how to preserve older supplier information.

Software is described as IAO software participating in a process through RO `has participant`. OntoCal `hasResponsibleAgent` identifies a responsible person or organisation when explicitly supplied. Participation does not establish responsibility. Optional local `startedAtTime` and `endedAtTime` properties preserve recorded actual process times; simulated model-time labels have a separate description.

Dublin Core `source` and `isVersionOf`, and OntoCal `previousRevision`, retain queryable source and revision references. They are descriptive annotations in this representation. They do not reproduce PROV-O's automatic conclusions about derivation, revision or specialisation. This first version also does not provide detailed delegation, approvals or role-qualified responsibility. A PROV export and assessment of the published PROV-to-BFO alignment are later work.

## Why PROV names may still appear in the dependency file

OEO's publisher file contains metadata describing where ontology terms came from, including properties with PROV identifiers. Those statements remain unchanged. Their presence is different from importing the PROV-O ontology to describe provenance between model records.

The earlier project investigation found property-declaration conflicts when the selected complete OEO and PROV files were combined for OWL 2 DL reasoning. The earlier candidate used documented modified copies. The adopted first version instead uses unchanged OEO without importing PROV-O. The history remains in the OntoCal repository and the earlier package commits; it is not an active dependency requirement for rc3. This choice does not establish that the complete published OEO and PROV files can be loaded together unchanged under that reasoning regime.

## What the verification establishes

Runtime SHACL checks whether generated records contain required information and relationships. For example, it can reject an explanation lacking both a contributor and supplier. It does not establish the scientific truth of the explanation and does not run an OWL reasoner.

The separate [OWL checks](../scripts/check_owl.py) combine generated example graphs with the bundled ontology and unchanged OEO. They check the permitted OWL structure, look for logical contradictions and test selected consequences. A deliberately invalid statement must fail in the intended way. See [evaluation.md](evaluation.md) for the actual candidate results and limits. These checks do not guarantee compatibility with arbitrary extra ontology versions or graph unions.

The original source header, attribution metadata and OEO licensing records are retained. These identify upstream contributions; the package does not claim authorship of those definitions. The root [NOTICE](../NOTICE) records the bundled third-party material. Reusing a shared vocabulary does not imply endorsement by its developers.

## Calliope used to prepare the examples

The primary saved examples were prepared with Calliope 0.7.0 and GLPK 5.0 in a separate environment. [Their manifest](../examples/calliope-0.7.0-glpk/manifest.json) records preparation software, sources, outputs and checksums; [preparation requirements](../examples/calliope-0.7.0-glpk/preparation-requirements.txt) identify that environment. These are not packages a user must install to translate an existing export. Routine checks read the included CSV files and do not solve models again. The original 0.7.0.dev7 exports remain separate regression cases.

A configured Calliope target version helps identify the format but does not establish which executable produced a particular run. Stable CSV exports normally omit that executable-version field. The included examples have separate preparation evidence; arbitrary user exports may not. CallioMapper keeps the software identity visible while leaving an unknown version unrecorded.

## Updating the bundled snapshot

After an ontology change has been reviewed, run:

```sh
python scripts/sync_ontology_resources.py /path/to/ontocal
```

Review the ontology version, copied files and checksum record, then rerun package and formal checks. The bundle should contain the active unchanged OEO dependency, not accidentally retain earlier modified imports. Do not regenerate the ontology from historical LinkML files or edit the bundled ontology independently of its authoring source.
