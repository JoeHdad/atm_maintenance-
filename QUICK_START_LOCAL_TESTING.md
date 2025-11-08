# Quick Start: Local Testing Guide

## TL;DR - Get Running in 3 Steps

### Step 1: Start Backend
```bash
cd backend
python manage.py runserver
```
✅ Backend runs at `http://localhost:8000`

### Step 2: Start Frontend
```bash
cd frontend/atm_frontend
npm start
```
✅ Frontend runs at `http://localhost:3000`

### Step 3: Test Login
1. Open `http://localhost:3000` in browser
2. Open DevTools (F12) → Network tab
3. Login with:
   - Username: `admin`
   - Password: `admin123`
4. Check Network tab: Request should go to `http://localhost:8000/api/auth/login/` with status 200

---

## What Was Fixed

**Problem:** Login requests were going to `http://localhost:3000/api/auth/login/` (wrong domain)

**Root Cause:** Missing `.env` file in frontend directory

**Solution:** Created `.env` with:
```
REACT_APP_API_URL=http://localhost:8000/api
```

---

## Testing Checklist

### Login Test
- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:3000`
- [ ] `.env` file exists with correct API URL
- [ ] Network tab shows POST to `http://localhost:8000/api/auth/login/`
- [ ] Response status is 200
- [ ] Dashboard loads after login
- [ ] No console errors

### Media Display Test (After Login)
- [ ] Navigate to submission with photos
- [ ] All photos load without 404 errors
- [ ] Photos are from `http://localhost:8000/media/photos/...`
- [ ] Click "View PDF Preview" - PDF opens in new tab
- [ ] PDF is from `http://localhost:8000/media/pdfs/...`
- [ ] Click photo to open modal - full-size image displays
- [ ] No console errors or CORS warnings

### API Response Test
- [ ] Network tab → Find `submissions` request
- [ ] Response contains absolute URLs starting with `http://localhost:8000/media/`
- [ ] All `file_url` fields are absolute
- [ ] All `pdf_url` fields are absolute

---

## Common Issues & Quick Fixes

### Issue: Login returns 400 Bad Request
**Fix:** 
1. Stop React dev server (Ctrl+C)
2. Restart: `npm start`
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue: CORS error in console
**Fix:**
1. Restart Django backend
2. Verify `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`

### Issue: Images show 404
**Fix:**
1. Check Network tab for actual image URL
2. Verify URL is absolute (starts with `http://`)
3. Verify backend is running

### Issue: "Invalid username or password"
**Fix:**
1. Create users: `python create_users.py`
2. Or login as `admin` / `admin123`

---

## File Locations

| File | Purpose | Status |
|------|---------|--------|
| `frontend/atm_frontend/.env` | Local dev config | ✅ Created |
| `frontend/atm_frontend/src/api/auth.js` | Login API | ✅ Correct |
| `frontend/atm_frontend/src/context/AuthContext.jsx` | Auth state | ✅ Correct |
| `backend/core/views.py` | Login endpoint | ✅ Correct |
| `backend/core/serializers.py` | Login serializer | ✅ Correct |

---

## Test Results Template

```
Date: _______________
Tester: _______________

Backend Status: ✅ Running / ❌ Failed
Frontend Status: ✅ Running / ❌ Failed

Login Test: ✅ Pass / ❌ Fail
- Network URL: _______________
- Response Status: _______________
- Error (if any): _______________

Media Display: ✅ Pass / ❌ Fail
- Images Load: ✅ Yes / ❌ No
- PDFs Load: ✅ Yes / ❌ No
- Console Errors: ✅ None / ❌ Present

Notes:
_______________________________________________
_______________________________________________
```

---

## Next Steps

1. ✅ Restart React dev server
2. ✅ Test login
3. ✅ Test media display
4. ✅ Report results
5. ⏳ Deploy to production (after all tests pass)

---

## Support

For detailed troubleshooting, see:
- `LOGIN_FIX_VERIFICATION.md` - Detailed login fix guide
- `TESTING_MEDIA_DISPLAY.md` - Detailed media testing guide
- `TEST_VERIFICATION.md` - Quick test checklist
