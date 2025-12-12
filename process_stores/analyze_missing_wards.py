import yaml
import unicodedata
import re

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    stores = load_yaml('convenience_stores.yml')
    
    total = len(stores)
    with_ward = sum(1 for s in stores if s.get('ward_id'))
    missing_ward = [s for s in stores if not s.get('ward_id')]
    
    with open('analysis_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total stores: {total}\n")
        f.write(f"Stores with ward_id: {with_ward}\n")
        f.write(f"Stores missing ward_id: {len(missing_ward)}\n")
        f.write("-" * 50 + "\n")
        
        f.write("Analysis of missing wards:\n")
        for s in missing_ward:
            f.write(f"ID: {s['id']}\n")
            f.write(f"Name: {s['name']}\n")
            f.write(f"Address: {s['address']}\n")
            f.write(f"District ID found: {s.get('district_id')}\n")
            f.write("-" * 20 + "\n")

if __name__ == '__main__':
    main()
