"""Represent saved model structure and recorded execution metadata."""

from datetime import datetime, timezone
import uuid
from rdflib import Graph, Literal, RDF, RDFS, XSD
from calliomapper.identity import entity_iri
from calliomapper.vocabulary import OC, OEO, OBO, PROV, DCT, PACKAGE_VERSION


def text(value):
    return Literal(str(value), datatype=XSD.string)


class MappingContext:
    def __init__(self, source, namespace):
        self.source, self.namespace = source, namespace
        self.graph = Graph()
        for prefix, vocabulary in (("oc", OC), ("oeo", OEO), ("obo", OBO), ("prov", PROV)):
            self.graph.bind(prefix, vocabulary)
        self.model = self.iri("model", source.configuration_digest)
        self.configuration = self.iri("configuration", source.configuration_digest)
        self.execution = self.iri("execution", source.execution_digest)
        self.export_activity = self.iri("graph-generation", str(uuid.uuid4()))
        self.nodes, self.components = {}, {}
        self.report = {"omissions": []}

    def iri(self, kind, *keys):
        return entity_iri(self.namespace, kind, *map(str, keys))

    def types(self, entity, *classes):
        for cls in classes:
            self.graph.add((entity, RDF.type, cls))

    def revision(self, filename):
        checksum = self.source.file_hash(filename)
        artifact = self.iri("source-file", filename)
        revision = self.iri("source-revision", filename, checksum)
        self.types(artifact, PROV.Entity)
        self.types(revision, PROV.Entity)
        self.graph.add((revision, PROV.specializationOf, artifact))
        self.graph.add((revision, OC.contentSHA256, text(checksum)))
        self.graph.add((revision, OC.sourcePath, text(filename)))
        self.graph.add((self.export_activity, PROV.used, revision))
        return revision


def add_structure(ctx):
    graph, source = ctx.graph, ctx.source
    metadata = ctx.revision("attrs.yaml")
    ctx.types(ctx.model, OEO.OEO_00000274, OEO.OEO_00000314, OBO.IAO_0000030, PROV.Entity)
    ctx.types(ctx.configuration, OC.ConfigurationSpecification, OBO.IAO_0000030, PROV.Entity)
    model_name = source.attrs["config"].get("init", {}).get("name")
    if model_name:
        graph.add((ctx.model, RDFS.label, text(model_name)))
    graph.add((ctx.configuration, OBO.IAO_0000136, ctx.model))
    graph.add((ctx.configuration, OC.sourceRevision, metadata))
    graph.add((ctx.configuration, OC.sourceLocator, text("definition, config, math and saved inputs_*.csv arrays")))
    ctx.types(ctx.execution, OEO.OEO_00000313, OEO.OEO_00000275, OBO.BFO_0000015, PROV.Activity)
    graph.add((ctx.execution, OC.usesConfiguration, ctx.configuration))
    graph.add((ctx.execution, PROV.used, ctx.configuration))
    graph.add((ctx.execution, OBO.RO_0000057, ctx.model))
    graph.add((ctx.execution, OC.executionStatus, Literal("solved")))
    execution_description = ctx.iri("execution-description", source.execution_digest)
    ctx.types(execution_description, OBO.IAO_0000030, PROV.Entity)
    graph.add((execution_description, OBO.IAO_0000136, ctx.execution))
    graph.add((execution_description, OC.sourceRevision, metadata))
    graph.add((execution_description, OC.sourceLocator, text("runtime")))
    configured_solver = source.attrs["config"].get("solve", {}).get("solver")
    if configured_solver:
        graph.add((ctx.configuration, DCT.description, text(f"Configured solver: {configured_solver}. The saved configuration does not identify its executable version.")))
    source_scenario = source.attrs["runtime"].get("scenario")
    if source_scenario is not None:
        graph.add((execution_description, DCT.description, text(f"Saved Calliope scenario selector: {source_scenario}. This label alone does not establish an OEO future scenario.")))
    timings = source.attrs["runtime"]["timings"]
    for key, predicate in (("solve_start", PROV.startedAtTime), ("solve_complete", PROV.endedAtTime)):
        if key in timings:
            graph.add((ctx.execution, predicate, Literal(datetime.fromtimestamp(timings[key], timezone.utc), datatype=XSD.dateTime)))
    software = ctx.iri("software", "Calliope", source.recorded_version or "version-not-recorded")
    ctx.types(software, PROV.SoftwareAgent, PROV.Agent)
    graph.add((software, RDFS.label, text(f"Calliope {source.recorded_version}" if source.recorded_version else "Calliope (producing version not recorded in saved export)")))
    if not source.recorded_version:
        graph.add((execution_description, DCT.description, text(f"Read using the Calliope {source.version} saved-array format, identified by {source.version_evidence}. This does not establish the actual executable version.")))
    graph.add((ctx.execution, PROV.wasAssociatedWith, software))
    ctx.types(ctx.export_activity, PROV.Activity, OBO.BFO_0000015)
    graph.add((ctx.export_activity, PROV.startedAtTime, Literal(datetime.now(timezone.utc), datatype=XSD.dateTime)))
    mapper = ctx.iri("software", "CallioMapper", PACKAGE_VERSION)
    ctx.types(mapper, PROV.SoftwareAgent, PROV.Agent)
    graph.add((mapper, RDFS.label, text(f"CallioMapper {PACKAGE_VERSION}")))
    graph.add((ctx.export_activity, PROV.wasAssociatedWith, mapper))

    active = source.active_components()
    for name in sorted({node for node, _ in active}):
        node = ctx.iri("node", source.configuration_digest, name)
        ctx.nodes[name] = node
        ctx.types(node, OC.CalliopeNetworkNode, OEO.OEO_00000276, OBO.IAO_0000030, PROV.Entity)
        graph.add((node, OC.sourceKey, text(name)))
        graph.add((node, RDFS.label, text(name)))
        graph.add((node, OC.inConfiguration, ctx.configuration))
        graph.add((node, OBO.BFO_0000050, ctx.model))
        graph.add((node, OC.sourceRevision, metadata))
    base_classes = {
        "supply": OC.CalliopeSupplyTechnology, "demand": OC.CalliopeDemandTechnology,
        "storage": OC.CalliopeStorageTechnology, "conversion": OC.CalliopeConversionTechnology,
        "transmission": OC.CalliopeTransmissionTechnology,
    }
    for (node_name, tech_name), effective in active.items():
        component = ctx.iri("technology", source.configuration_digest, node_name, tech_name)
        ctx.components[node_name, tech_name] = component
        ctx.types(component, OC.CalliopeTechnology, OEO.OEO_00000276, OBO.IAO_0000030, PROV.Entity)
        base = effective["base_tech"]
        if base in base_classes:
            ctx.types(component, base_classes[base])
        else:
            ctx.report["omissions"].append({"technology": tech_name, "reason": f"No specialised OntoCal class for base_tech {base}; retained as CalliopeTechnology."})
        graph.add((component, OC.sourceKey, text(tech_name)))
        graph.add((component, RDFS.label, text(f"{tech_name} at {node_name}")))
        graph.add((component, OC.atNode, ctx.nodes[node_name]))
        graph.add((component, OC.inConfiguration, ctx.configuration))
        graph.add((component, OBO.BFO_0000050, ctx.model))
        for filename in source.structure_files:
            graph.add((component, OC.sourceRevision, ctx.revision(filename)))
        for direction, predicate in (("carrier_in", OC.carrierIn), ("carrier_out", OC.carrierOut)):
            for carrier in effective[direction]:
                graph.add((component, predicate, text(carrier)))
        if base == "transmission":
            graph.add((component, OC.remoteNode, ctx.nodes[effective["remote_node"]]))
        definition = ctx.iri("technology-definition", source.configuration_digest, tech_name)
        ctx.types(definition, OBO.IAO_0000030, PROV.Entity)
        graph.add((definition, OC.sourceKey, text(tech_name)))
        graph.add((definition, OC.sourceRevision, metadata))
        graph.add((definition, OC.sourceLocator, text(f"definition.techs.{tech_name}")))
        graph.add((component, PROV.wasDerivedFrom, definition))
    filename = "inputs_timestep_resolution.csv"
    if filename in source.files:
        rows = source.rows("inputs", "timestep_resolution")
        if rows:
            description = ctx.iri("temporal-description", source.configuration_digest)
            ctx.types(description, OEO.OEO_00000119, OBO.IAO_0000030, PROV.Entity)
            graph.add((ctx.configuration, OC.hasTemporalDescription, description))
            graph.add((description, OC.sourceRevision, ctx.revision(filename)))
            if "inputs_timestep_weights.csv" in source.files:
                graph.add((description, OC.sourceRevision, ctx.revision("inputs_timestep_weights.csv")))
            graph.add((description, OC.firstIndexLabel, text(rows[0]["timesteps"])))
            graph.add((description, OC.lastIndexLabel, text(rows[-1]["timesteps"])))
            graph.add((description, OC.indexCount, Literal(len(rows), datatype=XSD.integer)))
            graph.add((description, DCT.description, text(f"Saved coordinate labels {rows[0]['timesteps']} to {rows[-1]['timesteps']}; {len(rows)} entries. These are modelled times, not execution dates. Interval boundaries and timezone are not asserted.")))
    ctx.report.update({"nodes": len(ctx.nodes), "components": len(ctx.components)})
