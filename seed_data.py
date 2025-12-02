import random
from faker import Faker
from database import Database
import mysql.connector

# Configuration - REPLACE WITH YOUR ACTUAL DB CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'database': 'convenience_store_db',
    'user': 'root',
    'password': 'password'
}

fake = Faker('vi_VN')

def seed_wards(db, count=10):
    print("Seeding Wards...")
    ward_ids = []
    for _ in range(count):
        name = fake.administrative_unit() + " " + fake.first_name() # Mock name
        query = "INSERT INTO wards (name) VALUES (%s)"
        cursor = db.execute_query(query, (name,))
        if cursor:
            ward_ids.append(cursor.lastrowid)
    return ward_ids

def seed_premises(db, ward_ids, count=50):
    print("Seeding Premises...")
    premise_ids = []
    for _ in range(count):
        ward_id = random.choice(ward_ids)
        # Hanoi coordinates approx: 21.0285, 105.8542
        lat = 21.0 + random.uniform(0, 0.1)
        lng = 105.8 + random.uniform(0, 0.1)
        frontage = random.uniform(3.0, 15.0)
        area = frontage * random.uniform(5.0, 20.0) # Approx depth
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
    return premise_ids

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

def seed_existing_stores(db, ward_ids, count=20):
    print("Seeding Existing Stores (Competitors)...")
    store_ids = []
    for _ in range(count):
        ward_id = random.choice(ward_ids)
        lat = 21.0 + random.uniform(0, 0.1)
        lng = 105.8 + random.uniform(0, 0.1)
        name = fake.company()

        query = """
        INSERT INTO existing_stores (ward_id, latitude, longitude, name, store_type)
        VALUES (%s, %s, %s, %s, 'COMPETITOR')
        """
        cursor = db.execute_query(query, (ward_id, lat, lng, name))
        if cursor:
            store_ids.append(cursor.lastrowid)
    return store_ids

def seed_distances(db, premise_ids, store_ids):
    print("Seeding Distances...")
    for p_id in premise_ids:
        # Get Premise coords
        res = db.fetch_all(f"SELECT latitude, longitude FROM premises WHERE id = {p_id}")
        if not res: continue
        p = res[0]

        for s_id in store_ids:
             # Get Store coords
            res_s = db.fetch_all(f"SELECT latitude, longitude FROM existing_stores WHERE id = {s_id}")
            if not res_s: continue
            s = res_s[0]

            # Approx distance in meters
            dist = ((p['latitude'] - s['latitude'])**2 + (p['longitude'] - s['longitude'])**2)**0.5 * 111000

            if dist < 2000: # Only record nearby stores
                query = "INSERT INTO distances (premise_id, store_id, distance_meters) VALUES (%s, %s, %s)"
                db.execute_query(query, (p_id, s_id, dist))

def main():
    db = Database(DB_CONFIG)
    if db.connect():
        ward_ids = seed_wards(db)
        premise_ids = seed_premises(db, ward_ids)
        seed_location_factors(db, premise_ids)
        seed_demographics(db, premise_ids)
        store_ids = seed_existing_stores(db, ward_ids)
        seed_distances(db, premise_ids, store_ids)

        print("Seeding completed!")
        db.close()

if __name__ == "__main__":
    main()
