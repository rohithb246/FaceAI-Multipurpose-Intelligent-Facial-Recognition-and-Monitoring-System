<<<<<<< HEAD
"""
Email Configuration for Face Analysis AI

To use email functionality (password reset), you need to configure your email settings.

For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use your Gmail address and the generated app password below

For other email providers, check their SMTP settings.
"""

import os

# Email Configuration
EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',  # Gmail SMTP server
    'MAIL_PORT': 587,                 # Gmail SMTP port
    'MAIL_USE_TLS': True,             # Use TLS encryption
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', 'facea0303@gmail.com'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', 'pmwo rtbe qyvv wsil'),
    'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_USERNAME', 'your-email@gmail.com'),
}

# Alternative email providers
ALTERNATIVE_CONFIGS = {
    'outlook': {
        'MAIL_SERVER': 'smtp-mail.outlook.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
    },
    'yahoo': {
        'MAIL_SERVER': 'smtp.mail.yahoo.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
    },
    'protonmail': {
        'MAIL_SERVER': '127.0.0.1',
        'MAIL_PORT': 1025,
        'MAIL_USE_TLS': False,
    }
}

def get_email_config():
    """Get email configuration with environment variable support"""
    config = EMAIL_CONFIG.copy()
    
    # Override with environment variables if set
    for key in config:
        env_value = os.environ.get(key)
        if env_value:
            config[key] = env_value
    
    return config

def setup_email_environment():
    """Instructions for setting up email environment variables"""
    print("""
=== EMAIL SETUP INSTRUCTIONS ===

To enable password reset emails, you need to set up your email credentials.

Option 1: Set Environment Variables (Recommended)
-----------------------------------------------
Set these environment variables before running the application:

For Windows (PowerShell):
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password"

For Windows (Command Prompt):
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password

For Linux/Mac:
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"

Option 2: Create a .env file
---------------------------
Create a file named '.env' in the project root with:
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

Option 3: Edit email_config.py directly
--------------------------------------
Edit the EMAIL_CONFIG dictionary in email_config.py with your credentials.

Gmail Setup:
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use your Gmail address and the generated app password

Security Note: Never commit your email credentials to version control!
""")

if __name__ == "__main__":
=======
"""
Email Configuration for Face Analysis AI

To use email functionality (password reset), you need to configure your email settings.

For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use your Gmail address and the generated app password below

For other email providers, check their SMTP settings.
"""

import os

# Email Configuration
EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',  # Gmail SMTP server
    'MAIL_PORT': 587,                 # Gmail SMTP port
    'MAIL_USE_TLS': True,             # Use TLS encryption
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', 'your-email@gmail.com'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', 'your-app-password'),
    'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_USERNAME', 'your-email@gmail.com'),
}

# Alternative email providers
ALTERNATIVE_CONFIGS = {
    'outlook': {
        'MAIL_SERVER': 'smtp-mail.outlook.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
    },
    'yahoo': {
        'MAIL_SERVER': 'smtp.mail.yahoo.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
    },
    'protonmail': {
        'MAIL_SERVER': '127.0.0.1',
        'MAIL_PORT': 1025,
        'MAIL_USE_TLS': False,
    }
}

def get_email_config():
    """Get email configuration with environment variable support"""
    config = EMAIL_CONFIG.copy()
    
    # Override with environment variables if set
    for key in config:
        env_value = os.environ.get(key)
        if env_value:
            config[key] = env_value
    
    return config

def setup_email_environment():
    """Instructions for setting up email environment variables"""
    print("""
=== EMAIL SETUP INSTRUCTIONS ===

To enable password reset emails, you need to set up your email credentials.

Option 1: Set Environment Variables (Recommended)
-----------------------------------------------
Set these environment variables before running the application:

For Windows (PowerShell):
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password"

For Windows (Command Prompt):
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password

For Linux/Mac:
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"

Option 2: Create a .env file
---------------------------
Create a file named '.env' in the project root with:
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

Option 3: Edit email_config.py directly
--------------------------------------
Edit the EMAIL_CONFIG dictionary in email_config.py with your credentials.

Gmail Setup:
1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use your Gmail address and the generated app password

Security Note: Never commit your email credentials to version control!
""")

if __name__ == "__main__":
>>>>>>> a8a36cb1c8a89472d874daa0bf4ce03cfbef9114
    setup_email_environment() 