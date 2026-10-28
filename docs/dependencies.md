# Ontology dependencies and our local modifications

CallioMapper includes a fixed copy of the OntoCal draft identified by `https://w3id.org/ontocal/draft/2026-10-22-stage1`. It uses OEO 2.12.0 and PROV-O of 30 April 2013 through explicitly identified local derivatives. The release candidate uses these fixed derivatives and preserves their identities and transformation records.

The authoritative editable ontology belongs to the OntoCal project. Files under `calliomapper/resources/` are copied dependencies, not another editable ontology. `snapshot.json` records their SHA-256 checksums. The package's runtime dependency set is RDFLib, pySHACL and PyYAML; ordinary translation does not require Calliope, LinkML, Java, an ontology server or network downloads.

## Calliope used to prepare the examples

The primary saved examples were prepared with the stable Calliope **0.7.0** release and GLPK **5.0** in a separate environment. [Their manifest](../examples/calliope-0.7.0-glpk/manifest.json) records the actual preparation software, sources, outputs and checksums; [the preparation requirements](../examples/calliope-0.7.0-glpk/preparation-requirements.txt) record that environment's dependencies. These are preparation dependencies, not packages a user must install to translate an existing export. Routine checks read the included CSV files and do not solve the models again. The original 0.7.0.dev7 exports remain as separate regression evidence.

Calliope's stable CSV export normally omits its executable-version field. A configured target of 0.7.0 helps the reader interpret the format, but does not establish the version actually used for a particular run. CallioMapper keeps these statements separate. The included examples have independent executable-version evidence in their preparation manifest; arbitrary user exports may not.

## Changes made by this project

OEO's full distribution uses `prov:wasDerivedFrom` as an annotation property for ontology-source metadata. PROV-O defines that same identifier as an object property between entities. Loading both unchanged creates an OWL property-category conflict in the selected reasoning workflow. Our OEO derivative relocates the source-metadata predicate to `urn:ontocal:dependency:metadata:wasDerivedFrom`. The standard PROV-O object property remains available for data provenance. The recorded transformation covers 2087 metadata uses and six description triples.

The PROV-O derivative removes the annotation-property declarations of `prov:wasRevisionOf` and `prov:specializationOf`, retaining their object-property declarations. Two source-document assertions are preserved separately in `relocated-source-metadata.ttl` rather than asserted as provenance relationships in the reasoning input.

The resulting ontology identifiers are:

- `urn:ontocal:dependency:oeo-2.12.0-dl`, version `urn:ontocal:dependency:oeo-2.12.0-dl:1`.
- `urn:ontocal:dependency:prov-o-20130430-dl`, version `urn:ontocal:dependency:prov-o-20130430-dl:1`.

These are our derivatives. They are not changes to the upstream projects, official upstream releases, or new definitions of the domain classes. Original files remain alongside the derivatives. Transformation scripts, removed/added triples and detailed manifests are included in [the dependency directory](../calliomapper/resources/dependencies/derived/README.md).

That bundled README is preserved from the OntoCal repository. Its reproduction
commands and historical evidence paths refer to that repository, including a
dependency-verification script that is not bundled with CallioMapper. For checks
in this package, use [scripts/check_owl.py](../scripts/check_owl.py), following the
prerequisites in the [evaluation instructions](evaluation.md). It checks generated
example graphs with the bundled ontology and imports; it does not require an
OntoCal checkout or repeat the original dependency-comparison suite.

## What the verification does and does not establish

The recorded comparison preserves the 4004 unannotated OEO logical axioms. PROV-O's OWL parsing has four identified differences: two relocated header assertions and two range interpretations associated with resolving the duplicate property declarations. This is not a claim of complete RDF equivalence or that the changes are purely cosmetic.

The fixed combination is tested with OntoCal and selected generated graphs. That evidence does not establish compatibility with arbitrary external ontology versions, unrestricted graph unions or every PROV constraint. Users should retain the dependency identities when repeating formal checks. Runtime SHACL checks required relationships and data constraints; it does not replace an OWL reasoner or scientific review.

The source headers, OEO attribution metadata, CC0 notice and reuse metadata are retained. They identify upstream contributions; the package metadata is not a claim that we authored or relicensed those contributions. The root NOTICE identifies the third-party material; retained source records provide its attribution and terms.

Use of these derivatives does not imply endorsement by the OEO or W3C projects. Changes to their import strategy require a new documented dependency snapshot and verification.

## Updating the bundled snapshot

After a new OntoCal version is reviewed, run:

```sh
python scripts/sync_ontology_resources.py /path/to/ontocal
```

Review the version, manifest and dependency changes, then rerun package and formal checks. Do not regenerate the ontology from the historical LinkML files or edit the bundled dependency files directly.
