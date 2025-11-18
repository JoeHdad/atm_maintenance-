# How to Send Test Email to yossefhaddad20@gmail.com

## 🎯 Quick Start

A dedicated test script is ready to send an actual email with PDF attachment to `yossefhaddad20@gmail.com`.

---

## 📋 Prerequisites

You need Gmail credentials to send emails. Follow these steps:

### **Step 1: Get Gmail App Password**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. You may need to enable **2-Step Verification** first
4. Click **"Select app"** → Choose **"Mail"**
5. Click **"Select device"** → Choose **"Other"** → Type "ATM System"
6. Click **"Generate"**
7. Copy the **16-character password** (e.g., `abcd efgh ijkl mnop`)

**Important:** Use the App Password, NOT your regular Gmail password!

---

### **Step 2: Update .env File**

Open: `backend/.env`

Update these two lines:

```env
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

**Example:**
```env
EMAIL_HOST_USER=myemail@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

**Note:** Remove spaces from the App Password!

---

### **Step 3: Run Test Script**

```bash
cd backend
python send_test_email.py
```

---

## 🚀 What the Script Does

1. ✅ Checks email configuration
2. ✅ Finds a test submission
3. ✅ Generates PDF if needed
4. ✅ Shows email preview
5. ✅ Asks for confirmation
6. ✅ Sends email to `yossefhaddad20@gmail.com`
7. ✅ Reports success/failure

---

## 📧 Email Content

**To:** yossefhaddad20@gmail.com

**Subject:** ATM Electrical Report – GFM1190967 – Half 1

**Body:** Professional email with:
- ATM details (ID, Cost Center, City)
- Technician information
- Visit and submission dates
- Status

**Attachment:** PDF report (~3 MB)
- Cover page
- Section 1, 2, 3 photos
- Preventive cleaning checklist

---

## ✅ Expected Output

```
================================================
EMAIL SENDING TEST - ACTUAL EMAIL TO yossefhaddad20@gmail.com
================================================

📧 Current Email Configuration:
   Host: smtp.gmail.com
   Port: 587
   From: noreply@atm-maintenance.com
   To: yossefhaddad20@gmail.com
   User: myemail@gmail.com

✅ Email credentials configured!

================================================
📄 Preparing Test Submission
================================================

✅ Found Submission:
   ID: 1
   Device: GFM1190967
   Cost Center: 8565
   Technician: hary
   Status: Approved

✅ PDF already exists: media/pdfs/1/report_GFM1190967_20251025_100604.pdf
   PDF Size: 2.96 MB

================================================
📧 READY TO SEND EMAIL
================================================

   From: noreply@atm-maintenance.com
   To: yossefhaddad20@gmail.com
   Subject: ATM Electrical Report – GFM1190967 – Half 1
   Attachment: ATM_Report_GFM1190967_20251025.pdf (2.96 MB)

================================================
⚠️  Do you want to send this email? (yes/no): yes
================================================

🔄 Sending email...
   This may take a few seconds...

================================================
📊 EMAIL SENDING RESULT
================================================

✅ ✅ ✅ EMAIL SENT SUCCESSFULLY! ✅ ✅ ✅

   Message: Email sent successfully to 1 recipient(s)
   Recipients: yossefhaddad20@gmail.com

📬 Please check the inbox at: yossefhaddad20@gmail.com
   (Check spam folder if not in inbox)

================================================
```

---

## 🔧 Troubleshooting

### **Error: "Username and Password not accepted"**

**Solution:**
- Make sure you're using **App Password**, not regular password
- Enable **2-Step Verification** in Gmail
- Generate a new App Password
- Remove spaces from the password in `.env`

---

### **Error: "Connection refused"**

**Solution:**
- Check your internet connection
- Verify firewall settings
- Confirm SMTP settings: `smtp.gmail.com:587`

---

### **Email not received**

**Check:**
1. Spam/Junk folder
2. Gmail account is correct: `yossefhaddad20@gmail.com`
3. Script showed "EMAIL SENT SUCCESSFULLY"
4. Wait a few minutes (sometimes delayed)

---

## 🔐 Security Notes

- ⚠️ **Never commit `.env` file** to Git
- ⚠️ Use **App Password**, not regular password
- ⚠️ Keep credentials secure
- ⚠️ `.env` is already in `.gitignore`

---

## 📝 Alternative: Use Your Own Email

If you want to test with your own email first:

1. Open: `backend/atm_backend/settings.py`
2. Find: `APPROVAL_EMAIL_RECIPIENTS`
3. Change to your email:
   ```python
   APPROVAL_EMAIL_RECIPIENTS = [
       'your-email@gmail.com',  # Test with your email first
   ]
   ```
4. Run the test script
5. Check your inbox
6. Change back to `yossefhaddad20@gmail.com` when ready

---

## 🎯 Summary

**To send test email:**

1. Get Gmail App Password from: https://myaccount.google.com/apppasswords
2. Update `backend/.env` with credentials
3. Run: `python send_test_email.py`
4. Type `yes` to confirm
5. Check inbox at `yossefhaddad20@gmail.com`

**That's it!** 🚀
