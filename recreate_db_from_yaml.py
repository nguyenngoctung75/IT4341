import yaml
import mysql.connector
from database import Database

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '07052004' # Using password from seed_data.py
}
DB_NAME = 'convenience_store_db'

def load_yaml(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_script():
    # 1. Connect and initialize DB
    print("Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute schema.sql to create DB and tables
        print("Executing schema.sql...")
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Split logic for schema execution
        statements = schema_sql.split(';')
        for stmt in statements:
            if stmt.strip():
                cursor.execute(stmt)

        conn.commit()
        print("Database structure created.")

        # Reconnect to the specific database for insertions
        conn.close()
        DB_CONFIG['database'] = DB_NAME
        db = Database(DB_CONFIG)
        conn = db.connect()
        cursor = conn.cursor()

    except Exception as e:
        print(f"Error initializing database: {e}")
        return

    # 2. Import Districts (transform name)
    print("Importing Districts...")
    try:
        districts = load_yaml('districts.yml')
        for d in districts:
            # removing "Quận"
            clean_name = d['name'].replace('Quận', '').strip()
            # Handle "Quận Nam Từ Liêm" -> "Nam Từ Liêm"

            sql = "INSERT INTO districts (id, name) VALUES (%s, %s)"
            cursor.execute(sql, (d['id'], clean_name))
        conn.commit()
    except Exception as e:
        print(f"Error importing districts: {e}")

    # 3. Import Wards
    print("Importing Wards...")
    try:
        wards = load_yaml('wards.yml')
        for w in wards:
            sql = "INSERT INTO wards (id, district_id, name) VALUES (%s, %s, %s)"
            cursor.execute(sql, (w['id'], w['district_id'], w['name']))
        conn.commit()
    except Exception as e:
        print(f"Error importing wards: {e}")

    # 4. Import Ward Demographics
    print("Importing Ward Demographics...")
    try:
        demos = load_yaml('ward_demographics.yml')
        if demos:
            for d in demos:
                sql = "INSERT INTO ward_demographics (id, ward_id, population, density) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (d['id'], d['ward_id'], d['population'], d['density']))
            conn.commit()
    except Exception as e:
        print(f"Error importing ward demographics: {e}")

    # 5. Import Opponent Stores
    print("Importing Opponent Stores...")
    try:
        opponents = load_yaml('opponent_convenience_stores.yml')
        if opponents:
            for o in opponents:
                sql = """INSERT INTO opponent_stores (id, district_id, ward_id, name, address, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (o['id'], o['district_id'], o['ward_id'], o['name'], o['address'], o['latitude'], o['longitude']))
            conn.commit()
    except Exception as e:
        print(f"Error importing opponent stores: {e}")

    # 6. Import Rental Shops
    print("Importing Rental Shops...")
    try:
        shops = load_yaml('rental_shops.yml')
        if shops:
            for s in shops:
                # Handle possible missing keys
                frontage = s.get('frontage', 0.0)
                desc = s.get('description', '')

                # Check validation for ward_id (some might be null or invalid fk?)
                # We assume data is cleaner now.

                sql = """INSERT INTO rental_shops (id, ward_id, address, price, area, frontage, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (s['id'], s['ward_id'], s['address'], s['price'], s['area'], frontage, desc))
            conn.commit()
    except Exception as e:
        print(f"Error importing rental shops: {e}")

    # 7. Import Distances (shop_opponent_distances)
    print("Importing Shop-Opponent Distances...")
    try:
        dists = load_yaml('shop_opponent_distances.yml')
        if dists:
            for d in dists:
                sql = "INSERT INTO shop_opponent_distances (id, shop_id, opponent_id, distance_km) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (d['id'], d['shop_id'], d['opponent_id'], d['distance_km']))
            conn.commit()
    except Exception as e:
        print(f"Error importing distances: {e}")

    # 8. Import Other Factors
    print("Importing Other Factors...")
    try:
        factors = load_yaml('other_factors.yml')
        if factors:
            for f in factors:
                sql = """INSERT INTO other_factors (id, rental_shop_id, foot_traffic, employee_cost, utilities_cost)
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (f['id'], f['rental_shop_id'], f['foot_traffic'], f['employee_cost'], f['utilities_cost']))
            conn.commit()
    except Exception as e:
        print(f"Error importing other factors: {e}")

    print("Success! Database recreated.")
    if conn:
        conn.close()

if __name__ == "__main__":
    run_script()
