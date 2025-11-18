# Post-Deployment Operations

## 1. Automation & Releases
- Enable auto-deploy on Render for `main` branch (if disabled).
- Set up GitHub Action (or manual SOP) to rebuild frontend and upload to HostGator when `frontend/` changes.
- Tag production releases in Git for traceability.

## 2. Monitoring & Alerts
- Check Render metrics dashboard (CPU, memory, response time) after each deploy.
- Configure Render deploy failure notifications to email.
- Install browser-side error tracking (e.g., Sentry) for frontend (optional).

## 3. Backups & Data Safety
- Schedule Render PostgreSQL backups (Snapshot or external `pg_dump` cron).
- Store backup restoration commands in `DB_RESTORE_INSTRUCTIONS.md` (recommended addition).
- Periodically export critical media/pdf files if stored locally on Render.

## 4. Security Hardening
- Rotate `SECRET_KEY`, DB passwords, and Gmail App Password every quarter.
- Enforce HTTPS redirects on both HostGator and Render domains (already configured, verify monthly).
- Review Django admin users and permissions after each staffing change.

## 5. Documentation & SOPs
- Keep `RENDER_DEPLOYMENT_EXECUTION.md`, `HOSTGATOR_DEPLOYMENT_STEPS.md`, and `DEPLOYMENT_VERIFICATION_CHECKLIST.md` up to date after process tweaks.
- Document contact points (who can access Render/HostGator) and store securely.

## 6. Incident Response
- Define escalation path for API downtime (Render status page, fallback email channel).
- Maintain changelog for production incidents and fixes.

## 7. Periodic Tasks
- Monthly: run full regression test pass using checklist in `MANUAL_TEST_CHECKLIST.md`.
- Quarterly: review CORS/CSRF allowed origin lists to ensure only active domains remain.
- Before big updates: create maintenance window plan and inform stakeholders.
