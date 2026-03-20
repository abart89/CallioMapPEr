# Shadow Prices

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/advanced/shadow_prices/

## Overview

In linear optimization problems, you can retrieve shadow prices (dual variables) for constraints from the Pyomo backend. This feature is valuable for analyzing economic impacts and linking with other models.

To enable shadow price tracking, specify constraints in your `solve` configuration:

```yaml
config:
  solve:
    shadow_prices: ["system_balance", ...]
```

Available constraint names are listed in the "Subject to" section of the base math documentation. Custom constraints defined in user-defined math can also be referenced.

## Important Limitations

- **Solver support varies**: Gurobi and GLPK support shadow prices; CBC does not
- **Incompatible with integer variables**: Models containing integer or binary variables cannot access shadow prices
- **Check status**: Use `model.backend.shadow_prices.is_active` to verify tracking status

## Command-Line Usage

When using the CLI tool, shadow prices specified in YAML configuration are automatically tracked and included in results with a `shadow_price_` prefix. For example, specifying `system_balance` produces `shadow_price_system_balance` in the saved results.

## Python Usage

In Python, you have two approaches:

**Method 1 - Manual activation:**
```python
model = calliope.examples.national_scale()
model.build()
model.backend.shadow_prices.activate()
model.solve()
balance_price = model.backend.shadow_prices.get("system_balance").to_series()
```

**Method 2 - Via solve parameters:**
```python
model = calliope.examples.national_scale()
model.build()
model.solve(shadow_prices=["system_balance"])
balance_price = model.results.shadow_price_system_balance.to_series()
```

Note: Manual activation can be memory-intensive with the Pyomo backend.
