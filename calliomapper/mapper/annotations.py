"""Validate supplied scientific context and add the reviewed OntoCal patterns.

This module does not infer intentions or read prose as evidence. Selectors refer
only to records already created from the saved export. A rejected document leaves
the graph unchanged.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
from urllib.parse import urlsplit

import yaml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

OC = Namespace("https://w3id.org/ontocal/")
OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
PROV = Namespace("http://www.w3.org/ns/prov#")

# Fixed unit classes verified in the bundled OEO 2.12.0 dependency.
SUPPORTED_UNITS = {
    OEO.OEO_00390000: ("power", "kW"),
    OEO.OEO_00390001: ("power", "MW"),
    OBO.UO_0000224: ("energy", "kWh"),
    OEO.OEO_00050008: ("energy", "MWh"),
    OBO.UO_0000190: ("dimensionless", "1"),
}


def _literal(value):
    return Literal(value, datatype=XSD.string)


class AnnotationError(ValueError):
    """A supplied annotation is incomplete, ambiguous or contradictory."""


class _UniqueKeysLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise AnnotationError(f"Annotation YAML contains a repeated or non-text key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeysLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise AnnotationError(f"{where} must be non-empty text")
    return value


def _uri(value, where):
    value = _text(value, where)
    if not urlsplit(value).scheme or re.search(r'[\s<>"{}|\\^`]', value):
        raise AnnotationError(f"{where} must be an absolute URI without spaces")
    return URIRef(value)


def _keys(value, allowed, required, where):
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise AnnotationError(f"{where} must be a mapping with text keys")
    unknown, missing = set(value) - set(allowed), set(required) - set(value)
    if unknown or missing:
        raise AnnotationError(f"{where}: unknown fields {sorted(unknown)}; missing fields {sorted(missing)}")


def _list(value, where, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise AnnotationError(f"{where} must be a {'non-empty ' if nonempty else ''}list")
    return value


class _Annotations:
    def __init__(self, ctx, document):
        self.ctx, self.document = ctx, document
        self.graph = Graph()
        for triple in ctx.graph:
            self.graph.add(triple)
        self.ids, self.agents, self.sources, self.scenarios = set(), {}, {}, {}
        self.counts = {}
        try:
            canonical = json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise AnnotationError("Annotations require JSON-compatible values; quote dates and use text field names") from exc
        self.digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def annotation_iri(self, *keys):
        return self.ctx.iri("annotation", str(self.ctx.execution), self.digest, *keys)

    def record(self, record, fields, required, where, *, claim=True):
        common = {"id", "supplier", "evidence_status", "evidence"} if claim else {"id"}
        _keys(record, common | set(fields), {"id"} | set(required), where)
        identifier = _text(record["id"], f"{where}.id")
        if identifier in self.ids:
            raise AnnotationError(f"Repeated annotation id {identifier!r}; ids must be unique throughout the document")
        self.ids.add(identifier)
        return self.annotation_iri(identifier)

    def external_uri(self, value, where):
        subject = _uri(value, where)
        reserved = {self.ctx.configuration, self.ctx.model, self.ctx.execution}
        if hasattr(self.ctx, "export_activity"):
            reserved.add(self.ctx.export_activity)
        reserved.update(self.ctx.components.values())
        reserved.update(self.ctx.nodes.values())
        if subject in reserved:
            raise AnnotationError(f"{where} cannot reuse an identifier belonging to the model, its components or an execution")
        return subject

    def types(self, subject, *classes):
        existing = set(self.graph.objects(subject, RDF.type)) | set(classes)
        information = {OBO.IAO_0000030, OBO.IAO_0000027, OEO.OEO_00000276,
                       OEO.OEO_00000364, OEO.OEO_00000063, OEO.OEO_00000350}
        material = {OBO.BFO_0000040, OEO.OEO_00000031}
        processes = {PROV.Activity, OBO.BFO_0000015, OBO.BFO_0000003, OEO.OEO_00010252}
        if ({PROV.Activity, PROV.Entity} <= existing or
                (existing & information and existing & material) or
                (existing & processes and existing & (information | material | {OBO.BFO_0000002}))):
            raise AnnotationError(f"Identifier {subject} would have incompatible activity, information or material types")
        for cls in classes:
            self.graph.add((subject, RDF.type, cls))

    def claim(self, subject, record, *, evidence_required=False, activity=False):
        self.graph.add((subject, DCTERMS.identifier, _literal(record["id"])))
        supplier = _text(record.get("supplier", self.document.get("default_supplier")), f"{record['id']}.supplier")
        if supplier not in self.agents:
            raise AnnotationError(f"{record['id']}: supplier must identify a declared agent")
        self.graph.add((subject, PROV.wasAssociatedWith if activity else PROV.wasAttributedTo, self.agents[supplier]))
        status = record.get("evidence_status", self.document.get("default_evidence_status"))
        self.graph.add((subject, OC.evidenceStatus, _literal(_text(status, f"{record['id']}.evidence_status"))))
        for ref in _list(record.get("evidence", []), f"{record['id']}.evidence", nonempty=evidence_required):
            _text(ref, "source reference")
            if ref not in self.sources:
                raise AnnotationError(f"{record['id']}: unknown evidence source {ref!r}")
            self.graph.add((subject, PROV.used if activity else PROV.wasDerivedFrom, self.sources[ref]))

    def component(self, selector, *, external=False):
        _keys(selector, {"node", "technology", "uri"}, set(), "component selector")
        if "uri" in selector:
            if len(selector) != 1:
                raise AnnotationError("A component URI cannot be combined with node/technology selectors")
            uri = _uri(selector["uri"], "component.uri")
            if not external and uri not in set(self.ctx.components.values()) | set(self.ctx.nodes.values()):
                raise AnnotationError("The component URI does not identify a component in this export")
            return uri
        node = _text(selector.get("node"), "component.node")
        key = (node, _text(selector["technology"], "component.technology")) if "technology" in selector else node
        mapping = self.ctx.components if "technology" in selector else self.ctx.nodes
        if key not in mapping:
            raise AnnotationError(f"Unknown component selector {selector!r}")
        return mapping[key]

    def target(self, selector):
        _keys(selector, {"group", "variable", "node", "technology", "carriers", "costs", "timesteps", "kind"},
              {"group", "variable", "node", "technology"}, "record selector")
        component = self.component({"node": selector["node"], "technology": selector["technology"]})
        group = _text(selector["group"], "record selector.group")
        if group not in {"inputs", "results"}:
            raise AnnotationError("record selector.group must be inputs or results")
        kind = _text(selector.get("kind", "record"), "record selector.kind")
        if kind not in {"record", "summary", "series"} or (group == "inputs" and kind != "record"):
            raise AnnotationError("Selector kind must be record, or summary/series for results")
        cls = {"record": OC.InputAssignment if group == "inputs" else OC.ResultRecord,
               "summary": OC.AggregatedResultRecord, "series": OC.TimeSeriesRecord}[kind]
        variable = _text(selector["variable"], "record selector.variable")
        candidates = []
        for record in self.graph.subjects(RDF.type, cls):
            if (record, OC.forComponent, component) not in self.graph or (record, OC.sourceKey, _literal(variable)) not in self.graph:
                continue
            if (record, OC.inConfiguration, self.ctx.configuration) not in self.graph:
                continue
            if all((record, predicate, _literal(_text(selector[key], f"selector.{key}"))) in self.graph
                   for key, predicate in (("carriers", OC.carrierIndex), ("costs", OC.costIndex), ("timesteps", OC.timeIndexLabel))
                   if key in selector):
                candidates.append(record)
        if len(candidates) != 1:
            raise AnnotationError(f"Record selector must resolve to exactly one exported record; found {len(candidates)} for {selector!r}")
        return candidates[0]

    def build(self):
        allowed = {"schema_version", "default_supplier", "default_evidence_status", "agents", "sources", "study", "scenarios", "assumptions", "units", "datasets", "physical_correspondences", "component_correspondences"}
        _keys(self.document, allowed, {"schema_version"}, "annotation document")
        if type(self.document["schema_version"]) is not int or self.document["schema_version"] != 1:
            raise AnnotationError("schema_version must be the integer 1")
        if "default_evidence_status" in self.document:
            _text(self.document["default_evidence_status"], "default_evidence_status")
        for section in allowed - {"schema_version", "default_supplier", "default_evidence_status", "study"}:
            _list(self.document.get(section, []), section)
        for record in self.document.get("agents", []):
            subject = self.record(record, {"label", "kind", "uri"}, {"label"}, "agent", claim=False)
            subject = self.external_uri(record["uri"], "agent.uri") if "uri" in record else subject
            kind = _text(record.get("kind", "agent"), "agent.kind")
            if kind not in {"agent", "person", "organization", "software"}:
                raise AnnotationError("agent.kind must be agent, person, organization or software")
            self.types(subject, PROV.Agent)
            if kind != "agent":
                self.types(subject, {"person": PROV.Person, "organization": PROV.Organization, "software": PROV.SoftwareAgent}[kind])
            self.graph.add((subject, RDFS.label, _literal(_text(record["label"], "agent.label"))))
            self.graph.add((subject, DCTERMS.identifier, _literal(record["id"])))
            self.agents[record["id"]] = subject
        if "default_supplier" in self.document and _text(self.document["default_supplier"], "default_supplier") not in self.agents:
            raise AnnotationError("default_supplier must identify a declared agent")
        for record in self.document.get("sources", []):
            subject = self.record(record, {"title", "uri", "locator", "sha256"}, {"title"}, "source", claim=False)
            subject = self.external_uri(record["uri"], "source.uri") if "uri" in record else subject
            self.types(subject, OBO.IAO_0000030, PROV.Entity)
            self.graph.add((subject, DCTERMS.title, _literal(_text(record["title"], "source.title"))))
            if "locator" in record:
                self.graph.add((subject, OC.sourceLocator, _literal(_text(record["locator"], "source.locator"))))
            if "sha256" in record:
                digest = _text(record["sha256"], "source.sha256")
                if not re.fullmatch(r"[0-9a-f]{64}", digest):
                    raise AnnotationError("source.sha256 must contain 64 lowercase hexadecimal digits")
                self.graph.add((subject, OC.contentSHA256, _literal(digest)))
            self.graph.add((subject, DCTERMS.identifier, _literal(record["id"])))
            self.sources[record["id"]] = subject
        for record in self.document.get("scenarios", []):
            subject = self.record(record, {"label", "description", "implemented_by_configuration", "uri"}, {"label", "description"}, "scenario")
            subject = self.external_uri(record["uri"], "scenario.uri") if "uri" in record else subject
            self.types(subject, OEO.OEO_00000364, PROV.Entity)
            self.graph.add((subject, RDFS.label, _literal(_text(record["label"], "scenario.label"))))
            self.graph.add((subject, RDFS.comment, _literal(_text(record["description"], "scenario.description"))))
            self.claim(subject, record)
            implemented = record.get("implemented_by_configuration", False)
            if type(implemented) is not bool:
                raise AnnotationError("implemented_by_configuration must be true or false")
            if implemented:
                self.graph.add((self.ctx.configuration, OC.implementsScenario, subject))
            self.scenarios[record["id"]] = subject
        if "study" in self.document:
            self.study(self.document["study"])
        for section, method in (("assumptions", self.assumption), ("units", self.unit), ("datasets", self.dataset),
                                ("physical_correspondences", self.physical), ("component_correspondences", self.correspondence)):
            for record in self.document.get(section, []):
                method(record)
        self.counts = {section: len(self.document.get(section, [])) for section in allowed - {"schema_version", "default_supplier", "default_evidence_status", "study"}}
        self.counts["study"] = int("study" in self.document)

    def study(self, record):
        subject = self.record(record, {"title", "question", "scenarios", "reference_scenario", "uri"}, {"title", "question", "scenarios"}, "study")
        subject = self.external_uri(record["uri"], "study.uri") if "uri" in record else subject
        self.types(subject, OEO.OEO_00010252, OBO.BFO_0000015, PROV.Activity)
        self.claim(subject, record, activity=True)
        self.graph.add((subject, RDFS.label, _literal(_text(record["title"], "study.title"))))
        self.graph.add((subject, DCTERMS.title, _literal(record["title"])))
        self.graph.add((subject, OBO.BFO_0000051, self.ctx.execution))
        self.graph.add((self.ctx.execution, OBO.BFO_0000050, subject))
        description = self.annotation_iri(record["id"], "description")
        self.types(description, OBO.IAO_0000030, PROV.Entity)
        self.graph.add((description, OBO.IAO_0000136, subject))
        self.graph.add((description, DCTERMS.description, _literal(_text(record["question"], "study.question"))))
        self.claim(description, record)
        for scenario in _list(record["scenarios"], "study.scenarios", nonempty=True):
            if _text(scenario, "study scenario") not in self.scenarios:
                raise AnnotationError(f"Unknown study scenario {scenario!r}")
            self.graph.add((subject, OEO.OEO_00020226, self.scenarios[scenario]))
        if "reference_scenario" in record:
            ref = record["reference_scenario"]
            if ref not in record["scenarios"]:
                raise AnnotationError("reference_scenario must be one of this study's scenarios")
            self.graph.add((subject, OC.referenceScenario, self.scenarios[ref]))
            self.types(self.scenarios[ref], OEO.OEO_00020314)

    def assumption(self, record):
        subject = self.record(record, {"statement", "scenario", "targets", "reasons"}, {"statement", "scenario", "targets"}, "assumption")
        if _text(record["scenario"], "assumption.scenario") not in self.scenarios:
            raise AnnotationError("assumption.scenario must identify a declared scenario")
        self.types(subject, OEO.OEO_00000063, PROV.Entity)
        self.claim(subject, record)
        self.graph.add((subject, RDFS.comment, _literal(_text(record["statement"], "assumption.statement"))))
        scenario = self.scenarios[record["scenario"]]
        self.graph.add((subject, OBO.BFO_0000050, scenario))
        self.graph.add((scenario, OBO.BFO_0000051, subject))
        for selector in _list(record["targets"], "assumption.targets", nonempty=True):
            target = self.target(selector)
            if (target, RDF.type, OC.InputAssignment) not in self.graph:
                raise AnnotationError("An assumption target must be an input assignment, not a calculated result")
            self.graph.add((target, OC.implementsAssumption, subject))
        for reason in _list(record.get("reasons", []), "assumption.reasons"):
            rationale = self.record(reason, {"statement"}, {"statement"}, "reason")
            self.types(rationale, OBO.IAO_0000030, PROV.Entity)
            self.claim(rationale, reason)
            self.graph.add((rationale, RDFS.comment, _literal(_text(reason["statement"], "reason.statement"))))
            self.graph.add((subject, OC.hasRationale, rationale))

    def unit(self, record):
        subject = self.record(record, {"target", "unit_class", "label"}, {"target", "unit_class", "label", "evidence"}, "unit interpretation")
        target = self.target(record["target"])
        datum = self.graph.value(target, OC.hasDatum)
        if datum is None:
            raise AnnotationError("Unit interpretations require a selected numerical record or summary, not a whole series")
        unit_class = _uri(record["unit_class"], "unit_class")
        if unit_class not in SUPPORTED_UNITS:
            raise AnnotationError("Unsupported unit_class; the first version supports kW, MW, kWh, MWh and dimensionless ratio only")
        dimension, label = SUPPORTED_UNITS[unit_class]
        if record["label"] != label:
            raise AnnotationError(f"The supported unit class requires label {label!r}")
        actual_dimension = self.graph.value(target, OC.quantityDimension)
        if actual_dimension is None or str(actual_dimension) != dimension:
            raise AnnotationError(f"The supplied unit requires a recorded {dimension!r} quantity dimension")
        for existing in self.graph.objects(datum, OBO.IAO_0000136):
            if (existing, RDF.type, OEO.OEO_00000350) in self.graph:
                raise AnnotationError("This datum already has a quantity interpretation; reconcile it instead of adding another")
        self.types(subject, OEO.OEO_00000350, PROV.Entity)
        self.claim(subject, record, evidence_required=True)
        unit = self.annotation_iri(record["id"], "unit")
        self.types(unit, unit_class)
        self.graph.add((unit, RDFS.label, _literal(_text(record["label"], "unit.label"))))
        value = self.graph.value(datum, OC.reportedNumericValue)
        if value is None:
            raise AnnotationError("The selected datum has no reported numerical value")
        self.graph.add((subject, OEO.OEO_00140178, value))
        self.graph.add((subject, OEO.OEO_00040010, unit))
        self.graph.add((datum, OBO.IAO_0000136, subject))

    def dataset(self, record):
        self.record(record, {"title", "revision_uri", "family_uri", "previous_revision_uri", "targets", "preparation"}, {"title", "revision_uri", "targets", "evidence"}, "dataset")
        revision = self.external_uri(record["revision_uri"], "dataset.revision_uri")
        self.types(revision, PROV.Entity)
        self.claim(revision, record, evidence_required=True)
        self.graph.add((revision, DCTERMS.title, _literal(_text(record["title"], "dataset.title"))))
        for key, predicate in (("family_uri", PROV.specializationOf), ("previous_revision_uri", PROV.wasRevisionOf)):
            if key in record:
                other = self.external_uri(record[key], f"dataset.{key}")
                if other == revision:
                    raise AnnotationError("A dataset revision must differ from its family and previous revision")
                self.types(other, PROV.Entity)
                self.graph.add((revision, predicate, other))
        for selector in _list(record["targets"], "dataset.targets", nonempty=True):
            target = self.target(selector)
            if (target, RDF.type, OC.InputAssignment) not in self.graph:
                raise AnnotationError("Recorded dataset use must target an input assignment")
            self.graph.add((self.graph.value(target, OC.hasDatum), PROV.wasDerivedFrom, revision))
        self.graph.add((self.ctx.execution, PROV.used, revision))
        if "preparation" in record:
            preparation = record["preparation"]
            process = self.record(preparation, {"description", "inputs"}, {"description", "inputs"}, "dataset preparation")
            self.types(process, PROV.Activity, OBO.BFO_0000015)
            self.claim(process, preparation, activity=True)
            self.graph.add((process, RDFS.comment, _literal(_text(preparation["description"], "preparation.description"))))
            for ref in _list(preparation["inputs"], "preparation.inputs", nonempty=True):
                if ref not in self.sources:
                    raise AnnotationError(f"Unknown preparation input source {ref!r}")
                self.graph.add((process, PROV.used, self.sources[ref]))
            self.graph.add((revision, PROV.wasGeneratedBy, process))

    def physical(self, record):
        subject = self.record(record, {"component", "kind", "scope", "target_uri", "target_label"},
                              {"component", "kind", "scope", "target_uri", "target_label", "evidence"}, "physical correspondence")
        kind = _text(record["kind"], "physical correspondence.kind")
        if kind not in {"actual", "aggregate", "hypothetical"}:
            raise AnnotationError("physical correspondence.kind must be actual, aggregate or hypothetical")
        component = self.component(record["component"])
        target = self.external_uri(record["target_uri"], "physical correspondence.target_uri")
        if kind == "actual" and (target, RDF.type, OBO.IAO_0000030) in self.graph:
            raise AnnotationError("An actual material target cannot already be an information description")
        if kind != "actual" and ((target, RDF.type, OBO.BFO_0000040) in self.graph or (target, RDF.type, OEO.OEO_00000031) in self.graph):
            raise AnnotationError("An aggregate or hypothetical description cannot already be a material target")
        self.types(subject, OC.PhysicalCorrespondenceAssertion, OBO.IAO_0000030, PROV.Entity)
        self.claim(subject, record, evidence_required=True)
        self.types(target, OBO.BFO_0000040 if kind == "actual" else OBO.IAO_0000030)
        self.graph.add((target, RDFS.label, _literal(_text(record["target_label"], "target_label"))))
        for predicate, value in ((OC.forComponent, component), (OC.correspondenceTarget, target),
                                 (OC.correspondenceKind, Literal(kind)), (OC.correspondenceScope, _literal(_text(record["scope"], "scope")))):
            self.graph.add((subject, predicate, value))

    def correspondence(self, record):
        subject = self.record(record, {"source", "target", "reason"}, {"source", "target", "reason"}, "component correspondence")
        source, target = self.component(record["source"]), self.component(record["target"], external=True)
        if source == target:
            raise AnnotationError("Component correspondence requires two distinct component identifiers")
        self.types(subject, OC.ComponentCorrespondence, OBO.IAO_0000030, PROV.Entity)
        self.types(target, OEO.OEO_00000276)
        self.claim(subject, record)
        self.graph.add((subject, OC.sourceComponent, source))
        self.graph.add((subject, OC.targetComponent, target))
        self.graph.add((subject, RDFS.comment, _literal(_text(record["reason"], "correspondence.reason"))))


def add_annotations(ctx, annotations: dict | Path) -> None:
    """Add validated, attributed annotations to ``ctx.graph``.

    ``ctx`` provides graph, configuration, execution, nodes, components,
    iri(kind, *keys), and report. See examples/annotations/README.md for version 1.
    """
    source_bytes = None
    if isinstance(annotations, (str, Path)):
        try:
            source_bytes = Path(annotations).read_bytes()
            document = yaml.load(source_bytes.decode("utf-8"), Loader=_UniqueKeysLoader)
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            raise AnnotationError(f"Invalid annotation YAML: {exc}") from exc
    else:
        document = annotations
    mapper = _Annotations(ctx, document)
    mapper.build()
    source_digest = hashlib.sha256(source_bytes).hexdigest() if source_bytes is not None else mapper.digest
    revision = ctx.iri("annotation-revision", source_digest)
    mapper.types(revision, PROV.Entity)
    mapper.graph.add((revision, OC.contentSHA256, _literal(source_digest)))
    description = ("SHA-256 identifies the original UTF-8 YAML file bytes; parsed using annotation schema version 1."
                   if source_bytes is not None else
                   "SHA-256 identifies the canonical JSON bytes of in-memory annotations using schema version 1.")
    mapper.graph.add((revision, DCTERMS.description, _literal(description)))
    mapper.graph.add((revision, DCTERMS.identifier, _literal("CallioMapper annotation schema version 1")))
    mapper.graph.add((revision, OC.sourcePath, _literal(Path(annotations).name if source_bytes is not None else "in-memory annotations (canonical JSON)")))
    if hasattr(ctx, "export_activity"):
        mapper.graph.add((ctx.export_activity, PROV.used, revision))
    for triple in mapper.graph:
        ctx.graph.add(triple)
    ctx.report["annotations"] = mapper.counts
    ctx.report["annotation_sha256"] = mapper.digest
    ctx.report["annotation_digest_representation"] = "canonical parsed JSON, schema version 1"
