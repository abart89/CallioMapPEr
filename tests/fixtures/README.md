# Test Fixtures

Calliope model fixtures used for reproducible testing.

## Fixture Sources

- `national_scale/` — Calliope's built-in national scale example. Primary test fixture for M1–M3.
- `urban_scale/` — Calliope's built-in urban scale example. Used for M4 integration validation.

## Adding Fixtures

Pre-solved `results.nc` files should be committed here so tests do not require a live
Calliope solve. Generate them once with:

```bash
calliope run --save_netcdf tests/fixtures/national_scale/results.nc national_scale
```

Do not commit large NetCDF files (>10MB) — store them in Git LFS or generate them in CI.
