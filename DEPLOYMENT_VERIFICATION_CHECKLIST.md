# Deployment Verification Checklist

Use this list after deploying both backend (Render) and frontend (HostGator).

## 1. Backend (Render)
- [ ] Visit `https://atm-maintenance.onrender.com/admin` → Django admin loads over HTTPS.
- [ ] Run `python manage.py migrate` in Render shell without errors.
- [ ] Run `python manage.py createsuperuser` (if not already created).
- [ ] Check Render logs: no errors after deployment.

## 2. Frontend (HostGator)
- [ ] Visit `https://aroundh-ksa.com` → React app loads without mixed-content warnings.
- [ ] Reload using direct routes (e.g., `/technician/dashboard`) → No 404 thanks to `.htaccess`.
- [ ] Browser console clean (no uncaught errors or CORS warnings).

## 3. API Communication
- [ ] From `https://aroundh-ksa.com`, login and perform key flows → API calls hit Render domain successfully.
- [ ] Check browser Network tab: requests to `https://atm-maintenance.onrender.com` return expected data/status.
- [ ] Verify JWT/auth flows (login, logout, refresh) operate normally.

## 4. HTTPS & Certificates
- [ ] Confirm SSL certificate valid for `aroundh-ksa.com` (padlock icon, no warnings).
- [ ] Confirm Render auto-HTTPS redirect working (hitting `http://atm-maintenance.onrender.com` redirects to HTTPS).

## 5. File Uploads & Downloads
- [ ] Upload a sample report/photo via frontend → succeeds, appears in backend.
- [ ] Download generated PDF/email attachment → correct filename, contents verify.
- [ ] Check Render logs for upload handling errors.

## 6. CORS & CSRF
- [ ] Requests from HostGator domain succeed; no `CORS policy` errors in console.
- [ ] API requests from other domains blocked (use browser devtools or curl to confirm).

## 7. Logging & Monitoring
- [ ] Monitor Render logs for 10–15 minutes post-deploy → no unexpected errors.
- [ ] Verify log files (`logs/error.log`, `logs/api.log`) are populated as expected.

## 8. Backup & Recovery
- [ ] Create initial database backup after migrations (Render DB snapshot or `pg_dump`).
- [ ] Document restoration steps in project wiki/README.

## 9. Stakeholder Sign-off
- [ ] Share deployment URLs with stakeholders for UAT.
- [ ] Collect approval/feedback and track issues.
