"""
FIX: Create test users in the database
This script creates the three test users needed for the system.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')
django.setup()

from core.models import User

print("=" * 80)
print("CREATING TEST USERS")
print("=" * 80)

# Define test users
test_users = [
    {
        'username': 'admin',
        'password': 'admin123',
        'role': 'supervisor',
        'city': None,
        'email': 'admin@atm.com',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'technician1',
        'password': 'tech123',
        'role': 'technician',
        'city': 'Riyadh',
        'email': 'tech1@atm.com',
        'is_staff': False,
        'is_superuser': False
    },
    {
        'username': 'host',
        'password': 'host123',
        'role': 'host',
        'city': None,
        'email': 'host@atm.com',
        'is_staff': False,
        'is_superuser': False
    }
]

# Create users
for user_data in test_users:
    username = user_data['username']
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"⚠️  User '{username}' already exists. Skipping...")
        continue
    
    # Create user
    try:
        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            role=user_data['role'],
            city=user_data['city'],
            is_staff=user_data['is_staff'],
            is_superuser=user_data['is_superuser'],
            is_active=True
        )
        print(f"✅ Created user: {username}")
        print(f"   Role: {user.role}")
        print(f"   City: {user.city}")
        print(f"   Active: {user.is_active}")
    except Exception as e:
        print(f"❌ Error creating user '{username}': {e}")

# Verify users were created
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

total_users = User.objects.count()
print(f"\nTotal users in database: {total_users}")

if total_users > 0:
    print("\nUser details:")
    for user in User.objects.all():
        print(f"  - {user.username} | Role: {user.role} | Active: {user.is_active}")
    print("\n✅ SUCCESS: Test users created successfully!")
else:
    print("\n❌ FAILED: No users were created!")

print("=" * 80)
