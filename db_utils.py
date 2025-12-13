import mysql.connector
import pandas as pd

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='test',  
            password='123456', # Empty password based on usual defaults if prompt one failed. 
                         # User said "123456" failed. I'll stick to '123456' but user might need to fix. 
                         # Wait, I shouldn't guess. I'll use the one provided or leave as is.
                         # Actually, I'll keep '123456' as placeholder, but if it fails app logs it.
            database='convenience_store_db'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def fetch_districts():
    """Fetches all districts."""
    conn = get_db_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM districts")
        districts = cursor.fetchall()
        conn.close()
        return districts
    except Exception as e:
        print(f"Error fetching districts: {e}")
        return []

def fetch_wards(district_id=None):
    """Fetches wards, optionally filtered by district."""
    conn = get_db_connection()
    if conn is None: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, district_id FROM wards"
        params = ()
        if district_id:
            query += " WHERE district_id = %s"
            params = (district_id,)
        cursor.execute(query, params)
        wards = cursor.fetchall()
        conn.close()
        return wards
    except Exception as e:
        print(f"Error fetching wards: {e}")
        return []

def fetch_location_data(max_price=None, district_id=None, ward_id=None):
    """
    Fetches and aggregates data for decision making with filters.
    :param max_price: Filter shops with price <= max_price.
    :param district_id: Filter by district.
    :param ward_id: Filter by ward.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    # Base query
    query = """
    SELECT 
        r.id AS shop_id,
        r.address,
        r.price,                 
        r.area,                  
        r.frontage,              
        o.foot_traffic,          
        o.employee_cost,         
        o.utilities_cost,        
        IFNULL(MIN(sod.distance_km), 0) AS min_opponent_dist
    FROM rental_shops r
    JOIN other_factors o ON r.id = o.rental_shop_id
    LEFT JOIN shop_opponent_distances sod ON r.id = sod.shop_id
    LEFT JOIN wards w ON r.ward_id = w.id
    WHERE 1=1
    """
    
    params = []
    
    if max_price is not None and max_price > 0:
        query += " AND r.price <= %s"
        params.append(max_price)
        
    if ward_id is not None and ward_id != "":
        query += " AND r.ward_id = %s"
        params.append(ward_id)
    elif district_id is not None and district_id != "":
        query += " AND w.district_id = %s"
        params.append(district_id)
        
    query += """
    GROUP BY r.id, r.address, r.price, r.area, r.frontage, o.foot_traffic, o.employee_cost, o.utilities_cost;
    """
    
    try:
        df = pd.read_sql(query, conn, params=tuple(params))
        conn.close()
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.close()
        return None

if __name__ == "__main__":
    # Test connection
    print("Districts:", fetch_districts())
    df = fetch_location_data(max_price=50) # Example filter
    if df is not None:
        print(f"Fetched {len(df)} rows with max price 50.")
    else:
        print("Failed to fetch data.")
