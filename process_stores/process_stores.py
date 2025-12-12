import csv
import yaml
import unicodedata
import re

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def flexible_normalize(text):
    if not text:
        return ""
    # Normalize unicode (NFD)
    text = unicodedata.normalize('NFD', text)
    # Remove accents
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Lowercase
    text = text.lower()
    return text

def clean_address_for_matching(text):
    """
    Remove common prefixes to help with matching, but keep the core name.
    """
    norm = flexible_normalize(text)
    # Remove common prefixes
    # Note: We keep the text relatively intact to check for "Pho Hai Ba Trung" vs "Quan Hai Ba Trung"
    return norm

def get_potential_matches(address_norm, items, type='district'):
    matches = []
    for item in items:
        # Check normalized name
        if item['norm_name'] in address_norm:
            # Heuristic: Check for "False Positives" for Districts
            if type == 'district':
                # If district name is "Hai Ba Trung", check if it's "Pho Hai Ba Trung"
                # This is a simple check.
                idx = address_norm.find(item['norm_name'])
                if idx > 0:
                    prefix = address_norm[max(0, idx-10):idx].strip()
                    if prefix.endswith('pho') or prefix.endswith('duong'):
                        # Likely a street name, ignore unless "Quan" is explicitly there?
                        # But "Quan" might be missing.
                        # Let's just flag it or lower priority?
                        # For now, let's include it but maybe we can filter later based on Ward intersection.
                        pass
            matches.append(item)
    return matches

def main():
    districts = load_yaml('districts.yml')
    wards = load_yaml('wards.yml')
    
    # Precompute normalized names
    for d in districts:
        d['norm_name'] = flexible_normalize(d['name'].replace('Quận ', '').replace('Huyện ', '').replace('Thị xã ', ''))
        d['full_norm_name'] = flexible_normalize(d['name'])
        
    for w in wards:
        raw_name = w['name']
        if raw_name.startswith(': '): raw_name = raw_name[2:]
        if raw_name.startswith('Ô '): raw_name = raw_name[2:]
        w['clean_name'] = raw_name
        w['norm_name'] = flexible_normalize(raw_name.replace('Phường ', '').replace('Xã ', '').replace('Thị trấn ', ''))

    stores = []
    
    with open('all_convenience_stores_hanoi.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        store_id_counter = 1
        
        for row in reader:
            if 'name' not in row:
                 for k in row.keys():
                     if k and k.endswith('name'):
                         row['name'] = row[k]
                         break
            
            name = row.get('name', '')
            address = row.get('address', '')
            
            try:
                lat = float(row.get('latitude')) if row.get('latitude') and row.get('latitude') != 'N/A' else None
                lon = float(row.get('longitude')) if row.get('longitude') and row.get('longitude') != 'N/A' else None
            except:
                lat, lon = None, None

            address_norm = flexible_normalize(address)
            
            # 1. Find ALL potential districts
            potential_districts = []
            for d in districts:
                # Check strict full name first "Quan Hai Ba Trung"
                if d['full_norm_name'] in address_norm:
                    potential_districts.append(d)
                # Check short name "Hai Ba Trung"
                elif d['norm_name'] in address_norm:
                    # Check if it's a street name (preceded by 'pho', 'duong', 'p.')
                    # This is tricky. regex lookbehind?
                    # simple check:
                    pattern = r'(pho|duong|p\.|ng.)\s*' + re.escape(d['norm_name'])
                    if not re.search(pattern, address_norm):
                        potential_districts.append(d)
            
            # 2. Find ALL potential wards
            potential_wards = []
            for w in wards:
                # Ward names can be short like "Lang Ha".
                # Check if it exists in address
                # Use word boundary to avoid "Trung" matching "Trung Hoa"
                # But flexible_normalize removes punctuation so boundaries are spaces.
                
                # Check for exact word match
                # e.g. "lang ha" in "123 lang ha" -> yes
                # "ha" in "ngoc ha" -> yes (bad)
                
                # So we should check if w['norm_name'] is a substring.
                if w['norm_name'] in address_norm:
                     potential_wards.append(w)

            # 3. Find Intersection
            final_district_id = None
            final_ward_id = None
            
            # Strategy A: We have potential districts. Check if any potential ward belongs to them.
            if potential_districts:
                # Sort districts by length (longest match first) - though usually we have 1 or 2.
                # If we have "Hai Ba Trung" (District) and "Hoan Kiem" (District)
                # And "Cua Nam" (Ward in Hoan Kiem)
                # We should pick Hoan Kiem.
                
                found_match = False
                for d in potential_districts:
                    # Find wards in this district that are also in potential_wards
                    valid_wards = [w for w in potential_wards if w['district_id'] == d['id']]
                    if valid_wards:
                        # Pick the longest ward name match?
                        valid_wards.sort(key=lambda x: len(x['norm_name']), reverse=True)
                        final_ward_id = valid_wards[0]['id']
                        final_district_id = d['id']
                        found_match = True
                        break
                
                if not found_match:
                    # We have districts but no matching wards found.
                    # Just pick the first district (longest name usually better?)
                    potential_districts.sort(key=lambda x: len(x['norm_name']), reverse=True)
                    final_district_id = potential_districts[0]['id']
            
            # Strategy B: No potential districts found (or filtered out).
            # Look at potential wards.
            # If we find a ward that is "Unique" (only exists in one district), we can infer the district.
            # Or if we find a ward, and maybe the district name was missing or typoed.
            elif potential_wards:
                # Filter out very short ward names that might be false positives (e.g. "yen", "hoa")
                # "Yen" is not a ward, but "Yen Hoa" is.
                # "Lang" might be "Lang Thuong" or "Lang Ha".
                
                # Let's sort by length. Longest ward name is likely correct.
                potential_wards.sort(key=lambda x: len(x['norm_name']), reverse=True)
                
                best_ward = potential_wards[0]
                # If the ward name is reasonably long (e.g. > 3 chars), assume it's correct?
                if len(best_ward['norm_name']) > 3:
                    final_ward_id = best_ward['id']
                    final_district_id = best_ward['district_id']

            # Construct Object
            store_obj = {
                'id': store_id_counter,
                'district_id': final_district_id,
                'ward_id': final_ward_id,
                'name': name,
                'address': address,
                'latitude': lat,
                'longitude': lon
            }
            stores.append(store_obj)
            store_id_counter += 1

    # Filter: Only include stores with valid ward_id
    valid_stores = [s for s in stores if s['ward_id'] is not None]
    
    # Re-assign IDs sequentially
    for i, s in enumerate(valid_stores, 1):
        s['id'] = i

    # Write output
    with open('convenience_stores.yml', 'w', encoding='utf-8') as f:
        yaml.dump(valid_stores, f, allow_unicode=True, sort_keys=False)
        
    print(f"Total stores in CSV: {len(stores)}")
    print(f"Stores with valid ward_id: {len(valid_stores)}")
    print(f"Stores excluded (no ward_id): {len(stores) - len(valid_stores)}")

if __name__ == '__main__':
    main()
