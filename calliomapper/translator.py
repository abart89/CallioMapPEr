"""
Translator — main orchestration class.

Coordinates CoreMapper and EpistemicEngine
to produce a validated N-Quads knowledge graph.

Accepts file paths or in-memory objects so it works inside Jupyter notebooks
without requiring filesystem access in the mapper layer.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from rdflib import Dataset

from calliomapper.mapper.core import CoreMapper
from calliomapper.utils import io, validation


# Default shapes file used when no custom schema is supplied.
_DEFAULT_SHAPES = Path(__file__).parent.parent / "ontology" / "dummy_shapes.ttl"


class Translator:
    """
    Orchestrates the CallioMapper pipeline.

    Parameters
    ----------
    model_dir:
        Path to a Calliope model directory containing ``nodes.yaml`` and
        ``techs.yaml``.  Pass ``None`` to supply *nodes* / *techs* directly.
    nodes:
        Pre-loaded nodes dict (alternative to *model_dir*).
    techs:
        Pre-loaded techs dict (alternative to *model_dir*).
    extension:
        Path to an epistemic extension YAML, or pre-loaded dict (optional).
    shapes:
        Path to a SHACL shapes file.  Defaults to ``ontology/dummy_shapes.ttl``.
    run_id:
        Base URI for this model run.  Auto-generated UUID if not supplied.
    graph_id:
        Override for the named graph URI (the 4th element of every quad in the
        core graph).  Defaults to ``{run_id}/core``.
        Use to encode scenario, parameter sweep, model version, etc.:
        e.g. ``"https://w3id.org/ontocal/runs/my-model/scenario-high-renewables"``.
    """

    def __init__(
        self,
        model_dir: str | Path | None = None,
        *,
        nodes: dict | None = None,
        techs: dict | None = None,
        extension=None,
        shapes: str | Path | None = None,
        run_id: str | None = None,
        graph_id: str | None = None,
    ) -> None:
        self.run_id = run_id or f"https://w3id.org/ontocal/runs/{uuid.uuid4()}"
        self.graph_id = graph_id  # None → CoreMapper uses default
        self.shapes = Path(shapes) if shapes else _DEFAULT_SHAPES
        self._graph: Dataset | None = None

        # Load core inputs
        if model_dir is not None:
            model_dir = Path(model_dir)
            self._nodes = io.load_yaml(model_dir / "nodes.yaml")
            self._techs = io.load_yaml(model_dir / "techs.yaml")
        else:
            self._nodes = nodes or {}
            self._techs = techs or {}

        # Extension placeholder
        self._extension = extension

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def translate(self) -> Dataset:
        """
        Run the full pipeline and return a validated ConjunctiveGraph/Dataset.

        Raises
        ------
        calliomapper.utils.validation.ValidationError
            If the produced graph fails SHACL validation.
        """
        cg = Dataset()

        # Core graph
        core_graph = CoreMapper(self.run_id, graph_id=self.graph_id).map(
            nodes=self._nodes,
            techs=self._techs,
        )
        cg.add_graph(core_graph)

        # Extension — not yet implemented; placeholder for EpistemicEngine

        validation.validate(cg, self.shapes)

        self._graph = cg
        return cg

    def save(self, path: str | Path) -> None:
        """
        Serialize the translated graph to an N-Quads (.nq) file.

        Calls ``translate()`` automatically if not already called.
        """
        if self._graph is None:
            self.translate()
        io.serialize_nq(self._graph, path)
