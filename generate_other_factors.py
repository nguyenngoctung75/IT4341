import yaml
import statistics

# Load data
with open('rental_shops.yml', 'r', encoding='utf-8') as f:
    rental_shops = yaml.safe_load(f)

with open('ward_demographics.yml', 'r', encoding='utf-8') as f:
    ward_demographics = yaml.safe_load(f)

# Create a mapping of ward_id to density
ward_density_map = {item['ward_id']: item['density'] for item in ward_demographics}

# Get densities for wards that HAVE rental shops (THIS IS THE FIX!)
rental_shop_ward_ids = set([shop['ward_id'] for shop in rental_shops])
densities_with_rental_shops = [ward_density_map[ward_id] for ward_id in rental_shop_ward_ids if ward_id in ward_density_map]

# Calculate Q33 and Q66 on wards WITH rental shops
q33 = statistics.quantiles(densities_with_rental_shops, n=3)[0]
q66 = statistics.quantiles(densities_with_rental_shops, n=3)[1]

print(f"Tính phân vị trên {len(densities_with_rental_shops)} phường có mặt bằng cho thuê:")
print(f"Q33 (33rd percentile): {q33}")
print(f"Q66 (66th percentile): {q66}")

# Function to determine foot traffic level based on density
def get_foot_traffic_level(density):
    if density >= q66:
        return "cao"
    elif density >= q33:
        return "trung bình"
    else:
        return "thấp"

# Function to calculate employee cost
def calculate_employee_cost(foot_traffic_level, area):
    base_employees = area / 50
    
    if foot_traffic_level == "cao":
        employees = base_employees * 1.5
    elif foot_traffic_level == "trung bình":
        employees = base_employees * 1.0
    else:  # thấp
        employees = base_employees * 0.7
    
    employees = max(1, round(employees))
    cost = employees * 20
    
    return round(cost, 1)

# Function to calculate utilities cost
def calculate_utilities_cost(foot_traffic_level, area):
    k1 = 70  # thousand VND/m²
    k2 = 30  # thousand VND/m²
    
    if foot_traffic_level == "cao":
        L = 1.3
    elif foot_traffic_level == "trung bình":
        L = 1.0
    else:  # thấp
        L = 0.8
    
    C = (k1 * area) + (k2 * area * L)
    
    return round(C, 1)

# Generate other factors data
other_factors = []

for shop in rental_shops:
    shop_id = shop['id']
    rental_shop_id = shop['id']
    ward_id = shop['ward_id']
    area = shop['area']
    
    # Get density for this ward
    density = ward_density_map.get(ward_id, 0)
    
    # Determine foot traffic level
    foot_traffic = get_foot_traffic_level(density)
    
    # Calculate employee cost
    employee_cost = calculate_employee_cost(foot_traffic, area)
    
    # Calculate utilities cost
    utilities_cost = calculate_utilities_cost(foot_traffic, area)
    
    other_factors.append({
        'id': shop_id,
        'rental_shop_id': rental_shop_id,
        'foot_traffic': foot_traffic,
        'employee_cost': employee_cost,
        'utilities_cost': utilities_cost
    })

# Write to YAML file
with open('other_factors.yml', 'w', encoding='utf-8') as f:
    yaml.dump(other_factors, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

# Count distribution
from collections import Counter
traffic_counts = Counter([item['foot_traffic'] for item in other_factors])

print(f"\nĐã tạo {len(other_factors)} bản ghi")
print("\nPhân bố lượng người qua lại:")
for level in ["cao", "trung bình", "thấp"]:
    count = traffic_counts[level]
    print(f"  {level}: {count} ({count/len(other_factors)*100:.1f}%)")
print("\nĐã ghi vào other_factors.yml")
