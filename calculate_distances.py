import yaml
import math
import sys
import os

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def load_yaml(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or []

def save_yaml(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def main():
    shops_file = 'rental_shops.yml'
    opponents_file = 'opponent_convenience_stores.yml'
    output_file = 'shop_opponent_distances.yml'

    print("Loading data...")
    shops = load_yaml(shops_file)
    opponents = load_yaml(opponents_file)

    print(f"Loaded {len(shops)} rental shops and {len(opponents)} opponents.")

    # Index opponents by ward_id to speed up lookup
    opponents_by_ward = {}
    for opp in opponents:
        ward_id = opp.get('ward_id')
        if ward_id:
            if ward_id not in opponents_by_ward:
                opponents_by_ward[ward_id] = []
            opponents_by_ward[ward_id].append(opp)

    distances_list = []
    next_id = 1

    for shop in shops:
        shop_ward_id = shop.get('ward_id')

        # Skip if no ward or no coordinates
        if not shop_ward_id:
            continue

        shop_lat = shop.get('latitude')
        shop_lon = shop.get('longitude')

        if shop_lat is None or shop_lon is None:
            # Skip shops without coords (probably pending geocoding)
            continue

        # Get opponents in the same ward
        nearby_opponents = opponents_by_ward.get(shop_ward_id, [])

        for opp in nearby_opponents:
            opp_lat = opp.get('latitude')
            opp_lon = opp.get('longitude')

            if opp_lat is None or opp_lon is None:
                continue

            dist = haversine_distance(shop_lat, shop_lon, opp_lat, opp_lon)

            entry = {
                'id': next_id,
                'shop_id': shop['id'],
                'opponent_id': opp['id'],
                'distance_km': round(dist, 4)
            }
            distances_list.append(entry)
            next_id += 1

    print(f"Calculated {len(distances_list)} distances.")
    save_yaml(output_file, distances_list)
    print(f"Saved results to {output_file}")

if __name__ == "__main__":
    main()
