# Quick Deployment Reference Card

## One-Command Deployment (Automated)

### Windows (PowerShell)
```powershell
.\DEPLOY_PRODUCTION.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x deploy_production.sh
./deploy_production.sh
```

**What it does:**
- ✅ Builds React frontend
- ✅ Collects Django static files
- ✅ Packages media files
- ✅ Verifies all deployment files

---

## Manual Deployment Steps

### 1. Build React
```bash
cd frontend/atm_frontend
npm install
npm run build
```
**Output:** `build/` folder

### 2. Collect Static Files
```bash
cd backend
python manage.py collectstatic --noinput --clear
```
**Output:** `staticfiles/` folder

### 3. Package Media
```bash
cd backend
zip -r ../media.zip media/
```
**Output:** `media.zip` file

### 4. Push to GitHub
```bash
git add .
git commit -m "Production build ready"
git push origin main
```

### 5. Deploy Backend
- Go to https://dashboard.render.com
- Click "Manual Deploy"
- Wait 5-10 minutes

### 6. Deploy Frontend
- Download `build/` folder
- Upload to Hostinger `/public_html/`
- Verify `.htaccess` is present

### 7. Upload Media
- Download `media.zip`
- Upload to Hostinger `/public_html/`
- Extract and verify

---

## Verification Commands

### Backend
```bash
# Test API
curl https://atm-maintenance.onrender.com/api/supervisor/submissions

# Check logs
# Go to: https://dashboard.render.com → Logs
```

### Frontend
```bash
# Test frontend
curl https://amanisafi.com

# Check browser console (F12)
# Look for errors or CORS warnings
```

### Media
```bash
# Verify media files
ls -la /public_html/media/

# Check image URL
curl https://amanisafi.com/media/photos/[filename]
```

---

## Environment Variables

### Backend `.env`
```
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,aroundh-ksa.com,www.aroundh-ksa.com,atm-maintenance.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://amanisafi.com,https://www.amanisafi.com
DATABASE_URL=postgresql://...
MEDIA_BASE_URL=https://atm-maintenance.onrender.com
```

### Frontend `.env.production`
```
REACT_APP_API_URL=https://atm-maintenance.onrender.com/api
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Blank page** | Check `.htaccess`, verify `build/index.html` exists |
| **CORS error** | Add domain to `CORS_ALLOWED_ORIGINS`, restart Render |
| **404 images** | Upload `media/` folder to Hostinger |
| **Login fails** | Check `ALLOWED_HOSTS`, verify `@csrf_exempt` on login |
| **API 500 error** | Check Render logs, verify database connection |
| **Build fails** | Run `npm install`, check Node version |

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| React build | `frontend/atm_frontend/build/` | Upload to Hostinger |
| Media ZIP | `media.zip` (project root) | Upload to Hostinger |
| Static files | `backend/staticfiles/` | Served by Render |
| Backend .env | `backend/.env` | Production config |
| Frontend .env | `frontend/atm_frontend/.env.production` | Production config |

---

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | https://amanisafi.com | User interface |
| Backend API | https://atm-maintenance.onrender.com/api | API endpoints |
| Admin Panel | https://atm-maintenance.onrender.com/admin | Django admin |
| Render Dashboard | https://dashboard.render.com | Deployment management |

---

## Deployment Checklist (Quick)

- [ ] Backend `.env` has `DEBUG=False`
- [ ] Frontend `.env.production` has correct API URL
- [ ] React build created: `npm run build`
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Media files packaged: `zip -r media.zip media/`
- [ ] Changes pushed to GitHub
- [ ] Render deployment triggered
- [ ] Build folder uploaded to Hostinger
- [ ] Media files uploaded to Hostinger
- [ ] `.htaccess` configured on Hostinger
- [ ] Frontend loads at https://amanisafi.com
- [ ] Login works without errors
- [ ] API requests go to Render backend
- [ ] Images and PDFs load correctly

---

## Common Commands

```bash
# Build frontend
npm run build

# Collect static files
python manage.py collectstatic --noinput --clear

# Package media
zip -r media.zip media/

# Test API
curl -X GET https://atm-maintenance.onrender.com/api/supervisor/submissions

# SSH to Hostinger
ssh username@amanisafi.com

# Upload files via SCP
scp -r build/* username@amanisafi.com:/home/username/public_html/

# Extract ZIP on Hostinger
unzip media.zip
```

---

## Emergency Rollback

### Rollback Frontend
```bash
# SSH to Hostinger
ssh username@amanisafi.com

# Restore from backup
cp -r backup/build/* public_html/
```

### Rollback Backend
1. Go to https://dashboard.render.com
2. Click "Deployments"
3. Select previous version
4. Click "Redeploy"

---

## Support

- **Render Docs:** https://render.com/docs
- **Hostinger Support:** https://www.hostinger.com/support
- **Django Docs:** https://docs.djangoproject.com
- **React Docs:** https://react.dev

---

**Last Updated:** November 8, 2025
