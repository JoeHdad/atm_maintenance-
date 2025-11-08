# ATM Maintenance System - Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the ATM Maintenance System to production:
- **Backend:** Render (https://atm-maintenance.onrender.com)
- **Frontend:** Hostinger (https://amanisafi.com)
- **Database:** Render PostgreSQL

---

## Prerequisites

### Local Environment
- Python 3.13+
- Node.js 18+
- npm or yarn
- Git
- PowerShell (for Windows) or Bash (for Linux/Mac)

### Accounts & Access
- GitHub repository access
- Render account with backend service deployed
- Hostinger account with domain configured
- Database credentials for Render PostgreSQL

---

## Automated Deployment Process

### Option 1: Automated Script (Recommended)

#### Windows (PowerShell)
```powershell
# Run the deployment script
.\DEPLOY_PRODUCTION.ps1
```

#### Linux/Mac (Bash)
```bash
# Make script executable
chmod +x deploy_production.sh

# Run the deployment script
./deploy_production.sh
```

The script will automatically:
1. ✅ Build React frontend for production
2. ✅ Collect Django static files
3. ✅ Package media files into ZIP
4. ✅ Verify all deployment files
5. ✅ Generate deployment summary

---

## Manual Deployment Process

### Step 1: Prepare Backend

#### 1.1 Verify Django Settings
```bash
cd backend
```

**Check `.env` file:**
```
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,aroundh-ksa.com,www.aroundh-ksa.com,atm-maintenance.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://amanisafi.com,https://www.amanisafi.com
DATABASE_URL=postgresql://...
```

#### 1.2 Collect Static Files
```bash
python manage.py collectstatic --noinput --clear
```

**Expected output:**
```
Collecting static files...
...
X static files copied to 'backend/staticfiles'
```

**Verify:**
```bash
ls -la staticfiles/
# Should contain: admin/, rest_framework/, etc.
```

#### 1.3 Verify Media Files
```bash
ls -la media/
# Should contain: photos/, pdfs/, excel_uploads/, etc.
```

---

### Step 2: Build React Frontend

#### 2.1 Install Dependencies
```bash
cd frontend/atm_frontend
npm install
```

#### 2.2 Build for Production
```bash
npm run build
```

**Expected output:**
```
> atm_frontend@0.1.0 build
> react-scripts build

Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  ...
  build/index.html: X KB
  build/static/js/main.*.js: X KB
```

**Verify build folder:**
```bash
ls -la build/
# Should contain: index.html, static/, favicon.ico, etc.
```

---

### Step 3: Package Media Files

#### 3.1 Create Media ZIP
```bash
# From project root
cd backend
Compress-Archive -Path "media\*" -DestinationPath "..\media.zip" -Force
```

**Or on Linux/Mac:**
```bash
cd backend
zip -r ../media.zip media/
```

**Verify ZIP contents:**
```bash
# List contents without extracting
unzip -l ../media.zip
```

---

### Step 4: Push to GitHub

```bash
# From project root
git add .
git commit -m "Production build: React build, static files, and media packaging ready for deployment"
git push origin main
```

---

### Step 5: Deploy Backend to Render

#### 5.1 Trigger Render Deployment
1. Go to https://dashboard.render.com
2. Select your service: `atm-maintenance`
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete (5-10 minutes)

#### 5.2 Verify Backend Deployment
```bash
# Test API endpoint
curl -X GET https://atm-maintenance.onrender.com/api/supervisor/submissions

# Expected: 401 Unauthorized (because no auth token)
# If you get 404 or 500, deployment failed
```

---

### Step 6: Deploy Frontend to Hostinger

#### 6.1 Download Build Folder
```bash
# From your local machine, the build folder is at:
frontend/atm_frontend/build/
```

#### 6.2 Connect to Hostinger via FTP/SSH

**Option A: Using FTP (FileZilla)**
1. Open FileZilla
2. Connect to Hostinger FTP server
3. Navigate to `/public_html/`
4. Upload contents of `build/` folder

**Option B: Using SSH (Terminal)**
```bash
# SSH into Hostinger
ssh username@amanisafi.com

# Navigate to public_html
cd public_html

# Upload build files (from local machine)
scp -r frontend/atm_frontend/build/* username@amanisafi.com:/home/username/public_html/
```

#### 6.3 Configure .htaccess for React Router
Create/update `.htaccess` in `/public_html/`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
```

---

### Step 7: Upload Media Files to Hostinger

#### 7.1 Download Media ZIP
```bash
# From your local machine
# File location: media.zip (in project root)
```

#### 7.2 Upload to Hostinger

**Option A: Using FTP**
1. Upload `media.zip` to `/public_html/`
2. Extract using Hostinger file manager
3. Verify folder structure: `/public_html/media/photos/`, `/public_html/media/pdfs/`, etc.

**Option B: Using SSH**
```bash
# Upload media.zip
scp media.zip username@amanisafi.com:/home/username/public_html/

# SSH into Hostinger
ssh username@amanisafi.com

# Extract media.zip
cd /home/username/public_html/
unzip media.zip
rm media.zip

# Verify structure
ls -la media/
```

---

### Step 8: Verify Production Deployment

#### 8.1 Test Frontend
```bash
# Open in browser
https://amanisafi.com

# Expected: Login page loads
# Check browser console (F12) for any errors
```

#### 8.2 Test Login
1. Go to https://amanisafi.com
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`
3. Check Network tab (F12):
   - Requests should go to `https://atm-maintenance.onrender.com/api`
   - No CORS errors
   - Status codes: 200, 401, etc. (not 404 or 500)

#### 8.3 Test Media Display
1. Navigate to a submission with photos
2. Verify images load from `https://atm-maintenance.onrender.com/media/photos/...`
3. Click "View PDF Preview"
4. Verify PDF opens from `https://atm-maintenance.onrender.com/media/pdfs/...`

#### 8.4 Test API Endpoints
```bash
# Get submissions (requires auth token)
curl -X GET https://atm-maintenance.onrender.com/api/supervisor/submissions \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 200 with JSON response
```

---

## Troubleshooting

### Frontend Issues

#### Issue: Blank page or 404 errors
**Cause:** Build folder not uploaded correctly
**Solution:**
1. Verify `build/index.html` exists on Hostinger
2. Check `.htaccess` is in place
3. Verify React Router configuration

#### Issue: API requests fail (CORS errors)
**Cause:** Backend CORS not configured for Hostinger domain
**Solution:**
1. Verify `CORS_ALLOWED_ORIGINS` includes `https://amanisafi.com`
2. Restart Render deployment
3. Clear browser cache

#### Issue: Images/PDFs show 404
**Cause:** Media files not uploaded to Hostinger
**Solution:**
1. Verify `media/` folder exists on Hostinger
2. Check folder structure matches database references
3. Re-upload media.zip and extract

### Backend Issues

#### Issue: Render deployment fails
**Cause:** Missing dependencies or environment variables
**Solution:**
1. Check Render logs: Dashboard → Service → Logs
2. Verify `.env` variables are set in Render
3. Ensure `requirements.txt` is up to date

#### Issue: Database connection fails
**Cause:** DATABASE_URL incorrect or database offline
**Solution:**
1. Verify DATABASE_URL in Render environment
2. Check Render PostgreSQL service is running
3. Test connection: `python manage.py dbshell`

#### Issue: Static files not serving
**Cause:** `collectstatic` not run or STATIC_ROOT incorrect
**Solution:**
1. Run `python manage.py collectstatic --noinput`
2. Verify `STATIC_ROOT` in settings.py
3. Check WhiteNoise middleware is enabled

---

## Environment Variables Checklist

### Backend (.env)
```
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1,aroundh-ksa.com,www.aroundh-ksa.com,atm-maintenance.onrender.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://amanisafi.com,https://www.amanisafi.com
MEDIA_BASE_URL=https://atm-maintenance.onrender.com
```

### Frontend (.env.production)
```
REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
```

---

## File Structure for Deployment

### Backend (Render)
```
backend/
├── atm_backend/
│   ├── settings.py (DEBUG=False, ALLOWED_HOSTS configured)
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── media/ (uploaded files)
│   ├── photos/
│   ├── pdfs/
│   └── excel_uploads/
├── staticfiles/ (collected by collectstatic)
├── manage.py
├── requirements.txt
└── .env (production settings)
```

### Frontend (Hostinger)
```
/public_html/
├── build/ (React production build)
│   ├── index.html
│   ├── static/
│   │   ├── js/
│   │   ├── css/
│   │   └── media/
│   └── favicon.ico
├── media/ (uploaded media files)
│   ├── photos/
│   ├── pdfs/
│   └── excel_uploads/
└── .htaccess (React Router configuration)
```

---

## Rollback Procedure

If deployment fails:

### Rollback Frontend
1. SSH into Hostinger
2. Restore previous build from backup
3. Or redeploy previous version from GitHub

### Rollback Backend
1. Go to Render dashboard
2. Click "Deployments"
3. Select previous successful deployment
4. Click "Redeploy"

---

## Maintenance & Updates

### Regular Tasks
- **Weekly:** Monitor Render logs for errors
- **Monthly:** Update dependencies (`npm update`, `pip install --upgrade`)
- **Quarterly:** Review and update security settings

### Deployment Updates
To deploy updates:
1. Make code changes locally
2. Test locally
3. Run `DEPLOY_PRODUCTION.ps1`
4. Push to GitHub
5. Render auto-deploys
6. Upload new build to Hostinger

---

## Support & Resources

- **Render Documentation:** https://render.com/docs
- **Hostinger Support:** https://www.hostinger.com/support
- **Django Documentation:** https://docs.djangoproject.com
- **React Documentation:** https://react.dev

---

## Deployment Checklist

- [ ] Backend `.env` configured for production
- [ ] Frontend `.env.production` configured
- [ ] React build folder created and verified
- [ ] Django static files collected
- [ ] Media files packaged into ZIP
- [ ] All files pushed to GitHub
- [ ] Render deployment triggered and successful
- [ ] Frontend build uploaded to Hostinger
- [ ] Media files uploaded to Hostinger
- [ ] `.htaccess` configured on Hostinger
- [ ] Frontend loads at https://amanisafi.com
- [ ] Login works without errors
- [ ] API requests go to https://atm-maintenance.onrender.com/api
- [ ] Images and PDFs load correctly
- [ ] No console errors or CORS warnings

---

**Last Updated:** November 8, 2025
**Version:** 1.0
