"""
Canned Queries module.

Abstracts raw SPARQL logic away from the user, returning easy-to-use
Pandas DataFrames for common tasks like identifying system costs or
installed capacities.
"""

from __future__ import annotations

import pandas as pd
from rdflib import Dataset

def get_installed_capacity(graph: Dataset, technology_type: str | None = None) -> pd.DataFrame:
    """
    Given a combined CallioMapper dataset, run a prepared SPARQL query to find all
    technologies and their installed capacities.
    
    Returns a Pandas DataFrame.
    """
    # TODO: Implement actual SPARQL mapping to generic OEO/SOSA capacity queries.
    return pd.DataFrame(columns=["node", "technology", "carrier", "capacity", "unit"])

def get_system_costs(graph: Dataset) -> pd.DataFrame:
    """
    Extract system costs (capex, opex) from the graph as a Pandas DataFrame.
    """
    # TODO: Implement actual SPARQL mapping to costs.
    return pd.DataFrame(columns=["node", "technology", "cost_type", "value", "unit"])
