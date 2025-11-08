#!/usr/bin/env python
"""
Script to create users directly on the Render database.
This script connects to the live database and creates/updates users.
"""
import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings')

# Setup Django
django.setup()

# Now import models
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def create_or_update_user(username, password, role, is_superuser=False, is_staff=False):
    """
    Create or update a user with the given credentials.
    """
    try:
        # Try to get existing user
        user = User.objects.get(username=username)
        print(f"\n✓ User '{username}' already exists. Updating...")
        
        # Update password and role
        user.set_password(password)
        user.role = role
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()
        
        print(f"  ✓ Password updated")
        print(f"  ✓ Role set to: {role}")
        if is_superuser:
            print(f"  ✓ Superuser status: True")
        if is_staff:
            print(f"  ✓ Staff status: True")
        
        return user, False
    
    except User.DoesNotExist:
        # Create new user
        print(f"\n✓ Creating new user '{username}'...")
        
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            is_superuser=is_superuser,
            is_staff=is_staff
        )
        
        print(f"  ✓ User created successfully")
        print(f"  ✓ Role set to: {role}")
        if is_superuser:
            print(f"  ✓ Superuser status: True")
        if is_staff:
            print(f"  ✓ Staff status: True")
        
        return user, True

def main():
    """
    Main function to create users.
    """
    print("=" * 60)
    print("ATM Maintenance System - User Creation Script")
    print("=" * 60)
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("\n✓ Database connection successful")
        print(f"  Database: {connection.settings_dict['NAME']}")
        print(f"  Host: {connection.settings_dict['HOST']}")
    except Exception as e:
        print(f"\n✗ Database connection failed: {e}")
        sys.exit(1)
    
    # Create/Update users
    users_config = [
        {
            'username': 'host',
            'password': 'host123',
            'role': 'host',
            'is_superuser': False,
            'is_staff': False,
            'description': 'Host user for Host access'
        },
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'supervisor',
            'is_superuser': True,
            'is_staff': True,
            'description': 'Admin user for Admin dashboard access'
        }
    ]
    
    print("\n" + "=" * 60)
    print("Creating/Updating Users")
    print("=" * 60)
    
    created_count = 0
    updated_count = 0
    
    for config in users_config:
        print(f"\n{config['description']}:")
        user, is_new = create_or_update_user(
            username=config['username'],
            password=config['password'],
            role=config['role'],
            is_superuser=config['is_superuser'],
            is_staff=config['is_staff']
        )
        
        if is_new:
            created_count += 1
        else:
            updated_count += 1
        
        # Print user details
        print(f"\n  User Details:")
        print(f"    ID: {user.id}")
        print(f"    Username: {user.username}")
        print(f"    Role: {user.role}")
        print(f"    Is Superuser: {user.is_superuser}")
        print(f"    Is Staff: {user.is_staff}")
        print(f"    Is Active: {user.is_active}")
        print(f"    Created: {user.date_joined}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Users created: {created_count}")
    print(f"✓ Users updated: {updated_count}")
    print(f"✓ Total users in database: {User.objects.count()}")
    
    print("\n" + "=" * 60)
    print("User Creation Complete!")
    print("=" * 60)
    print("\nYou can now login with:")
    print("  • Username: host, Password: host123 (Host role)")
    print("  • Username: admin, Password: admin123 (Admin/Supervisor role)")

if __name__ == '__main__':
    main()
