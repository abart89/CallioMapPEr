"""
CoreMapper — Core mapping layer.

Accepts pre-loaded Calliope model data (nodes dict, techs dict, results data) and maps
each entity to RDF triples using the generated Pydantic classes natively.
Because this operates entirely post-solve, inputs and outputs are handled uniformly
as solved properties of the graph.

Returns an rdflib.Graph tagged with the core named graph URI.
By default this is ``<{run_id}/core>``; the caller may override it
via ``graph_id`` to encode scenario, version, or any other context.

No filesystem I/O here. All inputs are already-loaded Python objects.
"""

from __future__ import annotations

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS

from calliomapper.ontology.namespaces import ONTOCAL
from calliomapper.generated.ontocal_core import (
    CalliopeNetworkNode,
    CalliopeTechnology,
    CalliopeSupplyTechnology,
    CalliopeDemandTechnology,
    CalliopeStorageTechnology,
    CalliopeTransmissionTechnology,
    CalliopeConversionTechnology,
)


_GRAPH_SUFFIX = "/core"


class CoreMapper:
    """
    Maps Calliope solved properties (nodes, technologies, and results) to RDF triples.

    Parameters
    ----------
    run_id:
        Base URI for this model run (e.g. ``"https://w3id.org/ontocal/runs/my-run-001"``).
        Used to mint entity URIs and, unless *graph_id* is given, the named graph URI.
    graph_id:
        Override for the named graph URI (the 4th element of each quad).
        Defaults to ``{run_id}/core``.
        Use this to encode scenario, model version, parameter sweep, etc.:
        e.g. ``"https://w3id.org/ontocal/runs/my-run-001/scenario-high-renewables"``.
    """

    def __init__(self, run_id: str, graph_id: str | None = None) -> None:
        self.run_id = run_id
        self.graph_uri = URIRef(graph_id if graph_id is not None else run_id + _GRAPH_SUFFIX)

    def map(
        self,
        nodes: dict | None = None,
        techs: dict | None = None,
    ) -> Graph:
        """
        Build and return the core named graph.

        Parameters
        ----------
        nodes:
            Dict of ``{node_name: node_config}`` as parsed from ``nodes.yaml``.
        techs:
            Dict of ``{tech_name: tech_config}`` as parsed from ``techs.yaml``.

        Returns
        -------
        rdflib.Graph
            An rdflib Graph whose identifier is the named graph URI
            (``<{run_id}/core>`` by default, or the value of *graph_id*).
        """
        g = Graph(identifier=self.graph_uri)

        for name, config in (nodes or {}).items():
            self._add_node(g, name, config)

        for name, config in (techs or {}).items():
            self._add_tech(g, name, config)

        return g

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _entity_uri(self, name: str) -> URIRef:
        """Mint a URI for a Calliope entity within the run namespace."""
        return URIRef(self.run_id + "/" + name)

    def _add_node(self, g: Graph, name: str, config: dict) -> None:
        """
        Validate the node via the generated Pydantic class, then add
        rdf:type and rdfs:label triples to the graph.
        """
        uri = self._entity_uri(name)
        label = (config or {}).get("name", name)

        # Filter kwargs to only those defined in Pydantic schema
        kwargs = {k: v for k, v in (config or {}).items() if k in CalliopeNetworkNode.model_fields}
        kwargs.setdefault("name", label)

        # Validate via generated Pydantic class — raises ValidationError if invalid.
        CalliopeNetworkNode(**kwargs)

        g.add((uri, RDF.type, ONTOCAL.CalliopeNetworkNode))
        g.add((uri, ONTOCAL.name, Literal(label)))

    def _add_tech(self, g: Graph, name: str, config: dict) -> None:
        """
        Validate the tech via the generated Pydantic class based on base_tech,
        then add rdf:type and rdfs:label triples.
        """
        uri = self._entity_uri(name)
        label = (config or {}).get("name", name)
        base_tech = (config or {}).get("base_tech")

        tech_classes = {
            "supply": (CalliopeSupplyTechnology, ONTOCAL.CalliopeSupplyTechnology),
            "demand": (CalliopeDemandTechnology, ONTOCAL.CalliopeDemandTechnology),
            "storage": (CalliopeStorageTechnology, ONTOCAL.CalliopeStorageTechnology),
            "transmission": (CalliopeTransmissionTechnology, ONTOCAL.CalliopeTransmissionTechnology),
            "conversion": (CalliopeConversionTechnology, ONTOCAL.CalliopeConversionTechnology),
        }

        PydanticClass, rdf_type = tech_classes.get(base_tech, (CalliopeTechnology, ONTOCAL.CalliopeTechnology))

        kwargs = {k: v for k, v in (config or {}).items() if k in PydanticClass.model_fields}
        kwargs.setdefault("name", label)

        # Validate via generated Pydantic class — raises ValidationError if invalid.
        PydanticClass(**kwargs)

        g.add((uri, RDF.type, rdf_type))
        g.add((uri, ONTOCAL.name, Literal(label)))
