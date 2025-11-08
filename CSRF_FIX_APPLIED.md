# CSRF 400 Error Fix - Applied

## Problem
Login requests were returning 400 Bad Request with HTML error page instead of JSON response.

**Error Message:**
```
POST http://localhost:8000/api/auth/login/ 400 (Bad Request)
Response: <!doctype html><html><body><h1>Bad Request (400)</h1></body></html>
```

## Root Cause
Django's CSRF middleware was blocking the cross-origin POST request from the React frontend because:
1. Request came from `http://localhost:3000` (frontend)
2. Request went to `http://localhost:8000` (backend)
3. No CSRF token was included (frontend uses JWT, not CSRF tokens)
4. Django CSRF middleware rejected the request before it reached the API view

## Solution Applied

### 1. Added CSRF Exemption to Login Endpoint
**File:** `backend/core/views.py`

```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # ... login logic ...
```

**Why:** Login endpoint doesn't need CSRF protection because:
- It uses JWT tokens for authentication, not session cookies
- It's a public endpoint (AllowAny permission)
- CORS is already configured to allow the frontend domain

### 2. Added CSRF Exemption to Token Refresh Endpoint
**File:** `backend/core/urls.py`

```python
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    # ...
]
```

**Why:** Token refresh also needs exemption for the same reasons as login.

---

## How to Test

### Step 1: Restart Django Backend
```bash
cd backend
python manage.py runserver
```

### Step 2: Test Login in Browser
1. Open `http://localhost:3000`
2. Open DevTools (F12) → Network tab
3. Enter login credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Login"

### Step 3: Verify Success
**Expected Network Request:**
- **URL:** `http://localhost:8000/api/auth/login/`
- **Method:** POST
- **Status:** ✅ **200** (not 400)
- **Response Type:** JSON (not HTML)
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
- ✅ No "400 Bad Request" errors

---

## Why CSRF Exemption is Safe Here

**CSRF Protection is NOT needed for:**
1. **Stateless API endpoints** - Using JWT tokens, not session cookies
2. **Public endpoints** - No sensitive user data exposed
3. **Cross-origin requests** - CORS already validates origin
4. **Token-based auth** - Tokens are in Authorization header, not cookies

**CSRF Protection IS needed for:**
- Form submissions with session cookies
- Endpoints that modify sensitive user data
- Traditional server-rendered applications

---

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `backend/core/views.py` | Added `@csrf_exempt` to `login_view` | Allow cross-origin login |
| `backend/core/urls.py` | Wrapped `TokenRefreshView` with `csrf_exempt()` | Allow cross-origin token refresh |

---

## Verification Checklist

- [ ] Backend restarted
- [ ] Network tab shows POST to `http://localhost:8000/api/auth/login/`
- [ ] Response status is 200 (not 400)
- [ ] Response is JSON (not HTML)
- [ ] Response contains `access`, `refresh`, and `user` fields
- [ ] Dashboard loads after login
- [ ] No console errors
- [ ] No "Bad Request" errors

---

## Next Steps

1. ✅ Restart Django backend
2. ✅ Test login from frontend
3. ✅ Verify 200 response with JSON
4. ✅ Proceed with media display testing

---

## Security Notes

- CSRF exemption is appropriate for stateless API endpoints using JWT
- CORS is still configured to only allow `http://localhost:3000` in development
- In production, CORS will only allow `https://amanisafi.com`
- JWT tokens are more secure than CSRF tokens for API authentication
- Session-based endpoints still have CSRF protection

---

## References

- [Django CSRF Protection](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/)
- [JWT vs CSRF](https://stackoverflow.com/questions/21357573/csrf-token-necessary-when-using-json-web-tokens-jwt)
