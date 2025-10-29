# Feature 2.4 - Manual Browser Testing Checklist

**Test Date**: October 22, 2025  
**Tester**: _______________  
**Browser**: _______________

## Pre-Test Setup ✅

- [x] Backend server running on `http://127.0.0.1:8000/`
- [x] Frontend server running on `http://localhost:3000/`
- [x] Test users created (test_host, test_tech_riyadh, test_tech_jeddah, test_tech_dammam)
- [ ] Test Excel file prepared

## Test Excel File

Create a file named `test_devices.xlsx` with these exact columns and data:

| Interaction ID | Gfm cost Center | Status | Gfm Problem Type | Gfm Problem Date |
|----------------|-----------------|--------|------------------|------------------|
| ATM-TEST-001 | CC-10001 | Central Region | Cleaning Required | 2025-01-20 |
| ATM-TEST-002 | CC-10002 | North Region | Maintenance Due | 2025-01-21 |
| ATM-TEST-003 | CC-10003 | South Region | Inspection Needed | 2025-01-22 |
| ATM-TEST-004 | CC-10004 | East Region | Repair Required | 2025-01-23 |
| ATM-TEST-005 | CC-10005 | West Region | Cleaning Required | 2025-01-24 |

---

## TEST 1: Login and Navigation

### Steps:
1. [ ] Open browser and go to: `http://localhost:3000/login`
2. [ ] Enter username: `test_host`
3. [ ] Enter password: `testpass123`
4. [ ] Click "Login" button

### Expected Results:
- [ ] Login successful
- [ ] Redirected to dashboard
- [ ] No console errors

### Steps (continued):
5. [ ] Navigate to: `http://localhost:3000/upload-excel`

### Expected Results:
- [ ] Excel upload page loads
- [ ] Page title shows "Upload Device Excel File"
- [ ] No console errors

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 2: UI Components Verification

### Check these elements are present:

- [ ] Page header with title "Upload Device Excel File"
- [ ] Description text below title
- [ ] Yellow warning banner with icon
- [ ] Warning text: "This will replace all existing devices for this technician"
- [ ] Technician dropdown label: "Select Technician *"
- [ ] Technician dropdown with placeholder "-- Select a technician --"
- [ ] Device Type dropdown label: "Device Type *"
- [ ] Device Type dropdown with options: Cleaning, Electrical
- [ ] File upload area with drag-and-drop zone
- [ ] Upload icon in file area
- [ ] Text: "Click to upload or drag and drop"
- [ ] Text: "Excel files only (.xlsx, .xls)"
- [ ] Upload button: "Upload Excel File"
- [ ] Upload button is disabled (gray)

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 3: Technician Dropdown

### Steps:
1. [ ] Click on "Select Technician" dropdown

### Expected Results:
- [ ] Dropdown opens
- [ ] Shows at least 3 technicians:
  - [ ] test_tech_riyadh - Riyadh
  - [ ] test_tech_jeddah - Jeddah
  - [ ] test_tech_dammam - Dammam
- [ ] Technicians are formatted as "username - city"

### Steps (continued):
2. [ ] Select "test_tech_riyadh - Riyadh"

### Expected Results:
- [ ] Selection is saved
- [ ] Upload button still disabled

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 4: Device Type Dropdown

### Steps:
1. [ ] Click on "Device Type" dropdown

### Expected Results:
- [ ] Dropdown opens
- [ ] Shows two options:
  - [ ] Cleaning
  - [ ] Electrical

### Steps (continued):
2. [ ] Select "Cleaning"

### Expected Results:
- [ ] Selection is saved
- [ ] Upload button still disabled (no file selected yet)

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 5: File Upload - Click Method

### Steps:
1. [ ] Click on the file upload area

### Expected Results:
- [ ] File picker dialog opens

### Steps (continued):
2. [ ] Select your `test_devices.xlsx` file
3. [ ] Click "Open"

### Expected Results:
- [ ] File is selected
- [ ] Upload area shows:
  - [ ] Green document icon
  - [ ] File name: "test_devices.xlsx"
  - [ ] File size in KB
  - [ ] "Remove file" button
- [ ] Upload button is now enabled (blue)

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 6: File Removal

### Steps:
1. [ ] Click "Remove file" button

### Expected Results:
- [ ] File is removed
- [ ] Upload area returns to initial state
- [ ] Shows upload icon and instructions
- [ ] Upload button is disabled again

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 7: Drag-and-Drop Upload

### Steps:
1. [ ] Drag `test_devices.xlsx` file over the upload area

### Expected Results:
- [ ] Upload area background changes to blue
- [ ] Border color changes

### Steps (continued):
2. [ ] Drop the file

### Expected Results:
- [ ] File is selected
- [ ] Shows file name and size
- [ ] Upload button is enabled

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 8: Invalid File Type

### Steps:
1. [ ] Remove current file if any
2. [ ] Try to select a `.txt` or `.pdf` file

### Expected Results:
- [ ] Error message appears (red box)
- [ ] Message: "Please select a valid Excel file (.xlsx or .xls)"
- [ ] File is not selected
- [ ] Upload button remains disabled

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 9: Form Validation

### Steps:
1. [ ] Clear all selections (refresh page if needed)
2. [ ] Try clicking "Upload Excel File" button

### Expected Results:
- [ ] Button is disabled, cannot click

### Steps (continued):
3. [ ] Select only technician
4. [ ] Check upload button

### Expected Results:
- [ ] Button still disabled

### Steps (continued):
5. [ ] Select device type (but no file)
6. [ ] Check upload button

### Expected Results:
- [ ] Button still disabled

### Steps (continued):
7. [ ] Select file
8. [ ] Check upload button

### Expected Results:
- [ ] Button is now enabled

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 10: Successful Upload

### Steps:
1. [ ] Ensure all fields are filled:
   - Technician: test_tech_riyadh
   - Device Type: Cleaning
   - File: test_devices.xlsx
2. [ ] Click "Upload Excel File" button

### Expected Results During Upload:
- [ ] Button shows loading spinner
- [ ] Button text changes to "Uploading..."
- [ ] Button is disabled during upload

### Expected Results After Upload:
- [ ] Success message appears (green box with checkmark)
- [ ] Message shows: "Upload Successful!"
- [ ] Shows: "5 devices imported for test_tech_riyadh (Riyadh)"
- [ ] Form is reset:
  - [ ] Technician dropdown cleared
  - [ ] Device type dropdown cleared
  - [ ] File removed

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 11: Import Summary Display

### After successful upload, verify:

#### Statistics Cards:
- [ ] Three colored cards displayed
- [ ] Blue card: "Total Devices" with number 5
- [ ] Green card: "Technician" with "test_tech_riyadh"
- [ ] Purple card: "Device Type" with "Cleaning"

#### Device Preview Table:
- [ ] Table header shows: "Imported Devices (showing first 10)"
- [ ] Table has 5 columns:
  - [ ] Interaction ID
  - [ ] Cost Center
  - [ ] Region
  - [ ] Problem Type
  - [ ] Problem Date
- [ ] Table shows 5 rows of data
- [ ] Data matches Excel file:
  - [ ] ATM-TEST-001 | CC-10001 | Central Region | Cleaning Required | 2025-01-20
  - [ ] ATM-TEST-002 | CC-10002 | North Region | Maintenance Due | 2025-01-21
  - [ ] ATM-TEST-003 | CC-10003 | South Region | Inspection Needed | 2025-01-22
  - [ ] ATM-TEST-004 | CC-10004 | East Region | Repair Required | 2025-01-23
  - [ ] ATM-TEST-005 | CC-10005 | West Region | Cleaning Required | 2025-01-24
- [ ] Rows have hover effect (background changes on mouse over)

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 12: REPLACE Strategy

### Steps:
1. [ ] Upload the same file again for test_tech_riyadh
2. [ ] This time select device type: "Electrical"
3. [ ] Click upload

### Expected Results:
- [ ] Upload successful
- [ ] Success message shows "5 devices imported"
- [ ] Device Type card now shows "Electrical"
- [ ] Old "Cleaning" devices were replaced

### Verification:
4. [ ] Check that only Electrical devices exist for this technician
   (Old Cleaning devices should be gone)

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 13: Multiple Technicians

### Steps:
1. [ ] Upload devices for test_tech_jeddah
   - Select: test_tech_jeddah - Jeddah
   - Device Type: Cleaning
   - File: test_devices.xlsx
2. [ ] Click upload

### Expected Results:
- [ ] Upload successful
- [ ] Shows "5 devices imported for test_tech_jeddah (Jeddah)"
- [ ] Technician card shows "test_tech_jeddah"

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 14: Error Handling - Missing Columns

### Steps:
1. [ ] Create an Excel file with wrong column names
2. [ ] Try to upload it

### Expected Results:
- [ ] Error message appears (red box)
- [ ] Message describes missing columns
- [ ] No devices created

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 15: Responsive Design

### Steps:
1. [ ] Resize browser window to mobile size (375px width)

### Expected Results:
- [ ] Layout adapts to mobile
- [ ] All elements remain accessible
- [ ] Text is readable
- [ ] Buttons are clickable
- [ ] No horizontal scrolling

### Steps (continued):
2. [ ] Resize to tablet size (768px width)

### Expected Results:
- [ ] Layout looks good
- [ ] Statistics cards stack appropriately

### Steps (continued):
3. [ ] Resize to desktop size (1920px width)

### Expected Results:
- [ ] Layout uses available space well
- [ ] Content is centered with max-width

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 16: Browser Console

### Throughout all tests:
- [ ] No JavaScript errors in console
- [ ] No network errors (except expected validation errors)
- [ ] No React warnings

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 17: Network Tab Verification

### Check Network tab during upload:

- [ ] Request to `/api/host/technicians/` (GET)
  - [ ] Status: 200 OK
  - [ ] Returns array of technicians
- [ ] Request to `/api/host/upload-excel` (POST)
  - [ ] Status: 201 Created
  - [ ] Content-Type: multipart/form-data
  - [ ] Includes: file, technician_id, device_type
  - [ ] Response includes: total_imported, technician, devices

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## TEST 18: Accessibility

### Keyboard Navigation:
1. [ ] Tab through all form elements
2. [ ] Can select technician with keyboard
3. [ ] Can select device type with keyboard
4. [ ] Can trigger file upload with Enter key
5. [ ] Can submit form with Enter key

### Screen Reader (if available):
- [ ] Labels are announced correctly
- [ ] Error messages are announced
- [ ] Success messages are announced

**Result**: ☐ PASS  ☐ FAIL  
**Notes**: _______________________________________________

---

## FINAL SUMMARY

### Tests Passed: _____ / 18

### Critical Issues Found:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Minor Issues Found:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Overall Assessment:
☐ Ready for Production  
☐ Needs Minor Fixes  
☐ Needs Major Fixes  

### Tester Signature: _______________  
### Date Completed: _______________

---

## Next Steps

If all tests pass:
- [ ] Update `report_feature_2.4.md` with test results
- [ ] Mark Feature 2.4 as COMPLETE
- [ ] Proceed to Feature 2.5: Data Host Dashboard Layout

If issues found:
- [ ] Document all issues
- [ ] Prioritize fixes
- [ ] Re-test after fixes
