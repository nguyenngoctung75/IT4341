import yaml
import pandas as pd
import re
import unicodedata

def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    # Normalize unicode characters to NFC (composed form)
    s = unicodedata.normalize('NFC', s)
    return s.strip().lower()

def clean_area(area_str):
    """
    "105 m²" -> 105.0
    "105" -> 105.0
    """
    if not isinstance(area_str, str):
        return 0.0

    # Remove " m²", "m2", "m"
    s = area_str.lower().replace('m²', '').replace('m2', '').replace('m', '').strip()
    # Remove thousand separators if any (like 1.500 -> 1500)
    # But be careful with decimals. Vietnamese use dot for thousands usually in price,
    # but area might use comma for decimal.
    # Examples in CSV: "105 m²", "1.500 m²", "77 m²"
    # "1.500 m²" likely means 1500, not 1.5.
    s = s.replace('.', '').replace(',', '.')

    try:
        return float(s)
    except:
        return 0.0

def clean_frontage(frontage_str):
    """
    "Mặt tiền 4 m" -> 4.0
    "4 m" -> 4.0
    """
    if not isinstance(frontage_str, str):
        return 0.0

    # Remove "Mặt tiền", "m"
    s = frontage_str.lower().replace('mặt tiền', '').replace('mặt tiền', '').replace('m', '').strip()
    s = s.replace(',', '.')

    try:
        return float(s)
    except:
        return 0.0

def main():
    districts = load_yaml('districts.yml')
    wards = load_yaml('wards.yml')

    # Build lookup maps
    # District ID -> List of Ward Objects
    wards_by_district = {}
    for w in wards:
        d_id = w['district_id']
        if d_id not in wards_by_district:
            wards_by_district[d_id] = []
        wards_by_district[d_id].append(w)

    # Normalized District Name -> District ID
    # Handle "Quận " prefix optionally for matching
    district_map = {}
    for d in districts:
        name = normalize_string(d['name'])
        district_map[name] = d['id']
        # Also map without "Quận/Huyện" prefix
        name_clean = name.replace('quận ', '').replace('huyện ', '').replace('thị xã ', '')
        district_map[name_clean] = d['id']

    # Read CSV
    try:
        df = pd.read_csv('final.csv')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    shops_list = []

    # Iterate rows
    # Columns: url,title,address,price,area,contact_name,contact_phone,post_id,post_date,expire_date,description
    for idx, row in df.iterrows():
        address = str(row['address']) if pd.notna(row['address']) else ""
        addr_lower = normalize_string(address)

        # 1. Find District
        found_d_id = None

        # Sort district names by length descending to match longest first (e.g. avoid matching substring issues if any)
        # But identifying exact match is better.
        # Address usually contains district name.

        # We look for district name in address
        for d_name, d_id in district_map.items():
            if d_name in addr_lower:
                found_d_id = d_id
                break # Found a district

        # 2. Find Ward in that District
        found_w_id = None
        if found_d_id:
            district_wards = wards_by_district.get(found_d_id, [])
            # Search for ward name in address
            # Sort wards by length desc to match long names first
            district_wards.sort(key=lambda x: len(x['name']), reverse=True)

            for w in district_wards:
                w_name = normalize_string(w['name'])
                # Ward name in address often prefixed with "Phường" or just name
                # Address: "..., Phường Đại Kim, ..." or "..., Đại Kim, ..."

                # Check for "phường " + w_name
                # or just w_name if unique enough?
                # Simple check:
                if w_name in addr_lower:
                    found_w_id = w['id']
                    break

        # Prepare Data
        shop_data = {
            'id': idx + 1, # specific requirement: id
            'address': address,
            'ward_id': found_w_id, # id_phường
            'price': str(row['price']) if pd.notna(row['price']) else "",
            'area': clean_area(row['area']), # clean to number
            'frontage': clean_frontage(row['frontage']) if 'frontage' in row and pd.notna(row['frontage']) else 0.0,
            'description': str(row['description']) if pd.notna(row['description']) else ""
        }

        shops_list.append(shop_data)

    # Write to YAML
    with open('rental_shops.yml', 'w', encoding='utf-8') as f:
        yaml.dump(shops_list, f, allow_unicode=True, sort_keys=False)

    print(f"Generated rental_shops.yml with {len(shops_list)} entries.")

    # Stats
    mapped_count = sum(1 for s in shops_list if s['ward_id'] is not None)
    print(f"Successfully mapped Ward ID for {mapped_count}/{len(shops_list)} shops.")

if __name__ == "__main__":
    main()
