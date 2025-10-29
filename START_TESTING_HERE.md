# 🧪 START MANUAL TESTING - Feature 2.4

## ✅ Pre-Test Checklist

All prerequisites are ready:
- ✅ Backend server running on `http://127.0.0.1:8000/`
- ✅ Frontend server running on `http://localhost:3000/`
- ✅ Test users created
- ✅ Test Excel file created: `test_devices.xlsx`

## 🚀 Quick Start (5 Minutes)

### Step 1: Login
1. Open browser: **`http://localhost:3000/login`**
2. Username: **`test_host`**
3. Password: **`testpass123`**
4. Click **Login**

### Step 2: Navigate to Upload Page
1. Go to: **`http://localhost:3000/upload-excel`**
2. Verify page loads with title "Upload Device Excel File"

### Step 3: Upload Test File
1. **Select Technician**: Choose "test_tech_riyadh - Riyadh"
2. **Select Device Type**: Choose "Cleaning"
3. **Upload File**: Click upload area and select `test_devices.xlsx`
   - File location: `C:\Users\ahmed\OneDrive\Desktop\VIBE CODING\Windsurf\atm-maintenance-system\test_devices.xlsx`
4. Click **"Upload Excel File"** button

### Step 4: Verify Success
✅ **You should see:**
- Green success message: "Upload Successful!"
- "5 devices imported for test_tech_riyadh (Riyadh)"
- Statistics cards (Total Devices, Technician, Device Type)
- Device preview table with 5 rows

### Step 5: Test REPLACE Strategy
1. Upload the same file again for the same technician
2. This time select device type: **"Electrical"**
3. Verify old devices are replaced with new ones

---

## 📋 Full Testing Checklist

For comprehensive testing, use: **`MANUAL_TEST_CHECKLIST.md`**

This includes 18 detailed test cases covering:
- UI components
- Form validation
- File upload (click & drag-drop)
- Success/error handling
- REPLACE strategy
- Multiple technicians
- Responsive design
- Accessibility

---

## 🔑 Test Credentials

### Data Host (for upload page)
- Username: `test_host`
- Password: `testpass123`

### Technicians (for testing different uploads)
- `test_tech_riyadh` (Riyadh) - password: `testpass123`
- `test_tech_jeddah` (Jeddah) - password: `testpass123`
- `test_tech_dammam` (Dammam) - password: `testpass123`

---

## 📁 Test File

**Location**: `test_devices.xlsx` (in project root)

**Contents**: 5 devices with columns:
- Interaction ID
- Gfm cost Center
- Status (Region)
- Gfm Problem Type
- Gfm Problem Date

---

## ✨ What to Look For

### ✅ Good Signs
- Technicians load in dropdown automatically
- File upload works (both click and drag-drop)
- Upload button enables/disables correctly
- Loading spinner shows during upload
- Success message displays with correct data
- Device preview table shows all devices
- Form resets after successful upload
- No console errors

### ❌ Issues to Report
- Technicians don't load
- File upload doesn't work
- Upload fails with error
- Success message doesn't show
- Device table is empty or wrong
- Console errors appear
- Page layout broken

---

## 🐛 Troubleshooting

### Technicians dropdown is empty
- Check backend server is running
- Check browser console for errors
- Try refreshing the page

### Upload fails
- Verify file is `.xlsx` format
- Check all fields are selected
- Check browser Network tab for errors

### Page doesn't load
- Verify frontend server is running on port 3000
- Check you're logged in as Data Host user
- Clear browser cache and try again

---

## 📊 Expected Test Results

### Test Duration
- Quick test: **5 minutes**
- Full test: **30-45 minutes**

### Success Criteria
- All 18 test cases pass
- No critical bugs found
- UI is responsive and user-friendly
- All features work as specified

---

## 📝 After Testing

### If All Tests Pass ✅
1. Mark tests as complete in `MANUAL_TEST_CHECKLIST.md`
2. Update `report_feature_2.4.md` with results
3. Feature 2.4 is COMPLETE
4. Ready to proceed to Feature 2.5

### If Issues Found ❌
1. Document issues in checklist
2. Note severity (Critical/Major/Minor)
3. Report to development team
4. Re-test after fixes

---

## 🎯 Focus Areas

### High Priority
1. **File Upload** - Must work reliably
2. **Technician Selection** - Must load from API
3. **Success Feedback** - Must show correct data
4. **REPLACE Strategy** - Must delete old devices

### Medium Priority
1. **Drag-and-Drop** - Nice to have, click upload is fallback
2. **Error Messages** - Should be clear and helpful
3. **Responsive Design** - Should work on mobile

### Low Priority
1. **Animations** - Smooth transitions
2. **Hover Effects** - Visual feedback
3. **Loading States** - Professional appearance

---

## 🚀 Ready to Start?

1. ✅ Open `http://localhost:3000/login`
2. ✅ Login as `test_host` / `testpass123`
3. ✅ Navigate to `http://localhost:3000/upload-excel`
4. ✅ Follow the Quick Start steps above
5. ✅ Use `MANUAL_TEST_CHECKLIST.md` for detailed testing

**Good luck with testing! 🎉**
