# Quick Test Verification Checklist

## Before Starting Tests
- [ ] Backend running at `http://localhost:8000` (or accessible)
- [ ] Frontend `.env` configured with `REACT_APP_API_URL=http://localhost:8000/api`
- [ ] Database has test submissions with photos
- [ ] Browser DevTools available (F12)
- [ ] Network tab in DevTools ready to monitor

---

## Test Execution Steps

### Step 1: Start Backend (if local)
```bash
cd backend
python manage.py runserver
```
✅ Verify: Backend running at `http://localhost:8000`

### Step 2: Start Frontend
```bash
cd frontend/atm_frontend
npm start
```
✅ Verify: Frontend opens at `http://localhost:3000`

### Step 3: Login
- [ ] Login as **supervisor/admin** user
- [ ] Verify: Dashboard loads without errors

### Step 4: Test SubmissionDetail.jsx

**Navigate to a submission with photos:**
1. Go to Submissions list
2. Click "Review Submission" on any pending submission
3. Open DevTools (F12) → Console tab

**Test Image Display:**
```javascript
// Run in console to verify image URLs
const images = document.querySelectorAll('img');
console.log(`Found ${images.length} images`);
images.forEach((img, i) => {
  console.log(`Image ${i}:`, {
    src: img.src,
    isAbsolute: img.src.startsWith('http'),
    loaded: img.complete,
    error: img.naturalWidth === 0
  });
});
```

**Expected Output:**
- All images have `src` starting with `http://localhost:8000/media/`
- All images have `isAbsolute: true`
- All images have `loaded: true`
- No images have `error: true`

**Checklist:**
- [ ] All photos visible without 404 errors
- [ ] Images are from `http://localhost:8000/media/photos/...`
- [ ] No red errors in console
- [ ] No CORS errors in console
- [ ] Loading skeleton appears briefly while images load

### Step 5: Test PDF Preview

**In the same submission:**
1. Click "View PDF Preview" button
2. PDF should open in new tab
3. Check Network tab for PDF request

**Checklist:**
- [ ] PDF opens in new tab without errors
- [ ] Network tab shows request to `http://localhost:8000/media/pdfs/...`
- [ ] PDF request status is 200 (not 404)
- [ ] No console errors

### Step 6: Test Image Modal

**In the same submission:**
1. Click on any photo to open modal
2. Modal should display full-size image
3. Press ESC to close

**Checklist:**
- [ ] Modal opens with full-size image
- [ ] Image displays correctly
- [ ] ESC key closes modal
- [ ] No console errors

### Step 7: Test SubmissionList.jsx

**Navigate to submissions list:**
1. Go back to Submissions list
2. Open DevTools → Network tab
3. Reload page

**Check API Response:**
1. In Network tab, find `submissions` request
2. Click on it, go to Response tab
3. Verify response contains absolute URLs

**Expected in Response:**
```json
{
  "submissions": [
    {
      "id": 1,
      "photos": [
        {
          "file_url": "http://localhost:8000/media/photos/..."
        }
      ],
      "pdf_url": "http://localhost:8000/media/pdfs/..."
    }
  ]
}
```

**Checklist:**
- [ ] API response contains absolute URLs
- [ ] All `file_url` start with `http://localhost:8000/media/`
- [ ] All `pdf_url` start with `http://localhost:8000/media/`
- [ ] No relative paths in response

### Step 8: Test Filters

**In submissions list:**
1. Apply device type filter (e.g., "Electrical")
2. Apply status filter (e.g., "Pending")

**Checklist:**
- [ ] Filters work correctly
- [ ] Submissions update based on filter
- [ ] No console errors
- [ ] API request includes filter parameters

### Step 9: Test with Render Backend (Optional)

**Update `.env` temporarily:**
```
REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
```

**Restart frontend:**
```bash
npm start
```

**Test:**
1. Login
2. Navigate to submission with photos
3. Check Network tab

**Checklist:**
- [ ] API calls go to Render backend
- [ ] Images load from Render backend
- [ ] No CORS errors
- [ ] PDFs open correctly
- [ ] All URLs are absolute from Render

**Revert `.env`:**
```
REACT_APP_API_URL=http://localhost:8000/api
```

---

## Console Error Checklist

**Look for these errors - if found, report them:**

- [ ] `404 Not Found` for media files
- [ ] `CORS error` or `Access-Control-Allow-Origin`
- [ ] `TypeError: Cannot read property 'file_url'`
- [ ] `ReferenceError: ensureAbsoluteUrl is not defined`
- [ ] `Failed to load resource` for images
- [ ] `Uncaught Error` in MediaImage component

**If any errors found:**
1. Screenshot the error
2. Note the exact error message
3. Note which component it occurred in
4. Report using Issue template in TESTING_MEDIA_DISPLAY.md

---

## Network Tab Checklist

**In DevTools → Network tab, verify:**

- [ ] All requests to `/api/` return status 200
- [ ] All media requests (images, PDFs) return status 200
- [ ] No requests return 404
- [ ] No requests return 403 (Forbidden)
- [ ] No requests return 500 (Server Error)
- [ ] Response headers include `Content-Type: image/...` for images
- [ ] Response headers include `Content-Type: application/pdf` for PDFs
- [ ] CORS headers present: `Access-Control-Allow-Origin`

---

## Test Results

### Backend API
- Status: ⬜ PENDING
- Notes: 

### Frontend - SubmissionDetail
- Images Load: ⬜ PENDING
- PDF Preview: ⬜ PENDING
- Image Modal: ⬜ PENDING
- Console Errors: ⬜ PENDING

### Frontend - SubmissionList
- List Loads: ⬜ PENDING
- Filters Work: ⬜ PENDING
- API Response: ⬜ PENDING
- Console Errors: ⬜ PENDING

### Network Verification
- All Requests 200: ⬜ PENDING
- No 404 Errors: ⬜ PENDING
- CORS Headers: ⬜ PENDING

### Cross-Domain (Render)
- API Calls to Render: ⬜ PENDING
- Images Load: ⬜ PENDING
- No CORS Errors: ⬜ PENDING

---

## Final Sign-Off

**All tests completed:** ⬜ YES / ⬜ NO

**Issues found:** ⬜ YES / ⬜ NO

**Ready for deployment:** ⬜ YES / ⬜ NO

**Notes:**
```
[Add any additional notes or observations here]
```

---

## Quick Reference: DevTools Commands

```javascript
// Check all image URLs
document.querySelectorAll('img').forEach(img => {
  console.log(img.src, img.complete ? '✓' : '✗');
});

// Check for network errors
performance.getEntriesByType('resource')
  .filter(r => r.transferSize === 0)
  .forEach(r => console.log('Failed:', r.name));

// Check for CORS errors
console.log(document.querySelectorAll('img[crossorigin]'));

// Monitor API calls
fetch('http://localhost:8000/api/supervisor/submissions')
  .then(r => r.json())
  .then(d => console.log(d.submissions[0]));
```

---

## Support

If you encounter issues:
1. Check TESTING_MEDIA_DISPLAY.md for detailed troubleshooting
2. Review the "Common Issues & Solutions" section
3. Document issue using the Issue template
4. Check backend logs for API errors
5. Check browser console for client-side errors
