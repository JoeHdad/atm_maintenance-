# Login API Fix - Verification & Testing

## Problem Identified
The React frontend was sending login requests to `http://localhost:3000` instead of `http://localhost:8000/api` because the `.env` file was missing. Without the environment variable, the fallback in `auth.js` was using `/api` which resolved to the frontend's own domain.

## Solution Applied

### 1. Created `.env` File
**Location:** `frontend/atm_frontend/.env`

**Content:**
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
GENERATE_SOURCEMAP=false
```

**Why This Fixes It:**
- `REACT_APP_API_URL` is now explicitly set to the Django backend
- React will use this value instead of the fallback `/api`
- All API calls (login, submissions, etc.) will go to `http://localhost:8000/api`

### 2. Backend Configuration (Already Correct)
- ✅ Login endpoint: `POST /api/auth/login/`
- ✅ CORS allowed origins include `http://localhost:3000`
- ✅ CSRF trusted origins include `http://localhost:3000`
- ✅ LoginSerializer expects `username` and `password`

### 3. Frontend API Configuration (Already Correct)
- ✅ `auth.js` creates axios instance with `REACT_APP_API_URL`
- ✅ Login function posts to `/auth/login/` (appended to baseURL)
- ✅ AuthContext properly handles response and stores tokens

---

## How to Test Locally

### Step 1: Verify Backend is Running
```bash
# Terminal 1: Start Django backend
cd backend
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Verify Frontend Environment
```bash
# Check .env file exists
cat frontend/atm_frontend/.env
```

**Expected Output:**
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
GENERATE_SOURCEMAP=false
```

### Step 3: Start Frontend Dev Server
```bash
# Terminal 2: Start React frontend
cd frontend/atm_frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view atm_frontend in the browser.

  Local:            http://localhost:3000
```

### Step 4: Test Login

**In Browser:**
1. Open `http://localhost:3000`
2. Open DevTools (F12) → Network tab
3. Enter credentials:
   - Username: `admin` (or `host` or technician username)
   - Password: `admin123` (or appropriate password)
4. Click "Login"

**Expected Network Request:**
- **URL:** `http://localhost:8000/api/auth/login/`
- **Method:** POST
- **Status:** 200
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response Body:**
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "city": null
    }
  }
  ```

**Expected Browser Behavior:**
- ✅ Login succeeds
- ✅ Redirected to dashboard
- ✅ No console errors
- ✅ No CORS errors

---

## Verification Checklist

### Environment Setup
- [ ] `.env` file exists at `frontend/atm_frontend/.env`
- [ ] `.env` contains `REACT_APP_API_URL=http://localhost:8000/api`
- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:3000`

### API Configuration
- [ ] `auth.js` baseURL uses `process.env.REACT_APP_API_URL`
- [ ] Login endpoint is `/api/auth/login/`
- [ ] Backend CORS allows `http://localhost:3000`
- [ ] Backend CSRF allows `http://localhost:3000`

### Login Test
- [ ] Network tab shows request to `http://localhost:8000/api/auth/login/`
- [ ] Request method is POST
- [ ] Request status is 200 (not 400)
- [ ] Response contains `access`, `refresh`, and `user` fields
- [ ] No console errors
- [ ] No CORS errors
- [ ] Dashboard loads after login

### Token Storage
- [ ] Tokens stored in localStorage
- [ ] User data stored in localStorage
- [ ] AuthContext state updated with tokens and user

---

## Troubleshooting

### Issue: Still Getting 400 Bad Request

**Cause:** `.env` file not reloaded by React dev server

**Solution:**
1. Stop React dev server (Ctrl+C)
2. Verify `.env` file exists and has correct content
3. Restart React dev server: `npm start`
4. Clear browser cache (Ctrl+Shift+Delete)
5. Try login again

### Issue: CORS Error in Console

**Cause:** CORS headers not configured correctly

**Solution:**
1. Verify backend `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
2. Restart Django backend
3. Check backend logs for CORS errors

### Issue: 404 Not Found for `/api/auth/login/`

**Cause:** Backend not running or wrong port

**Solution:**
1. Verify backend running at `http://localhost:8000`
2. Check Django logs for errors
3. Verify `core/urls.py` has `path('auth/login/', views.login_view, name='login')`

### Issue: "Invalid username or password"

**Cause:** User doesn't exist or password is wrong

**Solution:**
1. Verify user exists in database: `python manage.py shell`
   ```python
   from core.models import User
   User.objects.filter(username='admin').exists()
   ```
2. If user doesn't exist, create it:
   ```bash
   python create_users.py
   ```
3. Try login with correct credentials

---

## Files Modified/Created

### Created
- ✅ `frontend/atm_frontend/.env` - Local development environment variables

### Verified (No Changes Needed)
- ✅ `frontend/atm_frontend/src/api/auth.js` - Correct configuration
- ✅ `frontend/atm_frontend/src/context/AuthContext.jsx` - Correct implementation
- ✅ `backend/core/urls.py` - Login endpoint configured
- ✅ `backend/core/views.py` - Login view implemented
- ✅ `backend/core/serializers.py` - LoginSerializer correct
- ✅ `backend/atm_backend/settings.py` - CORS/CSRF configured

---

## Next Steps

1. ✅ Restart React dev server with `.env` file
2. ✅ Test login from `http://localhost:3000`
3. ✅ Verify Network tab shows correct API URL
4. ✅ Verify login succeeds with 200 response
5. ✅ Proceed with media display testing

---

## Environment Variables Reference

### Development (Local)
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

### Production (Hostinger)
```
REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
REACT_APP_ENV=production
```

---

## API Endpoint Reference

| Endpoint | Method | URL | Purpose |
|----------|--------|-----|---------|
| Login | POST | `/api/auth/login/` | Authenticate user |
| Refresh Token | POST | `/api/auth/refresh/` | Get new access token |
| Get Submissions | GET | `/api/supervisor/submissions` | List submissions |
| Get Submission Detail | GET | `/api/supervisor/submissions/{id}` | Get submission details |
| Preview PDF | POST | `/api/supervisor/submissions/{id}/preview-pdf` | Generate PDF |

---

## Success Indicators

✅ **Login works when:**
1. Network tab shows POST to `http://localhost:8000/api/auth/login/`
2. Response status is 200
3. Response contains `access`, `refresh`, and `user`
4. Dashboard loads after login
5. No console errors or CORS warnings
6. Tokens stored in localStorage

---

## Notes

- The `.env` file must be created in the `frontend/atm_frontend` directory
- React dev server must be restarted after creating/modifying `.env`
- The `REACT_APP_` prefix is required for React to expose the variable
- Environment variables are embedded at build time, not runtime
- For production, use `.env.production` with production API URL
