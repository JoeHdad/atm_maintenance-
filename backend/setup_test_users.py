#!/usr/bin/env python
"""Quick script to create test users for Feature 2.4 testing"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import User

print("Creating test users...")

# Create Data Host
host, created = User.objects.get_or_create(
    username='test_host',
    defaults={'role': 'host'}
)
host.set_password('testpass123')
host.save()
print(f"{'✓ Created' if created else '✓ Updated'} Data Host: test_host")

# Create Technicians
cities = [
    ('test_tech_riyadh', 'Riyadh'),
    ('test_tech_jeddah', 'Jeddah'),
    ('test_tech_dammam', 'Dammam'),
]

for username, city in cities:
    tech, created = User.objects.get_or_create(
        username=username,
        defaults={'role': 'technician', 'city': city}
    )
    tech.set_password('testpass123')
    tech.save()
    print(f"{'✓ Created' if created else '✓ Updated'} Technician: {username} ({city})")

print("\n✅ Test users ready!")
print("\nLogin credentials:")
print("  Data Host: username='test_host', password='testpass123'")
print("  Technicians: password='testpass123' for all")
