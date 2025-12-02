import random
import pandas as pd
from faker import Faker
from database import Database
import mysql.connector

# Configuration - REPLACE WITH YOUR ACTUAL DB CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'database': 'convenience_store_db',
    'user': 'root',
    'password': '07052004'
}

fake = Faker('vi_VN')

def create_database_if_not_exists():
    print("Checking database...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database {DB_CONFIG['database']} created or already exists.")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

def execute_schema(db, schema_file):
    print(f"Executing schema from {schema_file}...")
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Split by semicolon and execute each command
        commands = schema_sql.split(';')
        for cmd in commands:
            if cmd.strip():
                try:
                    db.execute_query(cmd)
                except Exception as e:
                    print(f"Error executing command: {cmd[:50]}... -> {e}")
    except Exception as e:
        print(f"Schema execution error: {e}")

def seed_wards(db, count=10):
    print("Seeding Wards...")
    ward_ids = []
    wards = ['Hoàn Kiếm', 'Đống Đa', 'Ba Đình', 'Hai Bà Trưng', 'Hoàng Mai', 'Thanh Xuân', 'Cầu Giấy', 'Tây Hồ']
    for name in wards:
        query = "INSERT INTO wards (name) VALUES (%s)"
        cursor = db.execute_query(query, (name,))
        if cursor:
            ward_ids.append(cursor.lastrowid)
    return ward_ids

def import_from_csv(db, csv_path, ward_ids):
    print(f"Importing data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return [], []

    # Shuffle data
    df = df.sample(frac=1).reset_index(drop=True)

    # Split 50/50
    split_idx = len(df) // 2
    existing_df = df.iloc[:split_idx]
    candidates_df = df.iloc[split_idx:]

    store_ids = []
    premise_ids = []

    # 1. Import Existing Stores
    print("Importing Existing Stores...")
    for _, row in existing_df.iterrows():
        ward_id = random.choice(ward_ids)
        lat = row['latitude']
        lng = row['longitude']
        name = row['name']

        query = """
        INSERT INTO existing_stores (ward_id, latitude, longitude, name, store_type)
        VALUES (%s, %s, %s, %s, 'COMPETITOR')
        """
        cursor = db.execute_query(query, (ward_id, lat, lng, name))
        if cursor:
            store_ids.append(cursor.lastrowid)

    # 2. Import Candidate Premises
    print("Importing Candidate Premises...")
    for _, row in candidates_df.iterrows():
        ward_id = random.choice(ward_ids)
        lat = row['latitude']
        lng = row['longitude']

        # Mock attributes
        frontage = random.uniform(3.0, 15.0)
        area = frontage * random.uniform(5.0, 20.0)
        has_parking = random.choice([True, False])
        rent = random.uniform(100, 1000) # Million VND
        transport_cost = random.uniform(5, 20)
        traffic = random.randint(500, 10000)

        query = """
        INSERT INTO premises (ward_id, latitude, longitude, frontage_width, area_sqm, has_parking, annual_rent, monthly_transport_cost, daily_traffic)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor = db.execute_query(query, (ward_id, lat, lng, frontage, area, has_parking, rent, transport_cost, traffic))
        if cursor:
            premise_ids.append(cursor.lastrowid)

    return premise_ids, store_ids

def seed_location_factors(db, premise_ids):
    print("Seeding Location Factors...")
    for p_id in premise_ids:
        staff_cost = random.uniform(10, 50)
        manager_cost = random.uniform(15, 30)
        utility_cost = random.uniform(2, 10)
        risk = random.uniform(0, 0.5)
        env = random.choice(['Clean', 'Noisy', 'Dusty', 'Crowded'])

        query = """
        INSERT INTO location_factors (premise_id, monthly_staff_cost, monthly_manager_cost, monthly_utility_cost, legal_risk_score, environment_desc)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (p_id, staff_cost, manager_cost, utility_cost, risk, env))

def seed_demographics(db, premise_ids):
    print("Seeding Demographics...")
    for p_id in premise_ids:
        density = random.uniform(2000, 20000)
        income = random.uniform(5, 30) # Million VND
        age = random.randint(20, 60)

        query = """
        INSERT INTO demographics (premise_id, population_density, avg_income, avg_age)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (p_id, density, income, age))

def seed_distances(db, premise_ids, store_ids):
    print("Seeding Distances...")
    if not premise_ids or not store_ids:
        return

    # Fetch Premise Coords
    p_map = {}
    if premise_ids:
        p_ids_str = ",".join(map(str, premise_ids))
        p_rows = db.fetch_all(f"SELECT id, latitude, longitude FROM premises WHERE id IN ({p_ids_str})")
        for r in p_rows:
            p_map[r['id']] = (r['latitude'], r['longitude'])

    # Fetch Store Coords
    s_map = {}
    if store_ids:
        s_ids_str = ",".join(map(str, store_ids))
        s_rows = db.fetch_all(f"SELECT id, latitude, longitude FROM existing_stores WHERE id IN ({s_ids_str})")
        for r in s_rows:
            s_map[r['id']] = (r['latitude'], r['longitude'])

    for p_id, p_coords in p_map.items():
        for s_id, s_coords in s_map.items():
            dist = ((p_coords[0] - s_coords[0])**2 + (p_coords[1] - s_coords[1])**2)**0.5 * 111000

            if dist < 2000:
                query = "INSERT INTO distances (premise_id, store_id, distance_meters) VALUES (%s, %s, %s)"
                db.execute_query(query, (p_id, s_id, dist))

def main():
    create_database_if_not_exists()

    db = Database(DB_CONFIG)
    if db.connect():
        execute_schema(db, 'schema.sql')

        # Optional: Clean up before seeding if you want fresh data every time
        # db.execute_query("SET FOREIGN_KEY_CHECKS = 0")
        # db.execute_query("TRUNCATE TABLE distances")
        # db.execute_query("TRUNCATE TABLE existing_stores")
        # db.execute_query("TRUNCATE TABLE demographics")
        # db.execute_query("TRUNCATE TABLE location_factors")
        # db.execute_query("TRUNCATE TABLE premises")
        # db.execute_query("TRUNCATE TABLE wards")
        # db.execute_query("SET FOREIGN_KEY_CHECKS = 1")

        ward_ids = seed_wards(db)

        csv_file = 'all_convenience_stores_hanoi.csv'
        premise_ids, store_ids = import_from_csv(db, csv_file, ward_ids)

        if premise_ids:
            seed_location_factors(db, premise_ids)
            seed_demographics(db, premise_ids)

        if premise_ids and store_ids:
            seed_distances(db, premise_ids, store_ids)

        print("Seeding completed!")
        db.close()

if __name__ == "__main__":
    main()
