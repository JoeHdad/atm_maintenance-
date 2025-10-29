#!/usr/bin/env python
"""Test script to verify openpyxl import"""

try:
    import openpyxl
    print(f"✓ openpyxl successfully imported")
    print(f"  Version: {openpyxl.__version__}")
except ImportError as e:
    print(f"✗ Failed to import openpyxl: {e}")
    exit(1)

try:
    from core.utils.excel_parser import ExcelParser, parse_excel_file
    print(f"✓ excel_parser module successfully imported")
except ImportError as e:
    print(f"✗ Failed to import excel_parser: {e}")
    exit(1)

print("\n✓ All imports successful!")
