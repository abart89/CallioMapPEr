"""Small text-file helpers; readers do not import Calliope."""
from pathlib import Path
import yaml


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())


def serialize_nq(graph, path):
    graph.serialize(destination=str(path), format="nquads")
