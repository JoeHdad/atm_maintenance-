# PDF Generation Debugging Guide

## Status: Logging Added & Deployed

I've added comprehensive logging throughout the PDF generation pipeline to help identify exactly where the issue is occurring.

---

## 🔍 What Was Added

### 1. **Enhanced Logging in `preview_pdf()` endpoint** (`views_admin.py`)

The endpoint now logs:
- ✅ When endpoint is called
- ✅ Request method and user authentication
- ✅ Submission lookup and photo count
- ✅ PDF generation start/completion
- ✅ Absolute URL construction
- ✅ All errors with full stack traces

**Log prefix:** `[PDF Preview]`

### 2. **Enhanced Logging in `generate_pdf()` function** (`pdf_generator.py`)

The function now logs:
- ✅ Function entry with submission ID
- ✅ Submission type and device info
- ✅ Existing PDF URL check
- ✅ PDF file existence verification
- ✅ Settings paths (PDF_BASE_DIR, MEDIA_ROOT)
- ✅ All errors with full stack traces

**Log prefix:** `[generate_pdf]`

### 3. **Enhanced Logging in `PDFGenerator.generate()` method** (`pdf_generator.py`)

The method now logs:
- ✅ Generation start
- ✅ Image preloading progress
- ✅ PDF directory creation
- ✅ Page generation progress
- ✅ All errors with full stack traces

**Log prefix:** `[PDFGenerator.generate]`

---

## 📋 Next Steps: Testing & Debugging

### Step 1: Wait for Render Deployment

The logging changes have been pushed to GitHub. Render will automatically deploy them within 1-5 minutes.

### Step 2: Check Render Logs

Once deployed, test the PDF endpoint again and check the Render logs:

1. Go to **Render Dashboard** → Your backend service
2. Click **"Logs"** tab
3. Search for `[PDF Preview]` to see all PDF-related logs
4. Look for any error messages

### Step 3: Interpret the Logs

**Expected successful flow:**
```
[PDF Preview] Endpoint called for submission 1
[PDF Preview] Request method: POST
[PDF Preview] User is authenticated: True
[PDF Preview] Fetching submission 1
[PDF Preview] Submission found: 1, Device: 2011, Photos: 5
[PDF Preview] Starting PDF generation for submission 1
[generate_pdf] Called for submission 1
[generate_pdf] Submission type: Electrical, Device: 2011
[generate_pdf] Submission has no existing pdf_url
[generate_pdf] Generating new PDF for submission 1
[generate_pdf] PDF_BASE_DIR: /var/data/pdfs
[generate_pdf] MEDIA_ROOT: /var/data/media
[PDFGenerator.generate] Starting PDF generation for submission 1
[PDFGenerator.generate] Preloading images...
[PDFGenerator.generate] Images preloaded in 0.45s
[PDFGenerator.generate] PDF directory: /var/data/pdfs/1
[PDFGenerator.generate] PDF generated successfully: media/pdfs/1/Electro_2011.pdf
[PDF Preview] PDF generated successfully: media/pdfs/1/Electro_2011.pdf
[PDF Preview] Absolute URL built: https://atm-maintenance.onrender.com/media/pdfs/1/Electro_2011.pdf
```

### Step 4: Common Issues & Solutions

#### **Issue 1: "Submission not found" (404)**
```
[PDF Preview] Submission 1 not found
```
**Solution:** Verify submission ID exists in database

#### **Issue 2: "PDF generation failed"**
```
[PDF Preview] PDF generation failed for submission 1: [error message]
```
**Check the error message for:**
- Permission denied → Check directory permissions
- File not found → Check MEDIA_ROOT path
- Out of memory → PDF too large
- Timeout → PDF generation taking too long

#### **Issue 3: "Images preloading failed"**
```
[PDFGenerator.generate] Images preloaded in 0.00s
[generate_pdf] PDF generation failed: No images found
```
**Solution:** Verify submission has photos attached

#### **Issue 4: "PDF directory creation failed"**
```
[PDFGenerator.generate] PDF directory: /var/data/pdfs/1
[generate_pdf] PDF generation failed: Permission denied
```
**Solution:** Check if `/var/data/pdfs` directory exists and is writable

---

## 🛠️ How to Read Render Logs

### Via Render Dashboard:
1. Go to your backend service
2. Click **"Logs"** tab
3. Logs appear in real-time
4. Use browser's Find (Ctrl+F) to search for `[PDF Preview]`

### Via Render CLI:
```bash
# If you have Render CLI installed
render logs --service=your-service-name --tail
```

### Via SSH (if enabled):
```bash
# SSH into Render instance
ssh your-instance
tail -f /var/log/app.log | grep "PDF"
```

---

## 📊 Log Analysis Checklist

When you test the PDF endpoint, check these logs in order:

- [ ] `[PDF Preview] Endpoint called` - Endpoint is reachable
- [ ] `[PDF Preview] User is authenticated: True` - Auth is working
- [ ] `[PDF Preview] Submission found` - Submission exists
- [ ] `[generate_pdf] Called for submission` - Function is called
- [ ] `[PDFGenerator.generate] Starting PDF generation` - Generator starts
- [ ] `[PDFGenerator.generate] Images preloaded` - Images loaded successfully
- [ ] `[PDFGenerator.generate] PDF directory created` - Directory exists
- [ ] `[generate_pdf] PDF generated successfully` - PDF created
- [ ] `[PDF Preview] Absolute URL built` - URL constructed
- [ ] Response returns 200 OK with `pdf_url` - Success!

---

## 🚨 If You Still Get 404

After checking logs, if you still see 404:

1. **Check if endpoint is being called at all:**
   - Look for `[PDF Preview] Endpoint called` in logs
   - If NOT present → URL routing issue
   - If present → Check subsequent logs

2. **Check if PDF is being generated:**
   - Look for `[PDFGenerator.generate] PDF generated successfully`
   - If NOT present → PDF generation is failing (check error logs)
   - If present → PDF exists but not being served

3. **Check if media serving is working:**
   - Test direct media access: `https://atm-maintenance.onrender.com/media/photos/1/image.jpg`
   - Should return 200 OK
   - If 404 → Media serving still broken

4. **Check file permissions:**
   - PDF file created but not readable?
   - Check Render instance file permissions
   - Ensure `/var/data/pdfs` is readable by Gunicorn

---

## 📝 Share Logs for Help

When reporting issues, please share:

1. **Full log output** from the PDF endpoint call (copy all `[PDF Preview]` and `[generate_pdf]` logs)
2. **Submission ID** you're testing with
3. **Error message** if any
4. **Browser console** error (if applicable)

---

## ✅ Verification After Fix

Once PDF generation is working:

1. **Test locally** with `DEBUG=False`:
   ```bash
   cd backend
   set DEBUG=False
   python manage.py runserver
   # Test: POST http://localhost:8000/api/supervisor/submissions/1/preview-pdf
   ```

2. **Check media directory:**
   ```bash
   ls -la backend/media/pdfs/
   # Should show: 1/Electro_2011.pdf (or similar)
   ```

3. **Test direct PDF access:**
   ```
   http://localhost:8000/media/pdfs/1/Electro_2011.pdf
   # Should return PDF (200 OK)
   ```

4. **Test on Render:**
   ```
   https://atm-maintenance.onrender.com/media/pdfs/1/Electro_2011.pdf
   # Should return PDF (200 OK)
   ```

---

## 🔗 Related Files

- `backend/core/views_admin.py` - `preview_pdf()` endpoint
- `backend/core/utils/pdf_generator.py` - `generate_pdf()` and `PDFGenerator` class
- `backend/core/utils/media_url_builder.py` - `build_absolute_pdf_url()` function
- `backend/atm_backend/urls.py` - Media serving configuration
- `backend/atm_backend/settings.py` - `PDF_BASE_DIR` and `MEDIA_ROOT` settings

---

## 📞 Next Steps

1. **Wait for Render deployment** (1-5 minutes)
2. **Test the PDF endpoint** by clicking "View / Generate PDF"
3. **Check Render logs** for `[PDF Preview]` messages
4. **Share the logs** with me to identify the exact issue
5. **Apply fix** based on the logs

The logging is now deployed and ready to help us identify the exact problem! 🚀
