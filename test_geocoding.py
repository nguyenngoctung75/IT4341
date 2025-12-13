import yaml
import time
import re
import urllib.parse
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout.reconfigure(encoding='utf-8')

def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

def get_coordinates(driver, address):
    try:
        # Construct Google Maps Search URL
        query = urllib.parse.quote(f"{address}, Việt Nam")
        url = f"https://www.google.com/maps/search/?api=1&query={query}"

        driver.get(url)

        # Wait for redirect and URL update
        # We poll the URL for a few seconds
        max_wait = 10
        start_time = time.time()

        coords = None

        while time.time() - start_time < max_wait:
            current_url = driver.current_url

            # Look for @lat,long pattern
            # Example: .../@20.9852339,105.7860845,17z...
            match = re.search(r'@([-.\d]+),([-.\d]+)', current_url)
            if match:
                lat = float(match.group(1))
                lng = float(match.group(2))
                coords = (lat, lng)
                break

            time.sleep(0.5)

        return coords

    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None

def main():
    shops_file = 'rental_shops.yml'
    shops = load_yaml(shops_file)

    print(f"Loaded {len(shops)} shops. Starting geocoding...")

    # Setup Headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    updated_count = 0

    try:
        for shop in shops:
            address = shop.get('address')
            print(f"[{shop['id']}] Processing: {address}...", end=" ", flush=True)

            # Skip if already exists (optional, but good for resuming)
            # if 'latitude' in shop and shop['latitude']:
            #     print("Skipped (Already has coords)")
            #     continue

            coords = get_coordinates(driver, address)

            if coords:
                lat, lng = coords
                print(f"Found: {lat}, {lng}")

                # Update Dictionary Order
                # We want lat/long after area
                new_shop = {}
                for k, v in shop.items():
                    new_shop[k] = v
                    if k == 'area':
                        new_shop['latitude'] = lat
                        new_shop['longitude'] = lng

                # Replace the shop entry with the new ordered one
                # (Note: Python 3.7+ dicts preserve insertion order)
                shop.clear()
                shop.update(new_shop)

                updated_count += 1
            else:
                print("Not found.")

            # Periodically save? Or save at end.
            # Saving at end is safer against partial file corruption,
            # but for long scripts, intermediate saving is better.
            # For 200 items, saving at end is fine.

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving progress...")
    finally:
        driver.quit()
        save_yaml(shops_file, shops)
        print(f"\nFinished. Updated {updated_count} shops. Saved to {shops_file}")

if __name__ == "__main__":
    main()
