# Feature 2.4 Testing Guide

## Test Status: READY FOR MANUAL TESTING

Feature 2.4 (Excel Upload UI) has been fully implemented. The backend API endpoints are ready and the frontend component is complete.

## Prerequisites

### 1. Servers Running
- **Backend**: `http://127.0.0.1:8000/` ✅ (Currently running)
- **Frontend**: `http://localhost:3000/` ✅ (Should be running)

### 2. Test Users Created

Run this command to create test users:
```bash
cd backend
.\venv\Scripts\python.exe -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atm_backend.settings'); django.setup(); from core.models import User; host, _ = User.objects.get_or_create(username='test_host', defaults={'role': 'host'}); host.set_password('testpass123'); host.save(); tech1, _ = User.objects.get_or_create(username='test_tech_riyadh', defaults={'role': 'technician', 'city': 'Riyadh'}); tech1.set_password('testpass123'); tech1.save(); tech2, _ = User.objects.get_or_create(username='test_tech_jeddah', defaults={'role': 'technician', 'city': 'Jeddah'}); tech2.set_password('testpass123'); tech2.save(); print('✓ Test users created')"
```

**Test Users:**
- **Data Host**: username=`test_host`, password=`testpass123`
- **Technician 1**: username=`test_tech_riyadh`, password=`testpass123`, city=Riyadh
- **Technician 2**: username=`test_tech_jeddah`, password=`testpass123`, city=Jeddah

### 3. Test Excel File

Create a file named `test_devices.xlsx` with these columns:

| Interaction ID | Gfm cost Center | Status | Gfm Problem Type | Gfm Problem Date |
|----------------|-----------------|--------|------------------|------------------|
| ATM-TEST-001 | CC-10001 | Central Region | Cleaning Required | 2025-01-20 |
| ATM-TEST-002 | CC-10002 | North Region | Maintenance Due | 2025-01-21 |
| ATM-TEST-003 | CC-10003 | South Region | Inspection Needed | 2025-01-22 |

Or download a sample from the backend test script.

## Manual Testing Steps

### Test 1: Login and Navigation ✅

1. Open browser: `http://localhost:3000/login`
2. Login with:
   - Username: `test_host`
   - Password: `testpass123`
3. Navigate to: `http://localhost:3000/upload-excel`
4. **Expected**: Excel upload page loads successfully

### Test 2: UI Components ✅

**Verify these elements are present:**
- [ ] Page title: "Upload Device Excel File"
- [ ] Warning banner (yellow): "This will replace all existing devices..."
- [ ] Technician dropdown (should show test_tech_riyadh, test_tech_jeddah)
- [ ] Device Type dropdown (Cleaning, Electrical)
- [ ] File upload area with drag-and-drop zone
- [ ] Upload button (should be disabled initially)

### Test 3: Form Validation ✅

1. Try clicking "Upload Excel File" without selecting anything
2. **Expected**: Button is disabled
3. Select a technician
4. **Expected**: Button still disabled
5. Select device type
6. **Expected**: Button still disabled
7. Select a file
8. **Expected**: Button becomes enabled

### Test 4: File Validation ✅

1. Try uploading a `.txt` file
2. **Expected**: Error message: "Please select a valid Excel file (.xlsx or .xls)"
3. Try uploading a `.xlsx` file
4. **Expected**: File accepted, name and size displayed

### Test 5: Drag and Drop ✅

1. Drag an Excel file over the upload area
2. **Expected**: Upload area changes color (blue background)
3. Drop the file
4. **Expected**: File is selected, details shown

### Test 6: Successful Upload ✅

1. Select technician: `test_tech_riyadh`
2. Select device type: `Cleaning`
3. Upload the test Excel file
4. Click "Upload Excel File"
5. **Expected**:
   - Loading spinner appears
   - Success message displays
   - Shows "X devices imported for test_tech_riyadh (Riyadh)"
   - Import summary section appears with:
     - Total Devices card (blue)
     - Technician card (green)
     - Device Type card (purple)
   - Device preview table shows first 10 devices
   - Form resets (dropdowns cleared, file removed)

### Test 7: REPLACE Strategy ✅

1. Upload the same file again for the same technician
2. Select device type: `Electrical` (different from first upload)
3. Upload
4. **Expected**:
   - Old devices are replaced
   - New devices are created with type "Electrical"
   - Success message shows correct count

### Test 8: Error Handling ✅

**Test Invalid File:**
1. Create an Excel file with wrong columns
2. Try to upload
3. **Expected**: Error message with details about missing columns

**Test Missing Data:**
1. Create an Excel file with empty cells
2. Try to upload
3. **Expected**: Error message specifying which rows have issues

### Test 9: Multiple Technicians ✅

1. Upload devices for `test_tech_riyadh`
2. Upload different devices for `test_tech_jeddah`
3. **Expected**: Each technician gets their own devices

### Test 10: Responsive Design ✅

1. Resize browser window to mobile size
2. **Expected**: Layout adapts, remains usable
3. Test on tablet size
4. **Expected**: Layout looks good

## API Endpoint Testing

### Test GET /api/host/technicians/

```bash
# Get JWT token first
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test_host","password":"testpass123"}'

# Use the token to get technicians
curl -X GET http://127.0.0.1:8000/api/host/technicians/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "username": "test_tech_riyadh",
    "role": "technician",
    "city": "Riyadh"
  },
  {
    "id": 2,
    "username": "test_tech_jeddah",
    "role": "technician",
    "city": "Jeddah"
  }
]
```

### Test POST /api/host/upload-excel

```bash
curl -X POST http://127.0.0.1:8000/api/host/upload-excel \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test_devices.xlsx" \
  -F "technician_id=1" \
  -F "device_type=Cleaning"
```

**Expected Response:**
```json
{
  "total_imported": 3,
  "technician": {
    "id": 1,
    "username": "test_tech_riyadh",
    "city": "Riyadh"
  },
  "device_type": "Cleaning",
  "devices": [...]
}
```

## Test Results Checklist

### Backend API
- [ ] GET /api/host/technicians/ returns technician list
- [ ] POST /api/host/upload-excel accepts Excel file
- [ ] File validation works (rejects non-Excel files)
- [ ] Excel parsing works correctly
- [ ] Devices are created in database
- [ ] REPLACE strategy works (old devices deleted)
- [ ] Error messages are clear and helpful

### Frontend UI
- [ ] Page loads without errors
- [ ] Technicians dropdown populates
- [ ] Device type dropdown works
- [ ] File upload (click) works
- [ ] Drag-and-drop works
- [ ] Form validation works
- [ ] Upload button disabled/enabled correctly
- [ ] Loading spinner shows during upload
- [ ] Success message displays
- [ ] Import summary shows correct data
- [ ] Device preview table displays
- [ ] Form resets after success
- [ ] Error messages display correctly
- [ ] Warning message is visible
- [ ] Responsive on mobile/tablet

### Integration
- [ ] Frontend successfully calls backend APIs
- [ ] JWT authentication works
- [ ] File upload with FormData works
- [ ] Success response is parsed correctly
- [ ] Error response is handled correctly

## Known Issues

None at this time. All features implemented according to Phase 2 specifications.

## Next Steps

After successful testing of Feature 2.4:
1. Document test results
2. Update report_feature_2.4.md with test results
3. Proceed to Feature 2.5: Data Host Dashboard Layout

## Troubleshooting

### Frontend not loading
- Check if `npm start` is running
- Check browser console for errors
- Verify React Router configuration

### Technicians not showing in dropdown
- Check backend server is running
- Check JWT token is valid
- Check browser Network tab for API errors
- Verify GET /api/host/technicians/ endpoint works

### Upload fails
- Check file is valid Excel (.xlsx or .xls)
- Check backend server is running
- Check browser console and Network tab
- Verify technician_id and device_type are selected

### CORS errors
- Verify CORS settings in backend settings.py
- Check ALLOWED_HOSTS includes localhost

## Success Criteria

Feature 2.4 is considered successfully tested when:
- ✅ All UI components render correctly
- ✅ Technicians load from API
- ✅ File upload works (both click and drag-drop)
- ✅ Excel file is parsed and devices created
- ✅ Success message and summary display correctly
- ✅ REPLACE strategy confirmed working
- ✅ Error handling works for all scenarios
- ✅ Responsive design works on all screen sizes
- ✅ No console errors
- ✅ No network errors

---

**Test Date**: October 22, 2025  
**Tester**: [Your Name]  
**Status**: PENDING MANUAL TESTING
