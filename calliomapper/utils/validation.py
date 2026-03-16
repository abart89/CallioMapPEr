"""
SHACL validation gate.

Wraps pyshacl to validate a produced rdflib.ConjunctiveGraph against a set of
SHACL shapes. Called by the Translator before any output is written or returned.
Raises ValidationError with the full SHACL report on failure — never silently
emits an invalid graph.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Dataset, Graph
import pyshacl


class ValidationError(Exception):
    """Raised when the produced graph fails SHACL validation."""


def validate(graph: Dataset, shapes_path: str | Path) -> None:
    """
    Validate *graph* against the SHACL shapes at *shapes_path*.

    Raises ValidationError if validation fails.
    Returns None on success.
    """
    shapes_graph = Graph().parse(str(shapes_path), format="turtle")
    try:
        conforms, _, report_text = pyshacl.validate(
            graph,
            shacl_graph=shapes_graph,
            inference="none",
            abort_on_first=False,
        )
    except RuntimeError as exc:
        # pyshacl raises RuntimeError when it encounters blank-node subjects
        # in a Dataset context (a known pyshacl limitation). Treat as failure.
        raise ValidationError(
            f"Graph failed SHACL validation against {shapes_path}: {exc}"
        ) from exc
    if not conforms:
        raise ValidationError(
            f"Graph failed SHACL validation against {shapes_path}:\n{report_text}"
        )
