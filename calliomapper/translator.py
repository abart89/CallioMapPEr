"""Translate one saved, solved Calliope CSV export into validated RDF."""
from datetime import datetime, timezone
from importlib.resources import files
import json
from pathlib import Path
import uuid

from rdflib import Dataset, Literal, RDF, URIRef, XSD

from calliomapper.mapper.annotations import add_annotations
from calliomapper.mapper.core import MappingContext, add_structure
from calliomapper.mapper.quantities import add_quantities
from calliomapper.source import SavedModel, FIXTURE_TESTED_VERSIONS
from calliomapper.utils.validation import validate
from calliomapper.vocabulary import OC, PROV, DCT, ONTOLOGY_VERSION, PACKAGE_VERSION

DEFAULT_GROUPS = frozenset({"structure", "capacities", "energy", "costs"})


class Translator:
    """Read saved files, add optional supplied context, and validate assertions.

    A default UUID namespace is persisted next to saved output. Reusing that
    manifest or explicitly using the same namespace keeps entity identifiers
    stable. An unchanged configuration can therefore be linked to distinct runs.
    No model reconstruction, optimisation or OWL inference occurs here.
    """
    def __init__(self, results_dir, *, annotations=None, groups=None, time_points=None,
                 namespace=None, identity_file=None):
        self.source = SavedModel(results_dir)
        self.annotations = annotations
        self.groups = set(DEFAULT_GROUPS if groups is None else groups) | {"structure"}
        if self.groups - DEFAULT_GROUPS:
            raise ValueError(f"Unknown groups: {sorted(self.groups - DEFAULT_GROUPS)}")
        self.time_points = time_points
        self.namespace = namespace
        self.identity_file = Path(identity_file) if identity_file else None
        self._graph = None
        self.context = None
        self.report = {}
        if self.identity_file and self.identity_file.exists():
            self._read_identity(self.identity_file)

    def _read_identity(self, path):
        manifest = json.loads(path.read_text())
        if manifest.get("manifest_version") != 1 or not isinstance(manifest.get("namespace"), str):
            raise ValueError(f"Not a CallioMapper identity manifest: {path}")
        if self.namespace is not None and self.namespace != manifest["namespace"]:
            raise ValueError(f"Requested namespace differs from the persisted namespace in {path}")
        self.namespace = manifest["namespace"]

    def translate(self):
        if self._graph is not None:
            return self._graph
        self.namespace = self.namespace or f"urn:uuid:{uuid.uuid4()}:"
        ctx = MappingContext(self.source, self.namespace)
        add_structure(ctx)
        add_quantities(ctx, self.groups, self.time_points)
        asserted = set(ctx.graph)
        if self.annotations is not None:
            add_annotations(ctx, self.annotations)
        annotation_triples = set(ctx.graph) - asserted
        dataset = Dataset(default_union=True)
        provenance = dataset.graph(ctx.iri("graph", str(ctx.export_activity), "provenance"))
        for name, triples in (("source-and-computed", asserted), ("supplied-context", annotation_triples)):
            if not triples:
                continue
            graph = dataset.graph(ctx.iri("graph", str(ctx.export_activity), name))
            for triple in triples:
                graph.add(triple)
            provenance.add((graph.identifier, RDF.type, PROV.Entity))
            provenance.add((graph.identifier, PROV.wasGeneratedBy, ctx.export_activity))
            provenance.add((graph.identifier, DCT.conformsTo, URIRef(ONTOLOGY_VERSION)))
        provenance.add((ctx.export_activity, PROV.endedAtTime, Literal(datetime.now(timezone.utc), datatype=XSD.dateTime)))
        if self.annotations is not None:
            provenance.add((ctx.export_activity, OC.evidenceStatus, Literal("Includes user-supplied annotations; their validation does not establish scientific adequacy.")))
        shacl_report = validate(dataset)
        snapshot = json.loads(files("calliomapper").joinpath("resources/snapshot.json").read_text())
        ctx.report.update({
            "package_version": PACKAGE_VERSION, "ontology_version": ONTOLOGY_VERSION,
            "ontology_sha256": snapshot["sha256"]["ontocal.ttl"],
            "calliope_version": self.source.recorded_version,
            "calliope_format_version": self.source.version,
            "calliope_configured_version": self.source.configured_version,
            "calliope_version_evidence": self.source.version_evidence,
            "real_fixture_tested_version": self.source.version in FIXTURE_TESTED_VERSIONS,
            "namespace": self.namespace, "configuration": str(ctx.configuration), "execution": str(ctx.execution),
            "groups": sorted(self.groups), "time_points": self.time_points or [],
            "asserted_triples": len(asserted), "annotation_triples": len(annotation_triples),
            "shacl": "passed", "owl_reasoning": "not executed by translation", "shacl_report": shacl_report,
            "source_files": self.source.files,
            "scope": "Selected effective inputs and saved results. Global definition values and override history are not separately expanded into numerical assignments.",
        })
        self.report, self.context, self._graph = ctx.report, ctx, dataset
        return dataset

    def save(self, path):
        path = Path(path)
        manifest_path = path.with_suffix(path.suffix + ".manifest.json")
        if manifest_path.exists():
            self._read_identity(manifest_path)
        if self.identity_file and self.identity_file.exists():
            self._read_identity(self.identity_file)
        graph = self.translate()
        path.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(destination=str(path), format="nquads")
        manifest = {
            "manifest_version": 1, "namespace": self.namespace,
            "configuration_digest": self.source.configuration_digest,
            "execution_digest": self.source.execution_digest,
            "package_version": PACKAGE_VERSION, "ontology_version": ONTOLOGY_VERSION,
        }
        rendered = json.dumps(manifest, indent=2) + "\n"
        manifest_path.write_text(rendered)
        if self.identity_file:
            self.identity_file.parent.mkdir(parents=True, exist_ok=True)
            self.identity_file.write_text(rendered)
        path.with_suffix(path.suffix + ".report.json").write_text(json.dumps(self.report, indent=2) + "\n")
