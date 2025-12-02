import sys
from database import Database
from models import CandidateLocation
from optimizer import StoreOptimizer

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'convenience_store_db',
    'user': 'root',
    'password': 'password'
}

# Optimization Parameters
BUDGET = 5000.0 # Million VND
MAX_STORES = 5
MIN_DISTANCE_M = 1000.0 # Meters

def fetch_candidates(db):
    # Join tables to get full view of candidates
    query = """
    SELECT
        p.id, p.annual_rent, p.monthly_transport_cost, p.daily_traffic, p.frontage_width, p.area_sqm,
        lf.monthly_staff_cost, lf.monthly_manager_cost, lf.monthly_utility_cost,
        d.population_density, d.avg_income
    FROM premises p
    LEFT JOIN location_factors lf ON p.id = lf.premise_id
    LEFT JOIN demographics d ON p.id = d.premise_id
    WHERE p.is_rented = FALSE
    """
    rows = db.fetch_all(query)
    candidates = []
    for row in rows:
        # Simple Revenue Estimation Model (Mock Logic)
        # Revenue ~ Traffic * ConversionRate * AvgBasket * 365
        # ConversionRate ~ 0.05, AvgBasket ~ 0.05 (50k VND)
        traffic = row['daily_traffic']
        revenue = traffic * 0.05 * 0.05 * 365

        # Cost Estimation
        # Rent + Staff + Utilities + Transport
        annual_rent = row['annual_rent']
        monthly_ops = (row['monthly_staff_cost'] or 0) + (row['monthly_manager_cost'] or 0) + (row['monthly_utility_cost'] or 0) + (row['monthly_transport_cost'] or 0)
        annual_ops = monthly_ops * 12
        setup_cost = 500 # Fixed setup cost assumption

        total_cost = annual_rent + annual_ops

        c = CandidateLocation(
            id=row['id'],
            name=f"Location {row['id']}",
            rent_cost=annual_rent,
            setup_cost=setup_cost,
            traffic=traffic,
            area=row['area_sqm'],
            competitors_count=0, # TODO: query this
            population_density=row['population_density'],
            avg_income=row['avg_income'],
            expected_revenue=revenue,
            expected_cost=total_cost
        )
        candidates.append(c)
    return candidates

def fetch_distance_matrix(db):
    query = "SELECT premise_id, store_id, distance_meters FROM distances"
    rows = db.fetch_all(query)
    # This table stores dist between candidate and EXISTING stores.
    # For optimization, we might also need dist between CANDIDATE and CANDIDATE to avoid cannibalization.
    # For this demo, we will assume we only check against existing stores or we need to compute candidate-candidate distances.
    # Since we don't have candidate-candidate distances in DB yet (only candidate-store),
    # we will skip the complex self-cannibalization check in this DB fetch
    # and rely on the optimizer to compute it if we had coordinates.
    # For simplicity in this demo, we will return empty or implement coordinate fetching if needed.
    return {}

def main():
    print("--- Convenience Store Location Optimizer ---")
    db = Database(DB_CONFIG)
    conn = db.connect()

    if not conn:
        print("Failed to connect to database. Please check configuration.")
        # Fallback for demonstration if DB fails
        print("Running in MOCK mode (no DB connection)...")
        candidates = [
            CandidateLocation(1, "Loc 1", 200, 500, 5000, 0, 0, 10000, 10, 8000, 1500), # High profit
            CandidateLocation(2, "Loc 2", 150, 500, 3000, 0, 0, 5000, 8, 4000, 1000),
            CandidateLocation(3, "Loc 3", 300, 600, 8000, 0, 0, 15000, 12, 12000, 2000), # Very high profit but expensive
            CandidateLocation(4, "Loc 4", 100, 400, 1000, 0, 0, 2000, 5, 1500, 800),
            CandidateLocation(5, "Loc 5", 180, 500, 4000, 0, 0, 8000, 9, 6000, 1200),
        ]
    else:
        print("Fetching candidates from database...")
        candidates = fetch_candidates(db)
        db.close()

    print(f"Found {len(candidates)} candidates.")

    optimizer = StoreOptimizer(candidates, BUDGET, MAX_STORES, MIN_DISTANCE_M)
    result = optimizer.solve()

    print("\n--- Optimization Results ---")
    print(f"Total Expected Profit: {result.total_profit:,.2f} Million VND")
    print(f"Total Investment Cost: {result.total_cost:,.2f} Million VND")
    print(f"Selected Locations ({len(result.selected_locations)}):")
    for loc in result.selected_locations:
        print(f" - ID: {loc.id}, Revenue: {loc.expected_revenue:.1f}, Cost: {loc.expected_cost:.1f}, Profit: {loc.expected_revenue - loc.expected_cost:.1f}")

if __name__ == "__main__":
    main()
