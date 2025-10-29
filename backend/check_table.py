import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='excel_upload'")
result = cursor.fetchone()

if result:
    print("✅ Table 'excel_upload' EXISTS in database")
else:
    print("❌ Table 'excel_upload' DOES NOT EXIST in database")

# Check migration status
cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app='core' ORDER BY id")
migrations = cursor.fetchall()
print("\nMigrations in database:")
for app, name, applied in migrations:
    print(f"  {app}.{name} - Applied: {applied}")
