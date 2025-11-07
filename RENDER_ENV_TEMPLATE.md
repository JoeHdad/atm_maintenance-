# Render Environment Variables Template

Set these environment variables in Render dashboard for the Django backend:

```
# Django Core
DEBUG=False
SECRET_KEY=<generate-new-secure-key>
ALLOWED_HOSTS=<your-render-app>.onrender.com,<custom-api-domain>

# Database (Render PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<postgres-db-name>
DB_USER=<postgres-user>
DB_PASSWORD=<postgres-password>
DB_HOST=<render-postgres-host>
DB_PORT=5432

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://<your-hostgator-domain>
CORS_ALLOW_ALL_ORIGINS=False
CSRF_TRUSTED_ORIGINS=https://<your-hostgator-domain>

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<your-app-password>
DEFAULT_FROM_EMAIL=<your-email@gmail.com>

# Media Root (optional, if using local storage)
MEDIA_ROOT=/var/data/media
```

**Notes:**
- Generate `SECRET_KEY` using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.
- Replace placeholders with actual values before deployment.
