#!/usr/bin/env python3
"""Regenerate genuine Calliope 0.7.0 examples in a new directory.

This optional development command solves the two upstream examples once. It is
not imported by CallioMapper and is never run by its routine tests or exports.
These examples use GLPK through Calliope's Pyomo backend.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata, resources
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
from tempfile import TemporaryDirectory


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(destination: Path) -> None:
    import calliope
    from pyomo.environ import SolverFactory

    if calliope.__version__ != "0.7.0":
        raise RuntimeError("This preparation script requires Calliope 0.7.0 exactly.")
    glpk = SolverFactory("glpk")
    if not glpk.available(exception_flag=False):
        raise RuntimeError("GLPK requires the glpsol executable on PATH.")
    executable = Path(glpk.executable())
    solver_version = ".".join(str(value) for value in glpk.version()[:2])
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(
            f"Destination already exists: {destination}. Choose a new directory."
        )
    destination.mkdir(parents=True)
    calliope_root = Path(str(resources.files("calliope")))
    distribution = metadata.distribution("calliope")
    license_path = next(
        distribution.locate_file(item)
        for item in distribution.files or []
        if str(item).endswith(".dist-info/licenses/LICENSE")
    )
    shutil.copy2(license_path, destination / "CALLIOPE-LICENSE")
    versions = {
        item.metadata["Name"]: item.version
        for item in metadata.distributions()
        if item.metadata.get("Name")
    }
    (destination / "preparation-requirements.txt").write_text(
        "".join(f"{name}=={version}\n" for name, version in sorted(versions.items())),
        encoding="utf-8",
    )
    manifest = {
        "calliope_version": calliope.__version__,
        "source_release": "https://github.com/calliope-project/calliope/releases/tag/v0.7.0",
        "source_distribution": "https://pypi.org/project/calliope/0.7.0/",
        "source_attribution": "Calliope contributors; Apache License 2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "pyomo_version": metadata.version("pyomo"),
        "platform": platform.platform(),
        "solver": "GLPK",
        "solver_version": solver_version,
        "solver_executable_sha256": sha256(executable),
        "solver_version_output": subprocess.run(
            [str(executable), "--version"], check=True, text=True,
            capture_output=True,
        ).stdout.strip(),
        "backend": "pyomo",
        "configuration_changes": {
            "build.backend": "pyomo",
            "solve.solver": "glpk",
            "solve.save_logs": "solver-logs",
        },
        "execution_description": (
            "Actual local optimisations of the unchanged built-in example source "
            "files from the Calliope 0.7.0 distribution, with the recorded backend "
            "and solver choices. The existing source time subsets are retained."
        ),
        "examples": {},
    }
    for name in ("national_scale", "urban_scale"):
        print(f"Preparing {name}", flush=True)
        upstream = calliope_root / "example_models" / name
        example = destination / name
        source = example / "source"
        shutil.copytree(upstream, source)
        source_hashes = {
            str(path.relative_to(source)): sha256(path)
            for path in sorted(source.rglob("*"))
            if path.is_file()
        }
        for relative, digest in source_hashes.items():
            if sha256(upstream / relative) != digest:
                raise RuntimeError(f"Source copy differs from upstream: {relative}")
        # A temporary working directory keeps solver temporary-file paths out of
        # the personal checkout. The saved configuration retains a relative path.
        with TemporaryDirectory(prefix="calliomapper-solver-") as working:
            previous_directory = Path.cwd()
            try:
                os.chdir(working)
                model = calliope.read_yaml(source / "model.yaml")
                model.build(backend="pyomo")
                model.solve(solver="glpk", save_logs="solver-logs")
            finally:
                os.chdir(previous_directory)
            shutil.copytree(Path(working) / "solver-logs", example / "solver-logs")
        termination = model.results.attrs.get("termination_condition")
        if termination is None:
            termination = model.runtime.termination_condition
        if termination != "optimal":
            raise RuntimeError(f"{name} did not solve optimally: {termination}")
        model.to_csv(example / "results_directory")
        manifest["examples"][name] = {
            "termination_condition": termination,
            "source_files_sha256": source_hashes,
            "result_files_sha256": {
                str(path.relative_to(example / "results_directory")): sha256(path)
                for path in sorted((example / "results_directory").iterdir())
                if path.is_file()
            },
            "solver_files_sha256": {
                path.name: sha256(path)
                for path in sorted((example / "solver-logs").iterdir())
                if path.is_file()
            },
            "runtime": model.runtime.model_dump(mode="json"),
            "dimensions": dict(model.inputs.sizes),
        }
        (destination / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"Saved {name}: {termination}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    prepare(parser.parse_args().destination)
