"""Validate asserted data with the fixed, packaged OntoCal application profile."""
from importlib.resources import files
import pyshacl
from rdflib import Dataset, Graph


class ValidationError(ValueError):
    """The generated data does not conform to the selected SHACL profile."""


def validate(graph, shapes_path=None):
    resources = files("calliomapper").joinpath("resources")
    shapes = Graph()
    if shapes_path is not None:
        shapes.parse(str(shapes_path), format="turtle")
    else:
        for name in ("capacity", "technology", "time-series", "context"):
            shapes.parse(data=resources.joinpath(f"shapes/{name}.shacl.ttl").read_text(), format="turtle")
    ontology = Graph().parse(data=resources.joinpath("ontocal.ttl").read_text(), format="turtle")
    data = Graph()
    if isinstance(graph, Dataset):
        for s, p, o, _ in graph.quads():
            data.add((s, p, o))
    else:
        data += graph
    conforms, _, report = pyshacl.validate(data, shacl_graph=shapes, ont_graph=ontology, inference="none", do_owl_imports=False)
    if not conforms:
        raise ValidationError(str(report))
    return str(report)
