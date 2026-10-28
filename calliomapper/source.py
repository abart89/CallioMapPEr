"""Read a solved Calliope CSV export without reconstructing the model."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from pathlib import Path

import yaml


class SourceError(ValueError):
    """The saved export cannot support the requested interpretation."""


SUPPORTED_VERSIONS = frozenset({"0.7.0.dev7", "0.7.0"})
FIXTURE_TESTED_VERSIONS = frozenset({"0.7.0", "0.7.0.dev7"})
DIMENSIONS = frozenset({"nodes", "techs", "carriers", "costs", "timesteps"})


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _hash_file(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def _boolean(value: str, filename: str) -> bool:
    if value.lower() not in {"true", "false"}:
        raise SourceError(f"{filename}: expected True or False, found {value!r}")
    return value.lower() == "true"


class SavedModel:
    """One fixed, successful export, including its recorded execution identity.

    Stable 0.7.0 uses its saved ``active`` array to identify components. Older
    0.7.0.dev7 exports use the carrier-indexed ``definition_matrix`` instead.
    ``version`` selects this format; ``recorded_version`` is only populated
    when runtime metadata explicitly records the initialisation version.
    Digests identify the saved representation; they do not prove that differently
    encoded files describe scientifically equivalent configurations.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        attrs_path = self.path / "attrs.yaml"
        if not attrs_path.is_file():
            raise SourceError(f"Missing saved Calliope metadata: {attrs_path}")
        self.files = {
            item.name: _hash_file(item)
            for item in sorted(self.path.iterdir())
            if item.is_file()
            and (item.name == "attrs.yaml" or re.fullmatch(r"(?:inputs|results)_.+\.csv", item.name))
        }
        try:
            self.attrs = yaml.safe_load(self._read_file("attrs.yaml"))
        except yaml.YAMLError as error:
            raise SourceError(f"Invalid attrs.yaml: {error}") from error
        if not isinstance(self.attrs, dict):
            raise SourceError("attrs.yaml must contain a mapping")
        for section in ("definition", "config", "math", "runtime"):
            if not isinstance(self.attrs.get(section), dict):
                raise SourceError(f"attrs.yaml is missing the {section!r} mapping")
        definition = self.attrs["definition"]
        for section in ("nodes", "techs"):
            values = definition.get(section)
            if not isinstance(values, dict) or not values:
                raise SourceError(f"attrs.yaml must record non-empty definition.{section}")
            if any(not isinstance(name, str) or not isinstance(value, dict) for name, value in values.items()):
                raise SourceError(f"definition.{section} must map names to saved definitions")
        self.nodes = definition["nodes"]
        self.techs = definition["techs"]
        runtime = self.attrs["runtime"]
        self.recorded_version = runtime.get("calliope_version_initialised")
        self.configured_version = self.attrs["config"].get("init", {}).get("calliope_version")
        if self.recorded_version:
            self.version = str(self.recorded_version)
            self.version_evidence = "runtime.calliope_version_initialised"
        elif self.configured_version:
            self.version = str(self.configured_version)
            self.version_evidence = "config.init.calliope_version (intended version; producing version not recorded)"
        elif ("inputs_active.csv" in self.files) != ("inputs_definition_matrix.csv" in self.files):
            self.version = "0.7.0" if "inputs_active.csv" in self.files else "0.7.0.dev7"
            self.version_evidence = "saved activation array layout (producing version not recorded)"
        else:
            raise SourceError("The saved export does not record a supported version or an unambiguous activation-array layout")
        if self.version not in SUPPORTED_VERSIONS:
            raise SourceError(f"Unsupported producing or configured Calliope version {self.version!r}; expected 0.7.0.dev7 or 0.7.0")
        self.activation_variable = "active" if self.version == "0.7.0" else "definition_matrix"
        self.activation_file = f"inputs_{self.activation_variable}.csv"
        if self.activation_file not in self.files:
            raise SourceError(f"Calliope {self.version} requires {self.activation_file}; a different version's layout cannot be inferred from the version label")
        self.status = str(runtime.get("termination_condition", ""))
        if self.status != "optimal":
            raise SourceError(f"Expected a successful 'optimal' execution, found {self.status!r}")
        if not any(name.startswith("inputs_") for name in self.files):
            raise SourceError("The saved export has no input CSV files")
        if not any(name.startswith("results_") for name in self.files):
            raise SourceError("The saved export has no result CSV files")
        self._rows: dict[tuple[str, str], list[dict[str, str]]] = {}
        self.configuration_digest = _digest({
            "attrs": {key: self.attrs[key] for key in ("definition", "config", "math")},
            "inputs": {name: checksum for name, checksum in self.files.items() if name.startswith("inputs_")},
        })
        timings = runtime.get("timings", {})
        start = timings.get("solve_start") if isinstance(timings, dict) else None
        end = timings.get("solve_complete", timings.get("solver_exit")) if isinstance(timings, dict) else None
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0 for value in (start, end)) or end < start:
            raise SourceError(
                "Execution identity needs recorded solve_start and solve_complete (or solver_exit) "
                "timestamps. Equal numerical results alone cannot identify a particular run."
            )
        self.execution_digest = _digest({
            "configuration": self.configuration_digest,
            "runtime": runtime,
            "results": {name: checksum for name, checksum in self.files.items() if name.startswith("results_")},
        })

    def file_hash(self, filename: str) -> str:
        """Return the checksum captured when the export was opened."""
        if filename not in self.files:
            raise SourceError(f"The saved export has no file {filename!r}")
        return self.files[filename]

    def _read_file(self, filename: str) -> str:
        contents = (self.path / filename).read_bytes()
        if hashlib.sha256(contents).hexdigest() != self.file_hash(filename):
            raise SourceError(f"{filename} changed while the export was being read; open the export again")
        try:
            return contents.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise SourceError(f"{filename} is not UTF-8 text") from error

    def rows(self, group: str, variable: str) -> list[dict[str, str]]:
        """Read coordinates and values, normalising scalar CSV header ``0``.

        Values remain strings, including missing/non-finite numerical values.
        The mapper decides whether a particular value can become a quantity.
        Unknown dimensions are rejected only for arrays actually requested.
        """
        if group not in {"inputs", "results"} or not re.fullmatch(r"[A-Za-z_]\w*", variable):
            raise SourceError(f"Invalid source selection: {group!r}, {variable!r}")
        key = (group, variable)
        if key not in self._rows:
            filename = f"{group}_{variable}.csv"
            self.file_hash(filename)
            reader = csv.reader(io.StringIO(self._read_file(filename)))
            header = next(reader, [])
            if header == ["0"]:
                header = [variable]
            if not header or header[-1] != variable or len(header) != len(set(header)):
                raise SourceError(f"{filename}: expected unique coordinate columns followed by {variable!r}")
            dimensions = header[:-1]
            unknown = set(dimensions) - DIMENSIONS
            if unknown:
                raise SourceError(f"{filename}: unsupported dimensions {sorted(unknown)}")
            result = []
            coordinates = set()
            for line, cells in enumerate(reader, start=2):
                if len(cells) != len(header):
                    raise SourceError(f"{filename}:{line}: expected {len(header)} columns, found {len(cells)}")
                coordinate = tuple(cells[:-1])
                if any(not item.strip() for item in coordinate):
                    raise SourceError(f"{filename}:{line}: a coordinate is missing")
                if coordinate in coordinates:
                    raise SourceError(f"{filename}:{line}: duplicate coordinates {coordinate}")
                coordinates.add(coordinate)
                row = dict(zip(header, cells))
                if "nodes" in row and row["nodes"] not in self.nodes:
                    raise SourceError(f"{filename}:{line}: unknown node {row['nodes']!r}")
                if "techs" in row and row["techs"] not in self.techs:
                    raise SourceError(f"{filename}:{line}: unknown technology {row['techs']!r}")
                result.append(row)
            if not dimensions and len(result) != 1:
                raise SourceError(f"{filename}: a scalar must have exactly one value")
            self._rows[key] = result
        return self._rows[key]

    def active_components(self) -> dict[tuple[str, str], dict]:
        """Read effective component structure from Calliope's saved arrays."""
        components = {}
        active_coordinates = set()
        activation_columns = {"nodes", "techs", self.activation_variable}
        if self.version == "0.7.0.dev7":
            activation_columns.add("carriers")
        for row in self.rows("inputs", self.activation_variable):
            if set(row) != activation_columns:
                raise SourceError(f"{self.activation_file} must have exactly these columns: {sorted(activation_columns)}")
            if _boolean(row[self.activation_variable], self.activation_file):
                if self.version == "0.7.0.dev7" and (self.nodes[row["nodes"]].get("active") is False or self.techs[row["techs"]].get("active") is False):
                    raise SourceError("The definition matrix activates a node or technology marked inactive in attrs.yaml")
                if self.version == "0.7.0.dev7":
                    active_coordinates.add((row["nodes"], row["techs"], row["carriers"]))
                components.setdefault((row["nodes"], row["techs"]), {"carrier_in": [], "carrier_out": []})
        bases = {}
        for row in self.rows("inputs", "base_tech"):
            if not {"techs", "base_tech"} <= row.keys() or set(row) - {"nodes", "techs", "base_tech"}:
                raise SourceError("inputs_base_tech.csv has unsupported coordinates")
            bases[(row.get("nodes"), row["techs"])] = row["base_tech"]
        for direction in ("carrier_in", "carrier_out"):
            for row in self.rows("inputs", direction):
                if set(row) != {"nodes", "techs", "carriers", direction}:
                    raise SourceError(f"inputs_{direction}.csv must have node, technology and carrier coordinates")
                if _boolean(row[direction], f"inputs_{direction}.csv"):
                    pair = (row["nodes"], row["techs"])
                    if self.version == "0.7.0.dev7" and (*pair, row["carriers"]) not in active_coordinates:
                        raise SourceError(f"inputs_{direction}.csv identifies an inactive component/carrier combination {(*pair, row['carriers'])}")
                    if pair not in components:
                        # Stable Calliope can retain carrier definitions for
                        # deactivated components (config.init.retain_inactive).
                        continue
                    components[pair][direction].append(row["carriers"])
        links = {}
        if self.version == "0.7.0" and any(value == "transmission" for value in bases.values()):
            for direction in ("link_from", "link_to"):
                for row in self.rows("inputs", direction):
                    if set(row) != {"techs", direction}:
                        raise SourceError(f"inputs_{direction}.csv must have technology coordinates")
                    links.setdefault(row["techs"], {})[direction] = row[direction]
        for (node, tech), component in components.items():
            base = bases.get((node, tech), bases.get((None, tech)))
            if not base:
                raise SourceError(f"No saved base technology for {(node, tech)}")
            component["base_tech"] = base
            component["carrier_in"].sort()
            component["carrier_out"].sort()
            if base == "transmission":
                definition = links.get(tech, {}) if self.version == "0.7.0" else self.techs[tech]
                origin, target = definition.get("link_from"), definition.get("link_to")
                if origin not in self.nodes or target not in self.nodes or origin == target or node not in {origin, target}:
                    raise SourceError(f"Invalid saved transmission endpoints for {(node, tech)}")
                if (origin, tech) not in components or (target, tech) not in components:
                    raise SourceError(f"Transmission {tech!r} is missing an active endpoint")
                component.update(link_from=origin, link_to=target, remote_node=target if node == origin else origin)
        return components

    @property
    def structure_files(self) -> tuple[str, ...]:
        """The saved arrays that establish active structure and carrier links."""
        filenames = (self.activation_file, "inputs_base_tech.csv", "inputs_carrier_in.csv", "inputs_carrier_out.csv")
        if self.version == "0.7.0":
            filenames += tuple(f"inputs_{name}.csv" for name in ("link_from", "link_to") if f"inputs_{name}.csv" in self.files)
        return filenames
