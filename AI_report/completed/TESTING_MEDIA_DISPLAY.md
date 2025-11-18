# Media Display Testing Guide

## Overview
This guide provides step-by-step instructions to test the media file display functionality locally before deployment to production (Hostinger + Render).

---

## Prerequisites

### 1. Backend Setup (Django/Render)
- Ensure Django backend is running locally or accessible at `http://localhost:8000`
- Database must have test submissions with photos and PDFs
- Backend should have the following changes applied:
  - ✅ `core/utils/media_url_builder.py` (absolute URL generation)
  - ✅ `core/serializers.py` (PhotoSerializer & SubmissionSerializer with absolute URLs)
  - ✅ `atm_backend/settings.py` (MEDIA_BASE_URL, CORS settings)
  - ✅ `core/views_admin.py` (request context passed to serializers)

### 2. Frontend Setup (React)
- Ensure Node.js and npm are installed
- Navigate to `frontend/atm_frontend` directory
- Install dependencies: `npm install`
- Ensure `.env` file exists with development settings:
  ```
  REACT_APP_API_URL=http://localhost:8000/api
  REACT_APP_ENV=development
  ```

---

## Testing Checklist

### Phase 1: Backend Verification

#### 1.1 Test API Endpoints
Run these commands to verify backend is returning absolute URLs:

```bash
# Test supervisor submissions list (with absolute URLs)
curl -H "Authorization: Bearer <YOUR_TOKEN>" \
  http://localhost:8000/api/supervisor/submissions

# Expected response should include:
# - photos[].file_url: "http://localhost:8000/media/photos/..."
# - pdf_url: "http://localhost:8000/media/pdfs/..."
```

**Verification Points:**
- [ ] API returns HTTP 200
- [ ] All photo URLs are absolute (start with `http://` or `https://`)
- [ ] All PDF URLs are absolute
- [ ] No relative paths like `media/photos/...`

#### 1.2 Test CORS Headers
```bash
# Check CORS headers are present
curl -i -H "Origin: http://localhost:3000" \
  http://localhost:8000/api/supervisor/submissions

# Expected headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
```

**Verification Points:**
- [ ] CORS headers present in response
- [ ] Origin is allowed

---

### Phase 2: Frontend Local Testing

#### 2.1 Start Frontend Dev Server
```bash
cd frontend/atm_frontend
npm start
```

This will open `http://localhost:3000` in your browser.

#### 2.2 Test Supervisor/Admin View (SubmissionDetail.jsx)

**Steps:**
1. Login as supervisor/admin user
2. Navigate to a submission with photos and PDF
3. Open browser DevTools (F12) → Console tab

**Test Cases:**

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| **Images Load** | View submission with photos | All photos display without 404 | ⬜ |
| **Image URLs** | Inspect image `src` in DevTools | URLs are absolute (e.g., `http://localhost:8000/media/...`) | ⬜ |
| **Image Errors** | Check Console tab | No 404 errors for images | ⬜ |
| **CORS Errors** | Check Console tab | No CORS errors | ⬜ |
| **MediaImage Loading** | View photos | Loading skeleton appears briefly | ⬜ |
| **MediaImage Error** | Simulate broken URL | Fallback error message displays | ⬜ |
| **PDF Preview** | Click "View PDF Preview" button | PDF opens in new tab without errors | ⬜ |
| **PDF URL** | Check Network tab | PDF request goes to `http://localhost:8000/media/pdfs/...` | ⬜ |
| **Modal Images** | Click on photo to open modal | Full-size image displays correctly | ⬜ |
| **Modal Close** | Press ESC or click outside | Modal closes properly | ⬜ |

**Console Checks:**
```javascript
// Run in browser console to verify URLs:
// Check if images have absolute URLs
document.querySelectorAll('img').forEach(img => {
  console.log('Image URL:', img.src);
  console.log('Is Absolute:', img.src.startsWith('http'));
});

// Check for any 404 errors
console.log('Network errors:', performance.getEntriesByType('resource')
  .filter(r => r.transferSize === 0 && r.name.includes('media')));
```

#### 2.3 Test Supervisor/Admin View (SubmissionList.jsx)

**Steps:**
1. Login as supervisor/admin
2. Navigate to submissions list
3. Open browser DevTools → Network tab

**Test Cases:**

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| **List Loads** | View submissions list | All submissions display | ⬜ |
| **API Call** | Check Network tab | GET `/api/supervisor/submissions` returns 200 | ⬜ |
| **Absolute URLs** | Inspect response in Network tab | All URLs in response are absolute | ⬜ |
| **Filter Works** | Apply device type filter | Submissions filter correctly | ⬜ |
| **Status Filter** | Apply status filter | Submissions filter correctly | ⬜ |
| **No Console Errors** | Check Console tab | No errors or warnings | ⬜ |

#### 2.4 Test Technician View (if applicable)

**Steps:**
1. Login as technician user
2. Navigate to device details or submission view
3. Check if any media is displayed

**Test Cases:**

| Test Case | Steps | Expected Result | Status |
|-----------|-------|-----------------|--------|
| **Device Page Loads** | View device page | Page loads without errors | ⬜ |
| **Submission History** | View past submissions | Submissions display correctly | ⬜ |
| **Media Display** | Check if photos/PDFs visible | Media displays using absolute URLs | ⬜ |
| **No CORS Errors** | Check Console | No CORS errors | ⬜ |

---

### Phase 3: Network Inspection

#### 3.1 Check Network Tab (DevTools)

**Steps:**
1. Open DevTools → Network tab
2. Reload page
3. Filter by "media" or "img"

**Verification Points:**
- [ ] All media requests show status 200 (not 404)
- [ ] All media URLs are to `http://localhost:8000/media/...`
- [ ] No failed requests
- [ ] Response headers include `Content-Type: image/...` or `application/pdf`

#### 3.2 Check Console for Errors

**Steps:**
1. Open DevTools → Console tab
2. Look for any red error messages

**Expected:**
- [ ] No 404 errors for media files
- [ ] No CORS errors
- [ ] No `TypeError` or `ReferenceError` related to media
- [ ] Only info/warning logs (if any)

---

### Phase 4: Cross-Domain Testing (Simulated Production)

#### 4.1 Test with Render Backend URL

**Setup:**
1. Temporarily update `.env` to use Render backend:
   ```
   REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
   ```
2. Restart React dev server: `npm start`
3. Login and navigate to submissions

**Verification Points:**
- [ ] API calls go to `https://atm-maintenance.onrender.com/api`
- [ ] Media URLs are absolute from Render: `https://atm-maintenance.onrender.com/media/...`
- [ ] Images load without CORS errors
- [ ] PDFs open without issues
- [ ] No console errors

#### 4.2 Revert to Local Backend
```
REACT_APP_API_URL=http://localhost:8000/api
```

---

## Issue Reporting Template

If you encounter issues, document them using this template:

### Issue: [Brief Title]
- **Component:** SubmissionDetail.jsx / SubmissionList.jsx / Other
- **User Role:** Technician / Supervisor / Admin
- **Steps to Reproduce:**
  1. ...
  2. ...
  3. ...
- **Expected Result:** [What should happen]
- **Actual Result:** [What actually happened]
- **Console Error:** [Copy full error message]
- **Network Error:** [Screenshot of Network tab showing failed request]
- **Severity:** Critical / High / Medium / Low

---

## Common Issues & Solutions

### Issue: Images show 404 errors
**Cause:** Backend not returning absolute URLs
**Solution:** 
1. Verify `PhotoSerializer.get_file_url()` is using `build_absolute_media_url()`
2. Check `MEDIA_BASE_URL` setting in Django settings
3. Verify request context is passed to serializer

### Issue: CORS errors in console
**Cause:** CORS headers not configured correctly
**Solution:**
1. Verify `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
2. Restart Django server after settings changes
3. Clear browser cache

### Issue: MediaImage component shows error state
**Cause:** Image URL is invalid or unreachable
**Solution:**
1. Check browser Network tab for actual request URL
2. Verify URL is absolute and correctly formed
3. Test URL directly in browser address bar

### Issue: PDF preview doesn't open
**Cause:** PDF URL is incorrect or popup blocked
**Solution:**
1. Check browser console for error message
2. Allow popups for localhost in browser settings
3. Verify PDF file exists on backend at specified path

---

## Success Criteria

✅ **All tests pass when:**
1. All images load without 404 errors
2. All PDFs open without errors
3. No CORS errors in console
4. No console errors or warnings related to media
5. All user roles (technician, supervisor, admin) can view media
6. MediaImage component properly handles loading and error states
7. Modal image viewer works correctly
8. Network tab shows all requests to correct backend URL

---

## Next Steps After Testing

### If All Tests Pass:
1. ✅ Proceed to deployment
2. Deploy backend changes to Render
3. Deploy frontend build to Hostinger
4. Test from production URLs

### If Issues Found:
1. ❌ Document issues using template above
2. Fix issues in code
3. Re-run tests
4. Repeat until all tests pass

---

## Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Backend API | ⬜ | |
| CORS Headers | ⬜ | |
| SubmissionDetail Images | ⬜ | |
| SubmissionDetail PDF | ⬜ | |
| SubmissionList | ⬜ | |
| Technician View | ⬜ | |
| Network Requests | ⬜ | |
| Console Errors | ⬜ | |
| Cross-Domain (Render) | ⬜ | |

---

## Testing Commands Reference

```bash
# Start frontend dev server
cd frontend/atm_frontend && npm start

# Start backend (if running locally)
cd backend && python manage.py runserver

# Check backend API (with token)
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/supervisor/submissions

# Check CORS
curl -i -H "Origin: http://localhost:3000" http://localhost:8000/api/supervisor/submissions

# Clear npm cache if needed
npm cache clean --force

# Reinstall dependencies if needed
rm -rf node_modules package-lock.json && npm install
```

---

## Notes
- Keep DevTools open during testing to catch any errors
- Test with different browsers if possible (Chrome, Firefox, Safari)
- Test on different network conditions if possible (throttle in DevTools)
- Document any issues found for future reference
