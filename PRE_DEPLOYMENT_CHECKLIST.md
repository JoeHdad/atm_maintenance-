# Pre-Deployment Checklist

## Backend Configuration

### Django Settings
- [ ] `DEBUG = False` in production `.env`
- [ ] `ALLOWED_HOSTS` includes all domains:
  - [ ] `localhost` (for local testing)
  - [ ] `127.0.0.1` (for local testing)
  - [ ] `atm-maintenance.onrender.com` (Render backend)
  - [ ] `aroundh-ksa.com` (production domain)
  - [ ] `www.aroundh-ksa.com` (production domain)
- [ ] `SECRET_KEY` is set and secure
- [ ] `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- [ ] `MEDIA_ROOT = BASE_DIR / 'media'`
- [ ] `MEDIA_URL = '/media/'`
- [ ] `MEDIA_BASE_URL` set to `https://atm-maintenance.onrender.com`

### CORS Configuration
- [ ] `CORS_ALLOWED_ORIGINS` includes:
  - [ ] `http://localhost:3000` (local development)
  - [ ] `http://127.0.0.1:3000` (local development)
  - [ ] `https://amanisafi.com` (Hostinger frontend)
  - [ ] `https://www.amanisafi.com` (Hostinger frontend)
- [ ] `CORS_ALLOW_CREDENTIALS = True`
- [ ] `CSRF_TRUSTED_ORIGINS` includes same domains

### Database
- [ ] `DATABASE_URL` set to Render PostgreSQL connection string
- [ ] Database connection tested: `python manage.py dbshell`
- [ ] All migrations applied: `python manage.py migrate`
- [ ] Database contains required data (users, devices, etc.)

### Authentication
- [ ] `LOGIN_ENDPOINT` has `@csrf_exempt` decorator
- [ ] `TOKEN_REFRESH_ENDPOINT` has `csrf_exempt()` wrapper
- [ ] JWT settings configured:
  - [ ] `ACCESS_TOKEN_LIFETIME = timedelta(hours=1)`
  - [ ] `REFRESH_TOKEN_LIFETIME = timedelta(days=7)`
  - [ ] `ALGORITHM = 'HS256'`

### Static & Media Files
- [ ] `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- [ ] WhiteNoise middleware enabled in `MIDDLEWARE`
- [ ] `MEDIA_ROOT` directory exists and contains files
- [ ] All uploaded photos exist in `media/photos/`
- [ ] All generated PDFs exist in `media/pdfs/`
- [ ] Excel uploads exist in `media/excel_uploads/`

### Serializers
- [ ] `PhotoSerializer` uses `build_absolute_media_url()`
- [ ] `SubmissionSerializer` includes `pdf_url` field
- [ ] `get_pdf_url()` method uses `build_absolute_pdf_url()`
- [ ] Request context passed to serializers in views

### Views
- [ ] All API views pass `context={'request': request}` to serializers
- [ ] Error handling middleware configured
- [ ] Logging middleware configured
- [ ] Request validation middleware configured

---

## Frontend Configuration

### React Environment
- [ ] `.env.production` exists with:
  ```
  REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
  REACT_APP_ENV=production
  GENERATE_SOURCEMAP=false
  ```
- [ ] `REACT_APP_API_URL` points to Render backend
- [ ] No hardcoded `localhost` URLs in code

### API Configuration
- [ ] `auth.js` uses `process.env.REACT_APP_API_URL`
- [ ] `host.js` uses `process.env.REACT_APP_API_URL`
- [ ] `technician.js` uses `process.env.REACT_APP_API_URL`
- [ ] `supervisor.js` uses `process.env.REACT_APP_API_URL`
- [ ] All API calls use correct baseURL

### Components
- [ ] `SubmissionDetail.jsx` uses `MediaImage` component
- [ ] `SubmissionDetail.jsx` uses `ensureAbsoluteUrl()` for PDFs
- [ ] `SubmissionList.jsx` displays media correctly
- [ ] `MediaImage` component handles loading and error states
- [ ] All image URLs are absolute (start with `http://` or `https://`)

### Build Configuration
- [ ] `package.json` has correct build script
- [ ] `public/index.html` has correct base tag (if needed)
- [ ] No console errors or warnings (except ESLint warnings)
- [ ] All dependencies in `package.json` are up to date

---

## Code Quality

### Backend
- [ ] No syntax errors: `python -m py_compile backend/**/*.py`
- [ ] No import errors: `python manage.py check`
- [ ] Database migrations clean: `python manage.py showmigrations`
- [ ] No hardcoded credentials in code
- [ ] No debug print statements in production code

### Frontend
- [ ] No console errors when building: `npm run build`
- [ ] No hardcoded API URLs (use environment variables)
- [ ] No hardcoded credentials in code
- [ ] All imports resolved correctly
- [ ] No unused variables (except allowed ESLint warnings)

---

## Security

### Backend
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` is restrictive (not `*`)
- [ ] `CORS_ALLOW_ALL_ORIGINS = False`
- [ ] CSRF protection enabled (except for JWT endpoints)
- [ ] Password validation enabled
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection headers set
- [ ] HTTPS enforced in production

### Frontend
- [ ] No sensitive data in localStorage (except JWT tokens)
- [ ] No API keys in client-side code
- [ ] HTTPS enforced for all API calls
- [ ] Content Security Policy headers configured (if applicable)
- [ ] No eval() or dangerous functions used

---

## Testing

### Backend API
- [ ] Login endpoint works: `POST /api/auth/login/`
- [ ] Token refresh works: `POST /api/auth/refresh/`
- [ ] Get submissions works: `GET /api/supervisor/submissions`
- [ ] Get submission detail works: `GET /api/supervisor/submissions/{id}`
- [ ] PDF preview works: `POST /api/supervisor/submissions/{id}/preview-pdf`
- [ ] All responses include absolute media URLs
- [ ] CORS headers present in responses
- [ ] No 400/403/500 errors for valid requests

### Frontend
- [ ] Login page loads
- [ ] Login succeeds with correct credentials
- [ ] Dashboard loads after login
- [ ] Submissions list displays
- [ ] Submission detail displays with photos
- [ ] Images load without 404 errors
- [ ] PDF preview opens in new tab
- [ ] No console errors or CORS warnings
- [ ] Responsive design works on mobile

### Media Files
- [ ] All photos display correctly
- [ ] All PDFs open without errors
- [ ] Media URLs are absolute (point to Render backend)
- [ ] No broken image links
- [ ] No missing PDF files

---

## Deployment Files

### React Build
- [ ] `build/` folder exists
- [ ] `build/index.html` exists
- [ ] `build/static/js/` contains bundled JavaScript
- [ ] `build/static/css/` contains bundled CSS
- [ ] `build/favicon.ico` exists
- [ ] Build size is reasonable (< 5 MB gzipped)

### Django Static Files
- [ ] `staticfiles/` folder exists
- [ ] `staticfiles/admin/` exists
- [ ] `staticfiles/rest_framework/` exists
- [ ] All CSS and JS files collected

### Media Files
- [ ] `media/` folder exists
- [ ] `media/photos/` contains all photos
- [ ] `media/pdfs/` contains all PDFs
- [ ] `media/excel_uploads/` contains all Excel files
- [ ] `media.zip` created successfully
- [ ] `media.zip` contains correct folder structure

---

## Git Repository

- [ ] All changes committed: `git status` shows clean working tree
- [ ] Sensitive files in `.gitignore`:
  - [ ] `.env` (local development)
  - [ ] `*.pyc`
  - [ ] `__pycache__/`
  - [ ] `node_modules/`
  - [ ] `build/`
  - [ ] `staticfiles/`
  - [ ] `media/` (optional, if not tracking)
- [ ] Latest changes pushed to GitHub: `git push origin main`
- [ ] No merge conflicts
- [ ] Branch is up to date with remote

---

## Hostinger Preparation

### Domain Configuration
- [ ] Domain `amanisafi.com` points to Hostinger
- [ ] SSL certificate installed and valid
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] DNS records configured correctly

### File Structure
- [ ] `/public_html/` directory accessible
- [ ] FTP/SSH access working
- [ ] File upload permissions correct
- [ ] `.htaccess` support enabled

### Environment
- [ ] Node.js available (if needed for build)
- [ ] PHP version compatible (if needed)
- [ ] Disk space sufficient (> 1 GB)
- [ ] Bandwidth sufficient

---

## Render Preparation

### Service Configuration
- [ ] Service name: `atm-maintenance`
- [ ] GitHub repository connected
- [ ] Auto-deploy on push enabled
- [ ] Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- [ ] Start command: `gunicorn atm_backend.wsgi:application`

### Environment Variables
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] `DATABASE_URL` set to PostgreSQL connection string
- [ ] `SECRET_KEY` set to strong value
- [ ] `CORS_ALLOWED_ORIGINS` includes Hostinger domain
- [ ] `MEDIA_BASE_URL=https://atm-maintenance.onrender.com`

### Database
- [ ] PostgreSQL service created
- [ ] Database connection string verified
- [ ] Backups enabled
- [ ] Migrations applied

---

## Final Verification

### Before Deployment
- [ ] All checklist items marked complete
- [ ] No outstanding bugs or issues
- [ ] Code reviewed and tested
- [ ] Deployment plan documented
- [ ] Rollback procedure documented

### Deployment Day
- [ ] Backup taken of current production
- [ ] Deployment window scheduled
- [ ] Team notified of deployment
- [ ] Monitoring tools ready
- [ ] Support team on standby

### Post-Deployment
- [ ] Frontend loads at https://amanisafi.com
- [ ] Backend API responds at https://atm-maintenance.onrender.com/api
- [ ] Login works without errors
- [ ] Media files display correctly
- [ ] No console errors or warnings
- [ ] Performance acceptable
- [ ] All features working as expected

---

## Sign-Off

**Prepared by:** ___________________  
**Date:** ___________________  
**Approved by:** ___________________  
**Deployment Date:** ___________________  

---

## Notes

```
[Add any additional notes or observations here]
```

---

**Last Updated:** November 8, 2025  
**Version:** 1.0
