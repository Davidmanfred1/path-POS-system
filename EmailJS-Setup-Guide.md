# EmailJS Setup Guide for Manfredinc Website

This guide will help you set up EmailJS to enable real email sending from your contact form directly to your Gmail account.

## Step 1: Create EmailJS Account

1. Go to [EmailJS.com](https://www.emailjs.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

## Step 2: Add Email Service

1. In your EmailJS dashboard, go to "Email Services"
2. Click "Add New Service"
3. Choose "Gmail" as your email service
4. Click "Connect Account" and authorize with your Gmail account (davidmanfred573589170@gmail.com)
5. Note down your **Service ID** (e.g., "service_abc123")

## Step 3: Create Email Template

1. Go to "Email Templates" in your dashboard
2. Click "Create New Template"
3. Use this template for receiving contact form messages:

**Template Name:** Contact Form Template
**Template ID:** contact_form (note this down)

**Subject:** New Project Inquiry from {{from_name}}

**Content:**
```
New project inquiry received from your website!

From: {{from_name}}
Email: {{from_email}}
Service Interest: {{service_type}}
Timestamp: {{timestamp}}

Message:
{{message}}

---
This message was sent from the Manfredinc website contact form.
Reply directly to this email to respond to the client.
```

## Step 4: Create Auto-Reply Template (Optional)

1. Create another template for auto-replies to users
2. **Template Name:** Auto Reply Template
3. **Template ID:** auto_reply (note this down)

**Subject:** Thank you for contacting Manfredinc!

**Content:**
```
Dear {{to_name}},

Thank you for reaching out to Manfredinc! We have received your message and will get back to you within 24 hours.

Here's a summary of your inquiry:
- Service Interest: {{service_type}}
- Message: {{message}}

In the meantime, feel free to explore our portfolio and learn more about our services on our website.

Best regards,
The Manfredinc Team

Contact Information:
📧 Email: davidmanfred573589170@gmail.com
📞 Phone: +233 59 154 4535
📍 Address: Oshimpa St, Accra, Ghana
```

## Step 5: Get Your Public Key

1. Go to "Account" in your EmailJS dashboard
2. Find your **Public Key** (e.g., "user_abc123xyz")
3. Note this down

## Step 6: Update the Website Code

In your `index-complete.html` file, replace these placeholders:

1. **Line ~1752:** Replace `"YOUR_PUBLIC_KEY"` with your actual public key
2. **Line ~1889:** Replace `"YOUR_SERVICE_ID"` with your Gmail service ID
3. **Line ~1889:** Replace `"YOUR_TEMPLATE_ID"` with your contact form template ID
4. **Line ~1925:** Replace `"YOUR_AUTOREPLY_TEMPLATE_ID"` with your auto-reply template ID

Example:
```javascript
// Replace this:
emailjs.init("YOUR_PUBLIC_KEY");

// With this (using your actual key):
emailjs.init("user_abc123xyz");
```

## Step 7: Test the Setup

1. Upload your updated `index-complete.html` to your web server
2. Fill out the contact form on your website
3. Check your Gmail inbox for the message
4. Check if the user receives an auto-reply (if enabled)

## Troubleshooting

### Common Issues:

1. **"EmailJS is not defined" error:**
   - Make sure the EmailJS script is loading properly
   - Check your internet connection

2. **"Service not found" error:**
   - Verify your Service ID is correct
   - Make sure the Gmail service is properly connected

3. **"Template not found" error:**
   - Check your Template ID matches exactly
   - Ensure the template is published (not in draft)

4. **Emails not arriving:**
   - Check your Gmail spam folder
   - Verify the template variables match the code
   - Check EmailJS dashboard for error logs

### Free Plan Limits:
- 200 emails per month
- EmailJS branding in emails
- Basic support

### Upgrade Options:
- Personal Plan: $15/month (1,000 emails)
- Professional Plan: $35/month (5,000 emails)
- No EmailJS branding on paid plans

## Security Notes

- Your EmailJS public key is safe to expose in frontend code
- Never expose your private key in frontend code
- EmailJS handles the secure email sending
- Consider implementing rate limiting for production use

## Alternative Fallback Methods

The website includes fallback options if EmailJS fails:
1. Direct mailto link with pre-filled content
2. WhatsApp message link
3. Phone number for direct calling

This ensures users can always contact you even if there are technical issues.

## Support

- EmailJS Documentation: https://www.emailjs.com/docs/
- EmailJS Support: support@emailjs.com
- For website issues: Contact your developer

---

Once configured, your contact form will automatically send emails to davidmanfred573589170@gmail.com whenever someone submits the form!
