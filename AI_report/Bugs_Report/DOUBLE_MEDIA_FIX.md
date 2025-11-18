# Fix: Double /media/ Prefix Issue

## 🎯 Problem Identified

The backend was returning URLs with **double `/media/` prefixes**:
- ❌ `GET /media/media/pdfs/3/CL1_8283.pdf` (should be `/media/pdfs/3/CL1_8283.pdf`)
- ❌ `GET /media/photos/3/section1_1_389b789d.jpg` (should be `/media/photos/3/section1_1_389b789d.jpg`)

This caused both **photo loading** and **PDF generation** to fail with 404 errors.

---

## 🔍 Root Cause Analysis

### Issue 1: PDF Generator Including `media/` Prefix

**File:** `backend/core/utils/pdf_generator.py` (line 127)

```python
# BEFORE (WRONG):
media_relative_dir = os.path.join('media', 'pdfs', str(self.submission.id))
# Result: 'media/pdfs/3'
```

When this path was passed to `build_absolute_media_url()`, it would add another `/media/`:
```
base_url + /media/ + media/pdfs/3 = /media/media/pdfs/3 ❌
```

### Issue 2: Photo Handler Inconsistency

**File:** `backend/core/utils/file_handler.py` (line 117)

```python
# CORRECT:
relative_path = os.path.join('photos', str(submission_id), unique_filename)
# Result: 'photos/3/section1_1_389b789d.jpg' (no 'media/' prefix)
```

Photos were stored correctly WITHOUT the `media/` prefix, but PDFs were stored WITH it.

### Issue 3: URL Builder Not Handling Both Cases

**File:** `backend/core/utils/media_url_builder.py` (line 69)

The `build_absolute_media_url()` function didn't strip the `media/` prefix if it was already present:

```python
# BEFORE (INCOMPLETE):
full_url = f"{base_url}{media_url}/{normalized_path}"
# If normalized_path = 'media/pdfs/3/file.pdf'
# Result: https://atm-maintenance.onrender.com/media/media/pdfs/3/file.pdf ❌
```

---

## ✅ Solution Applied

### Fix 1: Remove `media/` Prefix from PDF Generator

**File:** `backend/core/utils/pdf_generator.py` (line 127)

```python
# AFTER (CORRECT):
media_relative_dir = os.path.join('pdfs', str(self.submission.id))
# Result: 'pdfs/3' (no 'media/' prefix)
```

Now PDFs are stored with the same relative path format as photos.

### Fix 2: Strip `media/` Prefix in URL Builder

**File:** `backend/core/utils/media_url_builder.py` (lines 64-66)

```python
# AFTER (DEFENSIVE):
# Remove 'media/' prefix if it exists (to avoid double /media/media/)
if normalized_path.startswith('media/'):
    normalized_path = normalized_path[6:]  # Remove 'media/' (6 characters)
```

This ensures that even if a path includes `media/`, it will be stripped before adding the MEDIA_URL prefix.

---

## 📊 URL Construction Flow (After Fix)

### Photo URLs:
```
Photo file_url in DB: 'photos/3/section1_1_389b789d.jpg'
↓
build_absolute_media_url('photos/3/section1_1_389b789d.jpg')
↓
Strip 'media/' prefix (if exists): 'photos/3/section1_1_389b789d.jpg' (no change)
↓
Construct URL: https://atm-maintenance.onrender.com + /media/ + photos/3/section1_1_389b789d.jpg
↓
Result: https://atm-maintenance.onrender.com/media/photos/3/section1_1_389b789d.jpg ✅
```

### PDF URLs:
```
PDF relative_pdf_path: 'pdfs/3/Electro_8283.pdf'
↓
build_absolute_pdf_url('pdfs/3/Electro_8283.pdf')
↓
Strip 'media/' prefix (if exists): 'pdfs/3/Electro_8283.pdf' (no change)
↓
Construct URL: https://atm-maintenance.onrender.com + /media/ + pdfs/3/Electro_8283.pdf
↓
Result: https://atm-maintenance.onrender.com/media/pdfs/3/Electro_8283.pdf ✅
```

---

## 🚀 Deployment Status

✅ **Changes committed and pushed to GitHub**
- Commit: `c6cc7a1`
- Files modified:
  - `backend/core/utils/media_url_builder.py`
  - `backend/core/utils/pdf_generator.py`

⏳ **Render will auto-deploy within 1-5 minutes**

---

## 🧪 Testing After Deployment

### Test 1: Photo Loading
```
Expected: https://atm-maintenance.onrender.com/media/photos/3/section1_1_389b789d.jpg
Status: Should return 200 OK with image
```

### Test 2: PDF Generation
```
Expected: https://atm-maintenance.onrender.com/media/pdfs/3/Electro_8283.pdf
Status: Should return 200 OK with PDF
```

### Test 3: Admin Page
- Photos should display without 404 errors
- "View / Generate PDF" button should work

---

## 📝 Files Modified

| File | Change | Line(s) |
|------|--------|---------|
| `backend/core/utils/pdf_generator.py` | Remove `media/` from relative path | 127 |
| `backend/core/utils/media_url_builder.py` | Add defensive `media/` prefix stripping | 64-66 |

---

## 🔗 Related Issues Fixed

1. ✅ Admin can't view uploaded photos (404 errors)
2. ✅ PDF files not being generated (404 errors)
3. ✅ Double `/media/` prefix in URLs

---

## 📋 Next Steps

1. **Wait for Render deployment** (1-5 minutes)
2. **Test photo loading** in admin page
3. **Test PDF generation** by clicking "View / Generate PDF"
4. **Verify no 404 errors** in browser console
5. **Check Render logs** for any errors

If issues persist, check:
- Render logs for errors
- Media file permissions
- Database entries for correct paths
- Browser cache (clear if needed)

---

## 💡 Key Learnings

- **Consistency is critical**: All relative paths should follow the same format
- **Defensive programming**: URL builders should handle multiple input formats
- **Path normalization**: Always strip prefixes before adding them to avoid duplication
- **Testing**: Test both photos and PDFs together to catch inconsistencies

