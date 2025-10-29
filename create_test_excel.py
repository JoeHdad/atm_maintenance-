#!/usr/bin/env python
"""Create a test Excel file for Feature 2.4 testing"""

from openpyxl import Workbook
import os

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Devices"

# Add headers
headers = ['Interaction ID', 'Gfm cost Center', 'Status', 'Gfm Problem Type', 'Gfm Problem Date']
ws.append(headers)

# Add test data
test_data = [
    ['ATM-TEST-001', 'CC-10001', 'Central Region', 'Cleaning Required', '2025-01-20'],
    ['ATM-TEST-002', 'CC-10002', 'North Region', 'Maintenance Due', '2025-01-21'],
    ['ATM-TEST-003', 'CC-10003', 'South Region', 'Inspection Needed', '2025-01-22'],
    ['ATM-TEST-004', 'CC-10004', 'East Region', 'Repair Required', '2025-01-23'],
    ['ATM-TEST-005', 'CC-10005', 'West Region', 'Cleaning Required', '2025-01-24'],
]

for row in test_data:
    ws.append(row)

# Save file
output_path = os.path.join(os.path.dirname(__file__), 'test_devices.xlsx')
wb.save(output_path)

print(f"✅ Test Excel file created: {output_path}")
print(f"\nFile contains:")
print(f"  - 5 columns: {', '.join(headers)}")
print(f"  - 5 data rows")
print(f"\nUse this file for manual testing of Feature 2.4")
