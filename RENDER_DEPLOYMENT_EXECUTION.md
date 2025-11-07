# Render Deployment Execution Guide

## Overview
This guide walks through the automated deployment of the Django backend to Render using `render.yaml` configuration.

---

## Prerequisites

✅ Completed:
- Django settings configured for production (`DEBUG=False`, PostgreSQL, WhiteNoise).
- `requirements.txt` updated with `gunicorn` and `whitenoise`.
- `render.yaml` created with service and database configuration.
- Environment variables prepared and added to Render dashboard.
- GitHub repository connected to Render.

---

## Step 1: Verify GitHub Repository Setup

1. Ensure your repository is pushed to GitHub (main branch).
2. Confirm `render.yaml` is in the root directory of the repository.
3. Verify the following files exist:
   - `backend/requirements.txt` — with all dependencies.
   - `backend/atm_backend/settings.py` — production-ready config.
   - `backend/manage.py` — Django management script.
   - `backend/atm_backend/wsgi.py` — WSGI application entry point.

**Command to verify:**
```bash
git log --oneline -1
git ls-files | grep -E "render.yaml|backend/requirements.txt|backend/manage.py"
```

---

## Step 2: Create Render Account & Connect GitHub

1. Go to [render.com](https://render.com).
2. Sign up with GitHub account (or link existing account).
3. Authorize Render to access your GitHub repositories.
4. Verify connection in Render dashboard: **Settings** → **Integrations** → **GitHub**.

---

## Step 3: Deploy Using render.yaml

### Option A: Deploy from Render Dashboard (Recommended)

1. In Render dashboard, click **New +** → **Web Service**.
2. Select your GitHub repository: `atm-maintenance-system`.
3. Render will auto-detect `render.yaml` and pre-fill configuration.
4. Review settings:
   - **Name**: `atm-maintenance`
   - **Environment**: Python
   - **Region**: Frankfurt
   - **Build Command**: `pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput`
   - **Start Command**: `cd backend && gunicorn atm_backend.wsgi:application`
5. Click **Create Web Service**.

### Option B: Deploy from CLI (Advanced)

```bash
# Install Render CLI
npm install -g @render-oss/render-cli

# Login to Render
render login

# Deploy using render.yaml
render deploy --file render.yaml
```

---

## Step 4: Monitor Initial Deployment

1. In Render dashboard, go to **Deployments** tab.
2. Watch the build process:
   - **Build Phase**: Installing dependencies, collecting static files.
   - **Deploy Phase**: Starting Gunicorn server.
3. Check **Logs** for any errors:
   - Look for "Build successful" message.
   - Confirm Gunicorn started on port 10000 (Render default).

**Expected log output:**
```
[2025-11-07 14:00:00] Building...
[2025-11-07 14:02:15] Collecting static files...
[2025-11-07 14:02:30] Build successful
[2025-11-07 14:02:35] Starting service...
[2025-11-07 14:02:40] Gunicorn started on 0.0.0.0:10000
```

---

## Step 5: Run Database Migrations

After deployment succeeds:

1. In Render Web Service dashboard, click **Shell** (top right).
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Expected output:
   ```
   Running migrations:
     Applying core.0001_initial... OK
     Applying core.0002_...
     ...
   ```

4. Create superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```
   - Follow prompts to create admin account.

5. Verify static files collected:
   ```bash
   ls -la staticfiles/
   ```

---

## Step 6: Verify Backend Deployment

### Test 1: Check Service Health

```bash
curl https://atm-maintenance.onrender.com/
```

Expected: Django 404 page (no root route defined).

### Test 2: Access Admin Interface

Visit: `https://atm-maintenance.onrender.com/admin`

Expected: Django admin login page loads.

### Test 3: Test API Endpoint

```bash
curl https://atm-maintenance.onrender.com/api/submissions
```

Expected: JSON response or 401 (authentication required).

### Test 4: Check Logs for Errors

In Render dashboard, monitor **Logs** tab for:
- Database connection errors.
- Import errors.
- CORS issues.

---

## Step 7: Configure Environment Variables in Render

If not already set via `render.yaml`, add manually:

1. In Web Service dashboard, go to **Environment**.
2. Add/verify these variables:

| Key | Value |
|-----|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | `<your-generated-key>` |
| `ALLOWED_HOSTS` | `atm-maintenance.onrender.com,aroundh-ksa.com,127.0.0.1,localhost` |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` |
| `CORS_ALLOWED_ORIGINS` | `https://aroundh-ksa.com` |
| `CORS_ALLOW_ALL_ORIGINS` | `False` |
| `CSRF_TRUSTED_ORIGINS` | `https://aroundh-ksa.com` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `<your_email@gmail.com>` |
| `EMAIL_HOST_PASSWORD` | `<app-password>` |
| `DEFAULT_FROM_EMAIL` | `yossefhaddad20@gmail.com` |

3. Click **Save Changes**.
4. Render will automatically redeploy with new environment variables.

---

## Step 8: Enable Auto-Deploy

1. In Web Service dashboard, go to **Settings**.
2. Confirm **Auto-Deploy** is enabled (default).
3. Select branch: `main` (or your deployment branch).
4. Every push to the selected branch will trigger a new deployment.

---

## Step 9: Connect Custom Domain (Optional)

1. In Web Service dashboard, go to **Settings** → **Custom Domains**.
2. Add domain: `api.aroundh-ksa.com` (or subdomain of choice).
3. Update DNS records:
   - Go to your domain registrar (e.g., GoDaddy, Namecheap).
   - Add CNAME record pointing to Render service URL.
4. Wait for DNS propagation (5–30 minutes).
5. Verify: Visit `https://api.aroundh-ksa.com/admin` — should load admin page.

---

## Step 10: Monitor & Maintain

### Ongoing Monitoring

1. **Logs**: Check regularly for errors.
2. **Metrics**: Monitor CPU, memory, and response times.
3. **Alerts**: Set up email notifications for deployment failures.

### Useful Commands (Render Shell)

```bash
# Check environment variables
env | grep -E "DEBUG|DATABASE_URL|SECRET_KEY"

# Test database connection
python manage.py dbshell

# Run Django shell
python manage.py shell

# Check static files
ls -la staticfiles/

# View recent migrations
python manage.py showmigrations

# Create backup of database
pg_dump $DATABASE_URL > backup.sql
```

---

## Troubleshooting

### Build Fails

**Error**: `pip install` fails
- **Solution**: Check `requirements.txt` for syntax errors or incompatible versions.
- **Action**: Run locally: `pip install -r backend/requirements.txt`

**Error**: `collectstatic` fails
- **Solution**: Ensure `STATIC_ROOT` is set in `settings.py`.
- **Action**: Check `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`

### Database Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`
- **Solution**: Verify `DATABASE_URL` is correct.
- **Action**: In Render Shell, run: `python manage.py dbshell`

### CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`
- **Solution**: Verify `CORS_ALLOWED_ORIGINS` includes frontend domain.
- **Action**: Check Render environment variables match `settings.py` config.

### Static Files Not Loading

**Error**: CSS/JS returning 404
- **Solution**: Ensure `collectstatic` ran during build.
- **Action**: In Render Shell, run: `python manage.py collectstatic --noinput`

### Email Not Sending

**Error**: `SMTPAuthenticationError`
- **Solution**: Verify Gmail App Password (not regular password).
- **Action**: Generate new App Password at https://support.google.com/accounts/answer/185833

---

## Post-Deployment Checklist

- [ ] GitHub repository connected to Render.
- [ ] `render.yaml` in repository root.
- [ ] Web Service deployed successfully.
- [ ] PostgreSQL database created and running.
- [ ] Migrations run without errors.
- [ ] Superuser created (if needed).
- [ ] Admin interface accessible.
- [ ] API endpoints responding.
- [ ] Environment variables set correctly.
- [ ] CORS configured for frontend domain.
- [ ] Auto-deploy enabled.
- [ ] Custom domain configured (if applicable).
- [ ] Logs monitored for errors.
- [ ] Email sending tested.

---

## Next Steps

After backend deployment is verified:
1. Proceed to **Step 5: Deploy React Frontend on HostGator**.
2. Build React app with `REACT_APP_API_BASE_URL=https://atm-maintenance.onrender.com`.
3. Upload build to HostGator `public_html/`.
4. Configure `.htaccess` for React Router.
5. Test end-to-end API communication.

---

## Support & Resources

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Gunicorn: https://gunicorn.org/
- PostgreSQL: https://www.postgresql.org/docs/
