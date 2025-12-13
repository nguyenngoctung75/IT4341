import numpy as np
import pandas as pd

class TopsisAnalyzer:
    def __init__(self, df, weights=None, criteria_types=None):
        """
        Initialize the TOPSIS analyzer.
        :param df: pandas DataFrame containing the data (Alternative set).
                   Must involve columns corresponding to criteria.
        :param weights: Dictionary mapping column names to weights (must sum to 1).
        :param criteria_types: Dictionary mapping column names to 'benefit' or 'cost'.
        """
        self.df = df.copy()
        
        # Define default criteria columns mapping if not provided
        # Based on previous plan:
        # C1: price (Cost)
        # C2: area (Benefit)
        # C3: frontage (Benefit)
        # C4: foot_traffic (Benefit) - Note: foot_traffic is mapped to numerical levels usually? 
        #     In DB it's INT/VARCHAR? The schema says INT. Assuming higher is better.
        # C5: employee_cost (Cost)
        # C6: utilities_cost (Cost)
        # C7: min_opponent_dist (Benefit - we want to be far away)
        
        self.criteria_cols = [
            'price', 'area', 'frontage', 'foot_traffic', 
            'employee_cost', 'utilities_cost', 'min_opponent_dist'
        ]
        
        if weights is None:
            # Default equal weights
            n = len(self.criteria_cols)
            self.weights = {col: 1.0/n for col in self.criteria_cols}
        else:
            self.weights = weights
            
        if criteria_types is None:
            self.criteria_types = {
                'price': 'cost',
                'area': 'benefit',
                'frontage': 'benefit',
                'foot_traffic': 'benefit',
                'employee_cost': 'cost',
                'utilities_cost': 'cost',
                'min_opponent_dist': 'benefit'
            }
        else:
            self.criteria_types = criteria_types

    def normalize(self):
        """Step 2: Normalize the decision matrix."""
        # Vector normalization
        # r_ij = x_ij / sqrt(sum(x_kj^2))
        self.normalized_df = self.df.copy()
        
        for col in self.criteria_cols:
            # Handle potential zero vector to avoid division by zero
            denom = np.sqrt((self.df[col]**2).sum())
            if denom == 0:
                self.normalized_df[col] = 0
            else:
                self.normalized_df[col] = self.df[col] / denom
                
    def calculate_weighted_normalized(self):
        """Step 3: Calculate weighted normalized decision matrix."""
        # v_ij = w_j * r_ij
        self.weighted_df = self.normalized_df.copy()
        for col in self.criteria_cols:
            self.weighted_df[col] = self.normalized_df[col] * self.weights.get(col, 0)

    def determine_ideal_solutions(self):
        """Step 4: Determine Ideal (A*) and Negative-Ideal (A-) solutions."""
        self.ideal_best = {}
        self.ideal_worst = {}
        
        for col in self.criteria_cols:
            col_type = self.criteria_types.get(col, 'benefit')
            
            if col_type == 'benefit':
                self.ideal_best[col] = self.weighted_df[col].max()
                self.ideal_worst[col] = self.weighted_df[col].min()
            else: # cost
                self.ideal_best[col] = self.weighted_df[col].min()
                self.ideal_worst[col] = self.weighted_df[col].max()
                
    def calculate_similarity(self):
        """Step 5 & 6: Calculate separation measures and relative closeness."""
        # S_i* = sqrt(sum((v_ij - v_j*)^2))
        # S_i- = sqrt(sum((v_ij - v_j-)^2))
        
        s_best = np.zeros(len(self.weighted_df))
        s_worst = np.zeros(len(self.weighted_df))
        
        for col in self.criteria_cols:
            s_best += (self.weighted_df[col] - self.ideal_best[col])**2
            s_worst += (self.weighted_df[col] - self.ideal_worst[col])**2
            
        s_best = np.sqrt(s_best)
        s_worst = np.sqrt(s_worst)
        
        # C_i* = S_i- / (S_i* + S_i-)
        # Handle zero division if S_i* + S_i- == 0 (unlikely if data variance exists)
        total_dist = s_best + s_worst
        
        # If total_dist is 0, score is 0 (or undefined, but effectively neutral)
        self.scores = np.divide(s_worst, total_dist, out=np.zeros_like(s_worst), where=total_dist!=0)
        
    def get_ranking(self):
        """Run the full process and return ranked DataFrame."""
        self.normalize()
        self.calculate_weighted_normalized()
        self.determine_ideal_solutions()
        self.calculate_similarity()
        
        result_df = self.df.copy()
        result_df['topsis_score'] = self.scores
        
        # Sort by score descending
        ranked_df = result_df.sort_values(by='topsis_score', ascending=False)
        
        # Return relevant columns
        cols_to_show = ['shop_id', 'address', 'topsis_score'] + self.criteria_cols
        return ranked_df[cols_to_show]

if __name__ == '__main__':
    # Mock data for testing
    data = {
        'shop_id': [1, 2, 3],
        'address': ['A', 'B', 'C'],
        'price': [10, 20, 15],
        'area': [50, 60, 55],
        'frontage': [5, 6, 5.5],
        'foot_traffic': [100, 120, 110],
        'employee_cost': [200, 220, 210],
        'utilities_cost': [50, 60, 55],
        'min_opponent_dist': [0.5, 1.0, 0.8]
    }
    df = pd.DataFrame(data)
    analyzer = TopsisAnalyzer(df)
    print(analyzer.get_ranking())
