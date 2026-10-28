# Saved Calliope examples and supplied tutorial context

The primary tutorials use stable **Calliope 0.7.0** examples solved with **GLPK 5.0**, under [calliope-0.7.0-glpk/](calliope-0.7.0-glpk/README.md). Their source files, saved results and preparation records accompany them. CallioMapper reads those saved files without needing a solver.

The earlier stable [HiGHS examples](calliope-0.7.0/README.md) remain unchanged as regression evidence. The [version comparison](../docs/calliope-version-comparison.md) describes those stable HiGHS runs and the older development-preview runs; it has not been relabelled as a GLPK comparison. The text below describes Andrea's preserved original examples.

The national and urban directories preserve the model and saved-output files already present in CallioMapPEr at commit `20ba5ea1c2f77f8cfd1249d0c27b0f9b26dfbdc7`. All 139 files still match the [recorded checksums](source-manifest.json). That manifest was created when the ontology project copied these examples on 13 October 2026. The package implementation has not changed their numerical results or rerun an optimisation.

Both configurations request Calliope 0.7.0, while both saved runtime records identify **0.7.0.dev7** and termination condition `optimal`. Preserve that distinction: a requested version is not evidence of the version that produced an output.

The models originate from the national and urban examples distributed with Calliope. The fixed upstream reference is v0.7.0.dev7, commit `2c8fc10db7abbd13014e591856dce6f9573ba2ab`. Calliope credits its contributors and uses Apache-2.0; its [unchanged licence](CALLIOPE-LICENSE-v0.7.0.dev7) accompanies these snapshots. The software citation is Pfenninger and Pickering (2018), *Calliope: a multi-scale energy systems modelling framework*, [doi:10.21105/joss.00825](https://doi.org/10.21105/joss.00825).

These are local saved examples, not a claim that every byte matches the upstream tag or that their numerical outputs were produced by the upstream authors. The preserved NetCDF archives are not read by this package version. Its primary inputs are the CSV results directories and their metadata.

The separate [annotations directory](annotations/README.md) contains additional tutorial context invented for the current demonstration, with evidence status recorded explicitly. It does not reconstruct the original authors' intentions. Test-only modified graphs and synthetic reruns remain temporary test artifacts and never overwrite these fixed inputs.
