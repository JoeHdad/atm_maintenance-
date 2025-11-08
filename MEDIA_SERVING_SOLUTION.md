# Cross-Domain Media File Serving Solution

## Problem Statement
The frontend on Hostinger (`https://amanisafi.com/`) was unable to display images and PDFs uploaded by technicians because:
- Frontend tried to load media from `https://amanisafi.com/media/...` (404 errors)
- Media files actually exist on `https://atm-maintenance.onrender.com/media/...`
- Cross-origin requests were blocked due to missing CORS headers

## Solution Overview
This solution implements absolute URL generation on the backend and proper CORS configuration to allow the Hostinger frontend to access media files from the Render backend.

---

## Backend Changes (Django)

### 1. New Utility Module: `core/utils/media_url_builder.py`
Provides functions to build absolute URLs for media files:

```python
# Functions available:
- get_media_base_url(request=None)      # Get base URL for media
- build_absolute_media_url(path, request)  # Build absolute URL for images
- build_absolute_pdf_url(path, request)    # Build absolute URL for PDFs
- is_absolute_url(url)                     # Check if URL is absolute
```

**Usage in serializers:**
```python
from .utils.media_url_builder import build_absolute_media_url

absolute_url = build_absolute_media_url('photos/123/image.jpg', request)
# Returns: https://atm-maintenance.onrender.com/media/photos/123/image.jpg
```

### 2. Updated Serializers: `core/serializers.py`

#### PhotoSerializer
- Now uses `SerializerMethodField` for `file_url`
- Calls `build_absolute_media_url()` to convert relative paths to absolute URLs
- Example output:
  ```json
  {
    "id": 1,
    "section": 1,
    "file_url": "https://atm-maintenance.onrender.com/media/photos/123/image.jpg",
    "order_index": 1
  }
  ```

#### SubmissionSerializer
- Added `pdf_url` as `SerializerMethodField`
- Calls `build_absolute_pdf_url()` for PDF files
- All photos nested inside use PhotoSerializer (with absolute URLs)
- Example output:
  ```json
  {
    "id": 1,
    "technician": 1,
    "device": 1,
    "photos": [
      {
        "id": 1,
        "section": 1,
        "file_url": "https://atm-maintenance.onrender.com/media/photos/123/image.jpg",
        "order_index": 1
      }
    ],
    "pdf_url": "https://atm-maintenance.onrender.com/media/pdfs/123/report.pdf"
  }
  ```

### 3. Settings Configuration: `atm_backend/settings.py`

#### New Setting: MEDIA_BASE_URL
```python
MEDIA_BASE_URL = config(
    'MEDIA_BASE_URL',
    default='https://atm-maintenance.onrender.com' if not DEBUG else 'http://localhost:8000'
)
```

#### Updated CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://amanisafi.com',
    'https://www.amanisafi.com'
]
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

CORS_EXPOSE_HEADERS = [
    'Content-Type',
    'X-CSRFToken',
]
```

#### Updated CSRF Configuration
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://amanisafi.com',
    'https://www.amanisafi.com'
]
```

---

## Frontend Changes (React)

### 1. New Utility Module: `src/utils/mediaUrlHelper.js`
Provides helper functions for handling media URLs:

```javascript
// Functions available:
- isAbsoluteUrl(url)              // Check if URL is absolute
- getMediaBaseUrl()               // Get base URL for media
- ensureAbsoluteUrl(url)          // Ensure URL is absolute
- getSafeImageUrl(url, fallback)  // Get safe image URL
- getSafePdfUrl(url, fallback)    // Get safe PDF URL
- handleImageError(event, fallback) // Handle image load errors
- validateMediaUrl(url)           // Validate URL accessibility
- getImageDimensions(url)         // Get image dimensions
```

**Usage:**
```javascript
import { ensureAbsoluteUrl } from '../utils/mediaUrlHelper';

const imageUrl = ensureAbsoluteUrl(photo.file_url);
// If photo.file_url is already absolute: returns as-is
// If photo.file_url is relative: prepends base URL
```

### 2. New Component: `src/components/MediaImage.jsx`
React component for displaying images with error handling:

```jsx
import MediaImage from '../components/MediaImage';

<MediaImage
  src={photo.file_url}
  alt="Submission photo"
  className="w-full h-64 object-cover rounded"
  fallbackSrc="/placeholder.png"
  onError={(e) => console.error('Image failed to load')}
/>
```

**Features:**
- Automatic URL normalization (relative → absolute)
- Loading state with skeleton animation
- Error handling with fallback image
- Lazy loading support
- Cross-origin compatible

### 3. Integration Points

#### In SubmissionDetail Component
```jsx
import MediaImage from './MediaImage';
import { ensureAbsoluteUrl } from '../utils/mediaUrlHelper';

// Display photos
{submission.photos.map(photo => (
  <MediaImage
    key={photo.id}
    src={photo.file_url}
    alt={`Section ${photo.section}`}
    className="w-full h-64 object-cover rounded"
  />
))}

// Display PDF
{submission.pdf_url && (
  <a
    href={ensureAbsoluteUrl(submission.pdf_url)}
    target="_blank"
    rel="noopener noreferrer"
    className="btn btn-primary"
  >
    Download PDF
  </a>
)}
```

#### In SubmissionList Component
```jsx
// Thumbnail display
{submission.photos[0] && (
  <MediaImage
    src={submission.photos[0].file_url}
    alt="Submission thumbnail"
    className="w-20 h-20 object-cover rounded"
  />
)}
```

---

## Environment Configuration

### Backend (.env)
```env
# Render backend
MEDIA_BASE_URL=https://atm-maintenance.onrender.com

# CORS settings (already configured in settings.py)
# No need to add to .env unless you want to override defaults
```

### Frontend (.env.production)
```env
# API endpoint (already configured)
REACT_APP_API_URL=https://atm-maintenance.onrender.com/api

# Frontend will automatically use absolute URLs from API responses
```

---

## How It Works

### Request Flow
```
1. Technician uploads photos/PDF to Render backend
   └─ Files stored in: /media/photos/{submission_id}/
   └─ Files stored in: /media/pdfs/{submission_id}/

2. Backend serializer converts relative paths to absolute URLs
   └─ 'photos/123/image.jpg' → 'https://atm-maintenance.onrender.com/media/photos/123/image.jpg'

3. API response sent to Hostinger frontend with absolute URLs
   └─ Frontend receives: { file_url: "https://atm-maintenance.onrender.com/..." }

4. Frontend displays images using MediaImage component
   └─ Component uses absolute URL directly
   └─ CORS headers allow cross-origin access

5. Browser loads image from Render backend
   └─ CORS headers permit: https://amanisafi.com → https://atm-maintenance.onrender.com
```

### CORS Request Headers
```
Request:
  Origin: https://amanisafi.com
  
Response:
  Access-Control-Allow-Origin: https://amanisafi.com
  Access-Control-Allow-Credentials: true
  Access-Control-Expose-Headers: Content-Type, X-CSRFToken
```

---

## Testing Checklist

### Backend Testing
- [ ] Media files are uploaded successfully
- [ ] API returns absolute URLs in responses
- [ ] CORS headers are present in responses
- [ ] Test with: `curl -H "Origin: https://amanisafi.com" https://atm-maintenance.onrender.com/api/supervisor/submissions/1`

### Frontend Testing
- [ ] Images load without 404 errors
- [ ] PDFs can be downloaded
- [ ] Error handling works (fallback images display)
- [ ] Network tab shows requests to `https://atm-maintenance.onrender.com/media/...`
- [ ] No CORS errors in browser console
- [ ] Test on both localhost and Hostinger

### Cross-Domain Testing
- [ ] Access frontend from `https://amanisafi.com`
- [ ] Verify images load from `https://atm-maintenance.onrender.com`
- [ ] Check browser DevTools → Network tab for media requests
- [ ] Verify no CORS errors in Console

---

## Troubleshooting

### Images Still Show 404
1. Check backend API response includes absolute URLs
   ```bash
   curl https://atm-maintenance.onrender.com/api/supervisor/submissions/1
   ```
   Look for `"file_url": "https://..."` in response

2. Verify CORS headers in response
   ```bash
   curl -i https://atm-maintenance.onrender.com/api/supervisor/submissions/1
   ```
   Should include `Access-Control-Allow-Origin: https://amanisafi.com`

3. Check browser Network tab for actual image request
   - Should be to `https://atm-maintenance.onrender.com/media/...`
   - Should have 200 status code

### CORS Errors in Console
1. Verify `CORS_ALLOWED_ORIGINS` includes `https://amanisafi.com`
2. Restart Django server after settings changes
3. Clear browser cache and cookies
4. Test with: `curl -H "Origin: https://amanisafi.com" -v https://atm-maintenance.onrender.com/api/...`

### Images Load Slowly
1. Enable image compression in backend
2. Implement image caching headers
3. Use CDN for media files (future enhancement)

---

## Future Enhancements

1. **Image Optimization**
   - Implement image resizing for thumbnails
   - Add WebP format support
   - Implement lazy loading

2. **Caching**
   - Add Cache-Control headers
   - Implement browser caching
   - Add CDN for media files

3. **Security**
   - Implement signed URLs for temporary access
   - Add rate limiting for media downloads
   - Implement access control per user

4. **Performance**
   - Implement image compression
   - Add progressive image loading
   - Implement media file cleanup

---

## Files Modified/Created

### Backend
- ✅ `core/utils/media_url_builder.py` (NEW)
- ✅ `core/serializers.py` (MODIFIED - PhotoSerializer, SubmissionSerializer)
- ✅ `atm_backend/settings.py` (MODIFIED - CORS, CSRF, MEDIA_BASE_URL)

### Frontend
- ✅ `src/utils/mediaUrlHelper.js` (NEW)
- ✅ `src/components/MediaImage.jsx` (NEW)
- ✅ Components using media (to be updated with MediaImage component)

---

## Deployment Checklist

### Before Deploying to Production
- [ ] Update `.env` with `MEDIA_BASE_URL=https://atm-maintenance.onrender.com`
- [ ] Update `CORS_ALLOWED_ORIGINS` with production domain
- [ ] Update `CSRF_TRUSTED_ORIGINS` with production domain
- [ ] Test all media file downloads on staging
- [ ] Verify CORS headers in production
- [ ] Clear CDN cache if using CDN

### Render Deployment
```bash
# Push changes to Render
git push render main

# Render will automatically:
# - Collect static files
# - Run migrations
# - Restart the application
```

### Hostinger Deployment
```bash
# Rebuild frontend with production settings
npm run build

# Upload build/ folder to Hostinger
# Update .env.production if needed
```

---

## Support

For issues or questions:
1. Check browser DevTools → Network tab for failed requests
2. Check Django logs: `heroku logs --tail` (or Render equivalent)
3. Verify CORS headers: `curl -i https://atm-maintenance.onrender.com/api/...`
4. Test media URL directly in browser: `https://atm-maintenance.onrender.com/media/photos/...`
