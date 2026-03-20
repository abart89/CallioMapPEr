# Running Models in Different Modes (Tutorial)

Source: https://calliope.readthedocs.io/en/v0.7.0.dev7/examples/modes/

This page documents how to execute Calliope models using three distinct operational modes: base, operate, and spores.

## Running in 'base' mode

The base mode performs a full optimization to determine the optimal system design and operation. This mode designs new infrastructure and schedules operations across the entire time horizon simultaneously, making it suitable for long-term strategic planning scenarios.

## Running in 'operate' mode

Operating mode uses fixed infrastructure from a previous base mode run and optimizes only the operational decisions (dispatch). This approach is valuable for analyzing how an already-designed system performs under different operational constraints or demand scenarios without redesigning infrastructure.

## Running in 'spores' mode

SPORES (Spatially-explicit Pareto Optimal Renewable Energy Solutions) generates multiple diverse solutions that represent different trade-offs in the solution space. Rather than finding a single optimal solution, this mode explores the range of feasible alternatives, each optimized under different scoring criteria. This is particularly useful for understanding solution diversity and robust design choices.

## Visualising results

Results from any mode can be visualized and compared. The documentation includes guidance on interpreting outputs through different scoring algorithms.

### Using different scoring algorithms

Various scoring methods can be applied to evaluate and rank solutions across different objectives, allowing stakeholders to understand performance across multiple dimensions simultaneously.

## Comparative Analysis

**'base' vs 'operate'**: Base mode optimizes complete system design plus operation, while operate mode fixes the infrastructure and optimizes only dispatch.

**'base' vs 'spores'**: Base mode identifies one optimal solution; spores mode explores multiple diverse alternatives across the Pareto frontier.

**Comparing 'spores' scoring algorithms**: Different scoring approaches reveal how solution preferences shift based on optimization criteria.
