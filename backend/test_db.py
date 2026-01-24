import psycopg2
import os

url = "postgresql://atm_db_tf06_user:b8CPIvk5erg1DMJGtNBWAOVRZ3GurjjF@dpg-d46r4vidbo4c739fhos0-a.frankfurt-postgres.render.com/atm_db_tf06"
try:
    conn = psycopg2.connect(url)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
