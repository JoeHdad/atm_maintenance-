# Device Type Excel Upload - Debug Guide

## Issue Description
When uploading two Excel files (one for Cleaning and one for Electrical), the system only recognizes the Cleaning file. Even when selecting Electrical, it shows Cleaning data.

## Debug Logging Added

### Frontend Logging
1. **ExcelUpload Component** (`ExcelUpload.jsx`):
   - `[UPLOAD]` - Tracks file upload with device type
   - `[FETCH_TYPES]` - Tracks fetching uploaded types

2. **DeviceList Component** (`DeviceList.jsx`):
   - `[FRONTEND]` - Tracks Excel data fetching by device type

3. **API Calls** (`host.js` and `technician.js`):
   - `[API]` - Tracks all API requests and responses

### Backend Logging
1. **Upload Endpoint** (`views.py` - `upload_excel`):
   - `[UPLOAD DEBUG]` - Tracks device_type during upload
   - Shows if creating new or updating existing upload

2. **Get Uploaded Types** (`views.py` - `get_uploaded_types`):
   - `[GET_TYPES DEBUG]` - Shows all uploads and their device types

3. **Get Excel Data by Type** (`views.py` - `get_excel_data_by_type`):
   - `[RETRIEVAL DEBUG]` - Detailed comparison of device types
   - Shows all uploads and which one matches

## Testing Steps

### Step 1: Clear Previous Data (Optional)
Run the debug script to see current state:
```bash
cd backend
python debug_excel_uploads.py
```

### Step 2: Upload First File (Cleaning1)
1. Open browser console (F12)
2. Login as Host
3. Navigate to Excel Upload page
4. Select a technician
5. Select "Cleaning1" from device type dropdown
6. Upload an Excel file

**Watch for these logs:**
- Frontend: `[UPLOAD] Uploading file for device type: Cleaning1`
- Backend: `[UPLOAD DEBUG] Creating new upload for device_type: Cleaning1`
- Backend: `[UPLOAD DEBUG] Created upload with ID: X, device_type: Cleaning1`

### Step 3: Upload Second File (Electrical)
1. Keep the same technician selected
2. Select "Electrical" from device type dropdown
3. Upload a DIFFERENT Excel file

**Watch for these logs:**
- Frontend: `[UPLOAD] Uploading file for device type: Electrical`
- Backend: `[UPLOAD DEBUG] Creating new upload for device_type: Electrical`
- Backend: `[UPLOAD DEBUG] Created upload with ID: Y, device_type: Electrical`

**Important:** The upload ID (Y) should be DIFFERENT from the first upload (X)

### Step 4: Verify Uploaded Types
After uploading both files, refresh the page and select the same technician.

**Watch for these logs:**
- Frontend: `[FETCH_TYPES] Received uploaded types: ['Cleaning1', 'Electrical']`
- Backend: `[GET_TYPES DEBUG] Found uploaded types: ['Cleaning1', 'Electrical']`

### Step 5: Test Technician Page - Cleaning1
1. Login as the technician
2. Navigate to Device List page
3. Select "Cleaning1" from device type filter

**Watch for these logs:**
- Frontend: `[FRONTEND] Fetching Excel data for device type: Cleaning1`
- Frontend: `[API] Calling GET /technician/excel-data/Cleaning1`
- Backend: `[RETRIEVAL DEBUG] Fetching data for device_type: 'Cleaning1'`
- Backend: `[RETRIEVAL DEBUG] Matching uploads for 'Cleaning1': 1`
- Backend: `[RETRIEVAL DEBUG] Returning device_type: 'Cleaning1'`
- Frontend: `[FRONTEND] Device type in response: Cleaning1`
- Frontend: `[FRONTEND] File name: [your Cleaning1 file name]`

### Step 6: Test Technician Page - Electrical
1. Keep logged in as technician
2. Select "Electrical" from device type filter

**Watch for these logs:**
- Frontend: `[FRONTEND] Fetching Excel data for device type: Electrical`
- Frontend: `[API] Calling GET /technician/excel-data/Electrical`
- Backend: `[RETRIEVAL DEBUG] Fetching data for device_type: 'Electrical'`
- Backend: `[RETRIEVAL DEBUG] Matching uploads for 'Electrical': 1`
- Backend: `[RETRIEVAL DEBUG] Returning device_type: 'Electrical'`
- Frontend: `[FRONTEND] Device type in response: Electrical`
- Frontend: `[FRONTEND] File name: [your Electrical file name]`

## What to Look For

### If the issue persists:

1. **Check Upload IDs**: In Step 3, verify that two DIFFERENT upload IDs are created
   - If the same ID appears, the second upload is overwriting the first

2. **Check Device Type Storage**: Look at the backend logs in Step 3
   - Verify `device_type: Electrical` is shown, not `device_type: Cleaning1`

3. **Check Retrieval Matching**: In Step 6, look at the backend logs
   - Check if `match: True` appears for the Electrical upload
   - Check if `match: False` appears for the Cleaning1 upload

4. **Check Response Data**: In Step 6, verify frontend logs show:
   - `Device type in response: Electrical` (not Cleaning1)
   - `File name:` matches the Electrical file you uploaded

## Common Issues

### Issue 1: Same Upload ID for Both Files
**Symptom:** Upload ID in Step 3 is the same as Step 2
**Cause:** Update logic is incorrectly matching uploads
**Solution:** Check the `existing_upload` filter in `views.py`

### Issue 2: Device Type Not Stored
**Symptom:** Backend shows `device_type: None` or wrong type
**Cause:** FormData not sending device_type correctly
**Solution:** Check FormData in browser Network tab

### Issue 3: Wrong Data Retrieved
**Symptom:** Backend shows correct device_type but wrong data
**Cause:** Database has incorrect associations
**Solution:** Run `python debug_excel_uploads.py` to inspect database

### Issue 4: FetchError
**Symptom:** `Uncaught (in promise) FetchError`
**Cause:** API endpoint not found or authentication issue
**Solution:** Check Network tab for 404 or 401 errors

## Database Inspection

Run the debug script anytime to see the current database state:
```bash
cd backend
python debug_excel_uploads.py
```

This will show:
- All technicians
- All uploads for each technician
- Device type for each upload
- File names
- Row counts

## Next Steps

After testing with these logs, report:
1. All console logs from both frontend and backend
2. Output from `debug_excel_uploads.py`
3. Screenshots of the Network tab showing the API calls
4. Specific step where the issue occurs
