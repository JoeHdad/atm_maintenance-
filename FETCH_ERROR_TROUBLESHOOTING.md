# FetchError Troubleshooting Guide

## Error Description
When opening the Upload Device Excel File page, a FetchError appears immediately in the console.

## Root Causes

The FetchError typically indicates one of these issues:

1. **Backend server is not running**
2. **API endpoint is not accessible**
3. **CORS (Cross-Origin Resource Sharing) issue**
4. **Authentication token is missing or invalid**
5. **Network connectivity issue**

## Debugging Steps

### Step 1: Check Backend Server Status

1. Open terminal where backend is running
2. Look for any error messages
3. Verify the server is listening on the correct port (usually 8000)

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Check Browser Console Logs

Open browser DevTools (F12) and look for these logs:

**Expected logs when page loads:**
```
[API] Calling GET /host/technicians/
[API] Response status: 200
[API] Response data: [...]
[FETCH_TECH] Calling getTechnicians...
[FETCH_TECH] Successfully fetched technicians: [...]
```

**If you see FetchError, look for:**
```
[API] Error in getTechnicians: FetchError
[API] Error name: FetchError
[API] Error message: [specific error message]
[API] Error response: [response details]
```

### Step 3: Check Network Tab

1. Open DevTools → Network tab
2. Reload the page
3. Look for the request to `/api/host/technicians/`

**Expected:**
- Status: 200 OK
- Response: JSON array of technicians

**If error:**
- Status: 404 (endpoint not found)
- Status: 401 (unauthorized - token issue)
- Status: 500 (server error)
- Status: (no response) - network/CORS issue

### Step 4: Check API URL Configuration

1. Open `frontend/.env` or `frontend/.env.local`
2. Verify `REACT_APP_API_URL` is set correctly

**Common values:**
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_URL=/api  (if frontend and backend on same server)
```

### Step 5: Check Authentication Token

1. Open DevTools → Application → Local Storage
2. Look for `tokens` key
3. Verify it contains a valid access token

**Expected format:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 6: Check CORS Headers

1. In Network tab, click on the failed request
2. Go to Response Headers
3. Look for `Access-Control-Allow-*` headers

**If missing, backend needs CORS configuration**

## Common Solutions

### Solution 1: Backend Not Running
```bash
cd backend
python manage.py runserver
```

### Solution 2: Wrong API URL
Check `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
```

### Solution 3: Token Missing
1. Logout and login again
2. Check if token is stored in localStorage
3. Verify token is not expired

### Solution 4: CORS Issue
Backend `settings.py` should have:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Solution 5: Endpoint Not Found
Verify backend URL pattern in `core/urls.py`:
```python
path('host/technicians/', views.technicians_view, name='technicians'),
```

## Testing the API Directly

### Using cURL
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/host/technicians/
```

### Using Postman
1. Create GET request to `http://localhost:8000/api/host/technicians/`
2. Add header: `Authorization: Bearer YOUR_TOKEN`
3. Send request

## Detailed Logging Output

After implementing the new logging, you should see:

**In Browser Console:**
```
[API] Calling GET /host/technicians/
[API] Response status: 200
[API] Response data: {...}
[FETCH_TECH] Calling getTechnicians...
[FETCH_TECH] Successfully fetched technicians: [...]
```

**If error:**
```
[API] Error in getTechnicians: FetchError
[API] Error name: FetchError
[API] Error message: Failed to fetch
[API] Error response: undefined
[FETCH_TECH] Error fetching technicians: FetchError
[FETCH_TECH] Error name: FetchError
[FETCH_TECH] Error message: Failed to fetch
```

## Next Steps

1. **Check backend server** - Is it running?
2. **Check API URL** - Is it correct in `.env`?
3. **Check token** - Is it in localStorage?
4. **Check Network tab** - What's the actual error?
5. **Share logs** - Provide console output and network tab details

## Report Format

When reporting the issue, please provide:

1. **Backend console output** (full error if any)
2. **Browser console logs** (all [API] and [FETCH_TECH] logs)
3. **Network tab screenshot** showing the failed request
4. **Response headers** from the failed request
5. **Your environment**:
   - Frontend URL (e.g., http://localhost:3000)
   - Backend URL (e.g., http://localhost:8000)
   - Are they on the same machine?
