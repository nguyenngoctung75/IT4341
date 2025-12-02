from dataclasses import dataclass

@dataclass
class CandidateLocation:
    id: int
    name: str  # Placeholder for address or description
    rent_cost: float
    setup_cost: float # Derived or estimated
    traffic: int
    area: float
    competitors_count: int
    population_density: float
    avg_income: float

    # Calculated metrics
    expected_revenue: float = 0.0
    expected_cost: float = 0.0
    score: float = 0.0

@dataclass
class OptimizationResult:
    selected_locations: list[CandidateLocation]
    total_profit: float
    total_cost: float
