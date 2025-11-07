# Render Backend Deployment Steps

## Overview
Deploy Django backend to Render with PostgreSQL database, environment variables, and auto-deploy from GitHub.

---

## Step 1: Create Render Account & Connect GitHub

1. Go to [render.com](https://render.com) and sign up.
2. Connect your GitHub account (Settings → Integrations).
3. Authorize Render to access your repository.

---

## Step 2: Create PostgreSQL Database

1. In Render dashboard, click **New +** → **PostgreSQL**.
2. Configure:
   - **Name**: `atm-db`
   - **Database**: `atm_db_tf06`
   - **User**: `atm_db_tf06_user`
   - **Region**: Frankfurt (or your preferred region)
   - **Plan**: Free tier (or paid if needed)
3. Click **Create Database**.
4. **Copy the Internal Database URL** (looks like `postgresql://user:pass@host:5432/db`).
   - This will be used as `DATABASE_URL` environment variable.

---

## Step 3: Create Web Service

1. Click **New +** → **Web Service**.
2. Select your GitHub repository (atm-maintenance-system).
3. Configure:
   - **Name**: `atm-maintenance`
   - **Environment**: Python 3
   - **Region**: Frankfurt
   - **Branch**: main (or your deployment branch)
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```
     cd backend && gunicorn atm_backend.wsgi:application
     ```
   - **Plan**: Free (or Starter for production)

4. Click **Create Web Service**.

---

## Step 4: Add Environment Variables

In the Web Service dashboard, go to **Environment** and add:

| Key | Value | Notes |
|-----|-------|-------|
| `DEBUG` | `False` | Must be False in production |
| `SECRET_KEY` | `<your-generated-key>` | Already set; do not change |
| `ALLOWED_HOSTS` | `atm-maintenance.onrender.com,aroundh-ksa.com` | Render domain + custom domain |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` | From PostgreSQL instance |
| `CORS_ALLOWED_ORIGINS` | `https://aroundh-ksa.com` | HostGator frontend domain |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Restrict to specific origins |
| `CSRF_TRUSTED_ORIGINS` | `https://aroundh-ksa.com` | HostGator frontend domain |
| `EMAIL_HOST` | `smtp.gmail.com` | Gmail SMTP server |
| `EMAIL_PORT` | `587` | Gmail SMTP port |
| `EMAIL_USE_TLS` | `True` | Enable TLS for Gmail |
| `EMAIL_HOST_USER` | `<your_email@gmail.com>` | Gmail address |
| `EMAIL_HOST_PASSWORD` | `<app-password>` | Gmail App Password (not regular password) |
| `DEFAULT_FROM_EMAIL` | `yossefhaddad20@gmail.com` | Sender email address |

**Important**: Use Gmail App Password, not your regular password. [Generate one here](https://support.google.com/accounts/answer/185833).

---

## Step 5: Deploy & Run Migrations

1. **First Deploy**: Render automatically deploys when you push to the main branch.
   - Monitor the **Logs** tab for build progress.
   - Wait for "Build successful" message.

2. **Run Migrations** (via Render Shell):
   - In the Web Service dashboard, click **Shell**.
   - Run:
     ```bash
     python manage.py migrate
     ```
   - Output should show: `Running migrations: ... OK`

3. **Create Superuser** (optional, for admin access):
   - In the Shell, run:
     ```bash
     python manage.py createsuperuser
     ```
   - Follow prompts to create admin account.

4. **Collect Static Files** (if not done in build):
   - In the Shell, run:
     ```bash
     python manage.py collectstatic --noinput
     ```

---

## Step 6: Verify Deployment

1. **Check Render URL**: Visit `https://atm-maintenance.onrender.com`
   - Should see Django 404 page (expected, no root route).

2. **Test Admin Interface**: Visit `https://atm-maintenance.onrender.com/admin`
   - Should load Django admin login page.

3. **Test API Endpoint**: Visit `https://atm-maintenance.onrender.com/api/submissions`
   - Should return JSON (or 401 if authentication required).

4. **Check Logs**: In Render dashboard, monitor **Logs** for errors.

---

## Step 7: Connect Custom Domain (Optional)

1. In Render Web Service, go to **Settings** → **Custom Domains**.
2. Add your domain: `api.aroundh-ksa.com` (or subdomain of choice).
3. Update your DNS records (CNAME) to point to Render.
4. Wait for DNS propagation (5–30 minutes).

---

## Step 8: Enable Auto-Deploy

1. In Web Service settings, **Auto-Deploy** is enabled by default.
2. Every push to the main branch triggers a new deployment.
3. Monitor **Deployments** tab to see build history.

---

## Troubleshooting

### Build Fails
- Check **Build Logs** for errors.
- Verify `requirements.txt` has all dependencies.
- Ensure `manage.py` is in the `backend/` directory.

### Database Connection Error
- Verify `DATABASE_URL` is correct in Environment Variables.
- Check PostgreSQL instance is running (green status in Render).
- Run `python manage.py dbshell` in Shell to test connection.

### Static Files Not Loading
- Run `python manage.py collectstatic --noinput` in Shell.
- Verify `STATIC_ROOT` and `STATICFILES_STORAGE` in `settings.py`.

### CORS Errors
- Check `CORS_ALLOWED_ORIGINS` matches HostGator domain exactly.
- Ensure `CORS_ALLOW_ALL_ORIGINS=False` in production.

### Email Not Sending
- Verify Gmail App Password (not regular password).
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set.
- Test with: `python manage.py shell` → `from django.core.mail import send_mail; send_mail(...)`

---

## Post-Deployment Checklist

- [ ] PostgreSQL database created and running.
- [ ] Web Service deployed successfully.
- [ ] Environment variables set correctly.
- [ ] Migrations run without errors.
- [ ] Admin interface accessible.
- [ ] API endpoints responding.
- [ ] CORS configured for HostGator domain.
- [ ] Email sending verified.
- [ ] Logs monitored for errors.
- [ ] Auto-deploy enabled.
- [ ] Custom domain configured (if applicable).

---

## Useful Commands (Render Shell)

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test database connection
python manage.py dbshell

# Run Django shell
python manage.py shell

# Check environment variables
env | grep -E "DEBUG|DATABASE_URL|SECRET_KEY"
```

---

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- PostgreSQL on Render: https://render.com/docs/databases
