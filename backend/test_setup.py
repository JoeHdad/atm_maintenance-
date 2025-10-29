#!/usr/bin/env python
"""
Setup verification script for ATM Maintenance System
"""
import os
import sys

def test_project_structure():
    """Test project structure"""
    print("Testing project structure...")

    # We're running from backend directory, so adjust paths
    required_dirs = ['.', '../frontend', '../Instructions']  # . is backend
    dir_names = ['backend', 'frontend', 'Instructions']
    for i, dir_name in enumerate(required_dirs):
        assert os.path.exists(dir_name), f"Missing directory: {dir_names[i]}"

    required_files = [
        'manage.py',
        'atm_backend/settings.py',
        'venv/Scripts/activate',  # Windows venv
        '../frontend/atm_frontend/package.json',
        '../frontend/atm_frontend/tailwind.config.js',
        '../Instructions/Stack_Overview.md'
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing file: {file_path}"

    print("Project structure verified")

def test_documentation():
    """Test documentation files"""
    print("Testing documentation...")

    doc_files = [
        '../Instructions/Stack_Overview.md',
        '../Instructions/best-practices.md',
        '../Instructions/security-guidelines.md',
        '../Instructions/database-schema.md',
        '../Instructions/api-endpoints.md'
    ]

    for doc_file in doc_files:
        assert os.path.exists(doc_file), f"Missing documentation: {doc_file}"
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert len(content) > 100, f"Documentation file {doc_file} is too short"

    print("Documentation verified")

def test_django_config():
    """Test Django configuration without loading models"""
    print("Testing Django configuration...")

    # Read settings file
    with open('atm_backend/settings.py', 'r') as f:
        settings_content = f.read()

    # Check for required configurations
    assert 'from decouple import config' in settings_content, "decouple not imported"
    assert 'rest_framework' in settings_content, "DRF not in INSTALLED_APPS"
    assert 'rest_framework_simplejwt' in settings_content, "JWT not in INSTALLED_APPS"
    assert 'corsheaders' in settings_content, "CORS not configured"
    assert 'postgresql' in settings_content, "PostgreSQL not configured"

    print("Django configuration verified")

def test_frontend_config():
    """Test frontend configuration"""
    print("Testing frontend configuration...")

    # Check package.json
    with open('../frontend/atm_frontend/package.json', 'r') as f:
        package_content = f.read()
    assert '"react"' in package_content, "React not in package.json"

    # Check Tailwind config
    with open('../frontend/atm_frontend/tailwind.config.js', 'r') as f:
        tailwind_content = f.read()
    assert 'tailwindcss' in tailwind_content, "Tailwind not configured"

    # Check CSS imports
    with open('../frontend/atm_frontend/src/index.css', 'r') as f:
        css_content = f.read()
    assert '@tailwind base' in css_content, "Tailwind directives not in CSS"

    print("Frontend configuration verified")

if __name__ == '__main__':
    try:
        test_project_structure()
        test_django_config()
        test_frontend_config()
        test_documentation()
        print("\nAll tests passed! Foundation setup is correct.")
        print("\nNext steps:")
        print("1. Copy backend/.env.example to backend/.env and configure your settings")
        print("2. Set up PostgreSQL database")
        print("3. Run 'cd backend && venv\\Scripts\\activate && python manage.py migrate'")
        print("4. Run 'cd frontend/atm_frontend && npm start'")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)