# Email Setup Guide for Face Analysis AI

This guide will help you set up email functionality for password reset features in the Face Analysis AI application.

## Overview

The application now supports sending password reset emails to users who forget their passwords. This feature requires proper email configuration.

## Prerequisites

1. **Gmail Account** (recommended) or other email provider
2. **2-Factor Authentication** enabled on your email account
3. **App Password** generated for the application

## Setup Instructions

### Step 1: Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account settings
   - Navigate to Security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other" as the device
   - Enter "Face Analysis AI" as the name
   - Click "Generate"
   - Copy the 16-character password

### Step 2: Configure Environment Variables

#### Option A: Windows PowerShell
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-16-character-app-password"
```

#### Option B: Windows Command Prompt
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-16-character-app-password
```

#### Option C: Linux/Mac Terminal
```bash
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-16-character-app-password"
```

### Step 3: Install Dependencies

Make sure you have the required packages:
```bash
pip install flask-mail
```

### Step 4: Test the Setup

1. Start the application:
   ```bash
   python app.py
   ```

2. Go to the login page and click "Forgot Password?"
3. Enter a valid email address
4. Check if the email is sent successfully

## Alternative Email Providers

### Outlook/Hotmail
```python
MAIL_SERVER = 'smtp-mail.outlook.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
```

### Yahoo Mail
```python
MAIL_SERVER = 'smtp.mail.yahoo.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
```

### Custom SMTP Server
Update the `email_config.py` file with your server details:
```python
EMAIL_CONFIG = {
    'MAIL_SERVER': 'your-smtp-server.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'your-email@domain.com',
    'MAIL_PASSWORD': 'your-password',
    'MAIL_DEFAULT_SENDER': 'your-email@domain.com',
}
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables** for sensitive data
3. **Use app passwords** instead of your main password
4. **Enable 2-factor authentication** on your email account
5. **Regularly rotate app passwords**

## Troubleshooting

### Common Issues

1. **"Authentication failed" error**
   - Make sure you're using an app password, not your regular password
   - Verify 2-factor authentication is enabled
   - Check if the app password is correct

2. **"Connection refused" error**
   - Check your internet connection
   - Verify the SMTP server and port are correct
   - Some networks block SMTP ports

3. **"Email not received"**
   - Check spam/junk folder
   - Verify the email address is correct
   - Check if the email provider is blocking the connection

### Debug Mode

To see detailed error messages, run the application in debug mode:
```python
if __name__ == '__main__':
    app.run(debug=True)
```

## Email Templates

The application uses HTML email templates located in `templates/email/`. You can customize these templates to match your branding:

- `reset_password.html` - Password reset email template

## Testing Email Functionality

1. **Create a test user** in the application
2. **Request password reset** using the test email
3. **Check email delivery** and template rendering
4. **Test the reset link** functionality

## Production Deployment

For production deployment:

1. **Use a dedicated email service** like SendGrid, Mailgun, or AWS SES
2. **Set up proper DNS records** (SPF, DKIM, DMARC)
3. **Monitor email delivery** and bounce rates
4. **Implement rate limiting** for password reset requests
5. **Use HTTPS** for all email links

## Support

If you encounter issues:

1. Check the application logs for error messages
2. Verify your email configuration
3. Test with a different email provider
4. Check the troubleshooting section above

## Files Modified

- `app.py` - Added email functionality and routes
- `database.py` - Added password reset token management
- `email_config.py` - Email configuration management
- `templates/forgot-password.html` - Forgot password page
- `templates/reset_password.html` - Password reset page
- `templates/email/reset_password.html` - Email template
- `requirements.txt` - Added Flask-Mail dependency 