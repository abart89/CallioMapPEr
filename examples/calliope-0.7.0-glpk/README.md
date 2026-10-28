# Calliope 0.7.0 examples solved with GLPK

These are genuine saved executions of the national-scale and urban-scale
examples distributed with **Calliope 0.7.0**. They use **GLPK 5.0** through
Calliope's **Pyomo backend**, with Pyomo **6.10.1**. Both solver logs and saved
runtime records report optimal termination. GLPK is the chosen solver for
preparing this project's current examples; ordinary CallioMapper translation
and tests only read these saved files and require no solver.

The choice reflects this project's preference. Calliope's current guidance says
that HiGHS is installed automatically and recommends CBC when additional
features such as piecewise linear constraints are needed. It also supports
GLPK and explains that it can require more time or memory for larger models.
This project does not describe GLPK as Calliope's general recommendation.
See the [official solver guidance](https://calliope.readthedocs.io/en/stable/installation/#choosing-a-solver).

## Files and provenance

Each model directory contains:

- `source/`: the complete example YAML files and data tables, copied unchanged
  from the installed Calliope 0.7.0 distribution.
- `results_directory/`: all effective input and numerical result CSV files and
  `attrs.yaml`, written by Calliope after solving.
- `solver-logs/`: the saved GLPK log, mathematical problem and solver solution
  files from that execution.

The [manifest](manifest.json) records source and result checksums, executable
and package versions, backend, time coverage and runtime metadata. It contains
69 saved files for the national model and 64 for the urban model, including
each `attrs.yaml`. Both models retain the upstream time subsets: 120 hourly
timesteps in the national model and 48 in the urban model. The preparation
changes the solver to GLPK and saves solver logs; it retains the upstream
scenario, parameter values and mathematics, including the urban additional
mathematics.

The actual preparation environment is listed in
[preparation-requirements.txt](preparation-requirements.txt). This records the
Python packages used on macOS, including platform-specific packages; it is not
a portable list of CallioMapper runtime dependencies. HiGHS appears because
Calliope installs it, but these executions explicitly selected GLPK. The
[solver build record](solver-build.json) identifies the official GNU source
archive, its checksum, the compiler and the local GLPK executable's checksum.
GLPK was built into a temporary directory, without changing a global software
installation. No GLPK executable or library is distributed here.

The source examples are attributed to the Calliope contributors and retain
their [Apache 2.0 license](CALLIOPE-LICENSE). The supplied
[annotation example](annotations/national.yaml) is fictional tutorial context,
not a reconstruction of the original authors' intentions. Its unit
interpretations cite source comments separately.

## Relationship to the earlier saved examples

The original developer-preview examples and the first stable examples solved
with HiGHS remain separate and unchanged. These GLPK results are new executions;
they are not earlier results with a different solver label.

Compared with the HiGHS stable examples, all 15 copied source files and all
39 saved input CSV files for each model are byte-for-byte identical. The parsed
model definitions and saved mathematical definitions also match. The backend,
solver, execution times and solver-log locations differ. No additional solver
options were supplied.

The numerical results nevertheless differ. The national objective is
`277048.7909848666`, compared with `277048.4786392079` in the earlier HiGHS run.
The urban objective is `842.4825384264784`, compared with
`842.337196706969`. Some dispatch and link-capacity results differ as well.
For example, the saved cost for `N1 / N1_to_X2` is
`0.08229885598265695`, compared with `0.051678895602049` in the HiGHS run.
Both solvers reported optimal termination, but these observations do not
establish an identical optimum or interchangeable numerical answers. The
backend and solver changed together; this comparison does not isolate the
numerical cause. Tests of these examples use values from the GLPK files.

The GLPK logs report small primal infeasibilities at termination
(`7.515 × 10⁻¹⁰` for national and `2.834 × 10⁻¹³` for urban). These are linear
programmes, so no mixed-integer optimality gap is reported. The saved log,
problem and solution files allow separate numerical review if needed.

## Optional preparation of new examples

CallioMapper users do not need to perform this step. To create another pair of
saved executions, prepare a separate Calliope environment containing GLPK.
For example, using the installation approach described in the Calliope guide:

```sh
conda create -n calliomapper-example-preparation -c conda-forge python=3.13 calliope=0.7.0 glpk=5.0
conda activate calliomapper-example-preparation
glpsol --version
python scripts/prepare_stable_examples.py /path/to/a/new/example-directory
```

Run the last command from the CallioMapper repository root. The script requires
Calliope 0.7.0 and a `glpsol` executable on `PATH`. It uses Pyomo with GLPK,
checks for optimal termination and writes the saved exports and a new manifest.
The destination must not already exist. New executions have different times
and identifiers; numerical library versions can also affect their results.

The recorded installation instead used the existing isolated Python preparation
environment and compiled GLPK from its official source. The build procedure is
recorded in `solver-build.json`; using a packaged GLPK installation is also
supported by the preparation script.

The saved configuration uses the relative log path `solver-logs`. Solver logs
retain paths to the temporary execution files as execution evidence, rather
than embedding a personal checkout path. No example source or numerical result
was edited after the export.
