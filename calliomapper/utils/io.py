"""
I/O utilities — the ONLY layer in calliomapper allowed to touch the filesystem.

All mapper classes receive already-loaded Python objects (dicts, xarray Datasets,
rdflib graphs). File loading and serialization are handled exclusively here.
"""

from __future__ import annotations

from pathlib import Path

import yaml
import xarray as xr
from rdflib import Dataset


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_netcdf(path: str | Path) -> xr.Dataset:
    """Load a NetCDF results file as an xarray Dataset."""
    return xr.open_dataset(path)


def serialize_nq(graph: Dataset, path: str | Path) -> None:
    """Serialize a ConjunctiveGraph to an N-Quads (.nq) file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=str(path), format="nquads")
