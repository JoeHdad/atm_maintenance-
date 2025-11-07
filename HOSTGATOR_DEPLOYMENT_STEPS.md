# HostGator Frontend Deployment Steps

## Overview
Deploy React production build to HostGator static hosting with proper routing configuration.

---

## Step 1: Build React App for Production

1. Navigate to frontend directory:
   ```bash
   cd frontend/atm_frontend
   ```

2. Create `.env.production` file with production API URL:
   ```
   REACT_APP_API_BASE_URL=https://atm-maintenance.onrender.com
   REACT_APP_ENV=production
   ```

3. Install dependencies (if not already done):
   ```bash
   npm install
   ```

4. Build production bundle:
   ```bash
   npm run build
   ```

5. Verify build output:
   - Check `build/` folder exists.
   - Confirm `build/index.html` is present.
   - Build should complete with no errors.

---

## Step 2: Prepare HostGator Account

1. Log in to HostGator cPanel.
2. Ensure your domain is pointing to HostGator servers (DNS A record).
3. Verify SSL certificate is installed (AutoSSL or Let's Encrypt).
   - Go to **SSL/TLS Status** in cPanel.
   - If not installed, click **Auto SSL** to generate.

---

## Step 3: Upload Build to HostGator

### Option A: File Manager Upload (Recommended)

1. In cPanel, go to **Files** → **File Manager**.
2. Navigate to `public_html` (or your domain's root directory).
3. If deploying to a subdomain (e.g., `www.aroundh-ksa.com`), stay in `public_html`.
4. Click **Upload** in the top menu.
5. Upload the entire `build/` folder contents (or zip the `build` folder first and extract on server).
6. Ensure all files are uploaded (HTML, CSS, JS, assets).
7. Confirm `index.html` is at the root level.

### Option B: FTP Upload

1. Use FileZilla or another FTP client.
2. Connect to your HostGator FTP server.
3. Upload `build/` contents to `public_html/`.
4. Verify all files uploaded successfully.

---

## Step 4: Configure React Router (SPA Routing)

Since React Router handles client-side routing, create a `.htaccess` file to redirect all requests to `index.html`:

1. In File Manager, create a new file named `.htaccess` in `public_html/`.
2. Add this content:

   ```
   RewriteEngine On
   RewriteBase /
   RewriteRule ^index\.html$ - [L]
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule . /index.html [L]

   # Security headers (optional but recommended)
   <IfModule mod_headers.c>
     Header always set X-Frame-Options DENY
     Header always set X-Content-Type-Options nosniff
     Header always set Referrer-Policy strict-origin-when-cross-origin
   </IfModule>
   ```

3. Save the file.
4. Test by visiting a direct route (e.g., `https://aroundh-ksa.com/technician/dashboard`) - should load the React app, not a 404.

---

## Step 5: Force HTTPS (Security)

1. In cPanel, go to **Domains** → **Redirects**.
2. Create a redirect:
   - **Type**: Permanent (301)
   - **Domain**: aroundh-ksa.com (or your domain)
   - **Redirects to**: `https://aroundh-ksa.com`
   - **www. redirection**: Choose based on your preference
   - **Wild Card Redirect**: Checked

3. Alternatively, use `.htaccess` for HTTPS redirect:

   ```
   RewriteCond %{HTTPS} off
   RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
   ```

---

## Step 6: Verify Deployment

1. Visit your domain: `https://aroundh-ksa.com`
   - Should load the React app homepage.
   - Check browser console for API errors (should show CORS or 404 if backend not ready).

2. Test navigation:
   - Click links/routes - should work without page reloads.
   - Try direct URLs - should load the app (thanks to `.htaccess`).

3. Check assets:
   - Images, CSS, JS should load (no 404s).
   - Verify in browser Network tab.

4. Test API communication:
   - Perform login or data fetch - should call Render backend.
   - Check Network tab for successful API calls to `https://atm-maintenance.onrender.com/*`.

---

## Step 7: Auto-Deploy Setup (Optional)

For automatic updates when code changes:

1. Set up a CI/CD pipeline (e.g., GitHub Actions) to:
   - Build React app on push to main branch.
   - Upload build files to HostGator via FTP or API.

2. HostGator doesn't provide direct API for file uploads, so use:
   - FTP with credentials stored in CI secrets.
   - Or deploy to Netlify/Vercel and use HostGator for domain redirect.

3. Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

   ```yaml
   name: Deploy Frontend
   on:
     push:
       branches: [ main ]
       paths: [ 'frontend/**' ]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Setup Node
           uses: actions/setup-node@v3
           with:
             node-version: '18'
         - name: Install dependencies
           run: |
             cd frontend/atm_frontend
             npm install
         - name: Build
           run: |
             cd frontend/atm_frontend
             npm run build
           env:
             REACT_APP_API_BASE_URL: https://atm-maintenance.onrender.com
         - name: Deploy to HostGator
           uses: SamKirkland/FTP-Deploy-Action@v4.3.3
           with:
             server: ${{ secrets.FTP_SERVER }}
             username: ${{ secrets.FTP_USERNAME }}
             password: ${{ secrets.FTP_PASSWORD }}
             local-dir: ./frontend/atm_frontend/build/
             server-dir: /public_html/
   ```

---

## Troubleshooting

### 404 on Direct Routes
- Check `.htaccess` file exists and has correct rewrite rules.
- Ensure `mod_rewrite` is enabled in Apache.

### HTTPS Not Working
- Verify SSL certificate is active in cPanel.
- Check `.htaccess` for HTTPS redirect rules.

### Assets Not Loading
- Confirm all files uploaded to correct directory.
- Check file permissions (should be 644 for files, 755 for directories).

### API Calls Failing
- Check CORS settings in Django (should allow `https://aroundh-ksa.com`).
- Verify `REACT_APP_API_BASE_URL` is set correctly.

### Build Errors
- Run `npm install` before build.
- Check console for dependency issues.
- Ensure Node version matches your development environment.

---

## Post-Deployment Checklist

- [ ] React app built successfully (`npm run build`).
- [ ] `.env.production` created with correct API URL.
- [ ] Build files uploaded to `public_html/`.
- [ ] `.htaccess` file created with rewrite rules.
- [ ] HTTPS redirect configured.
- [ ] Domain resolves to HostGator.
- [ ] React app loads on domain.
- [ ] Client-side routing works (no 404s).
- [ ] API calls reach Render backend.
- [ ] SSL certificate active.
- [ ] No console errors in browser.

---

## Useful Commands

```bash
# Build React app
cd frontend/atm_frontend
npm install
npm run build

# Test build locally (optional)
npx serve -s build

# Check build contents
ls -la frontend/atm_frontend/build/
```

---

## Support

- HostGator Docs: https://www.hostgator.com/help
- React Deployment: https://create-react-app.dev/docs/deployment/
- Apache .htaccess: https://httpd.apache.org/docs/2.4/howto/htaccess.html
