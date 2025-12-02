import pulp
from models import CandidateLocation, OptimizationResult

class StoreOptimizer:
    def __init__(self, candidates: list[CandidateLocation], budget: float, max_stores: int, min_distance: float = 0):
        self.candidates = candidates
        self.budget = budget
        self.max_stores = max_stores
        self.min_distance = min_distance
        self.model = pulp.LpProblem("ConvenienceStoreLocation", pulp.LpMaximize)
        self.decision_vars = {}

    def solve(self, distance_matrix: dict = None) -> OptimizationResult:
        # 1. Decision Variables
        # x[i] = 1 if location i is selected, 0 otherwise
        for c in self.candidates:
            self.decision_vars[c.id] = pulp.LpVariable(f"x_{c.id}", cat='Binary')

        # 2. Objective Function
        # Maximize Total Expected Profit (Revenue - Cost)
        # We can also add weights for other factors like market share (population density)
        # For now, simple profit maximization:
        profit_expr = pulp.lpSum([
            (c.expected_revenue - c.expected_cost) * self.decision_vars[c.id]
            for c in self.candidates
        ])
        self.model += profit_expr, "Total_Expected_Profit"

        # 3. Constraints

        # Budget Constraint
        # Setup cost + 1 year rent (example)
        cost_expr = pulp.lpSum([
            (c.setup_cost + c.rent_cost) * self.decision_vars[c.id]
            for c in self.candidates
        ])
        self.model += cost_expr <= self.budget, "Budget_Constraint"

        # Max Stores Constraint
        count_expr = pulp.lpSum([self.decision_vars[c.id] for c in self.candidates])
        self.model += count_expr <= self.max_stores, "Max_Stores_Constraint"

        # Min Stores Constraint (Optional, e.g. at least 1)
        self.model += count_expr >= 1, "Min_Stores_Constraint"

        # Distance Constraint (Conflict Constraints)
        # If dist(i, j) < min_distance, then x_i + x_j <= 1
        if distance_matrix and self.min_distance > 0:
            # distance_matrix is expected to be {(id1, id2): distance, ...}
            # We iterate through pairs to find conflicts
            # This can be expensive for large N, but fine for N < 1000
            ids = [c.id for c in self.candidates]
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    id1 = ids[i]
                    id2 = ids[j]
                    dist = distance_matrix.get((id1, id2)) or distance_matrix.get((id2, id1))
                    if dist and dist < self.min_distance:
                        self.model += self.decision_vars[id1] + self.decision_vars[id2] <= 1, f"Distance_Conflict_{id1}_{id2}"

        # 4. Solve
        status = self.model.solve(pulp.PULP_CBC_CMD(msg=False))

        print(f"Optimization Status: {pulp.LpStatus[status]}")

        # 5. Extract Results
        selected = []
        total_profit = 0
        total_cost = 0

        if status == pulp.LpStatusOptimal:
            for c in self.candidates:
                if pulp.value(self.decision_vars[c.id]) == 1:
                    selected.append(c)
                    total_profit += (c.expected_revenue - c.expected_cost)
                    total_cost += (c.setup_cost + c.rent_cost)

        return OptimizationResult(
            selected_locations=selected,
            total_profit=total_profit,
            total_cost=total_cost
        )
