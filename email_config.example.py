"""
SkyWings Aviation - Live Email Configuration Template
-----------------------------------------------------
Copy this file to `email_config.py` and fill in your details:
cp email_config.example.py email_config.py
"""

import os

# Set this to True to start sending live emails to real inboxes over the internet!
SMTP_ENABLED = True

# SMTP Server configuration (Gmail default)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USE_TLS = True

# Your sender account credentials
SMTP_USER = os.environ.get("SMTP_USER", "your_email@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "your_16_character_app_password")

# Sender name and email displayed in recipient inbox
SMTP_FROM = f"SkyWings Aviation <{SMTP_USER}>"

# Target email where all customer support complaints are forwarded
SUPPORT_FORWARD_EMAIL = os.environ.get("SUPPORT_FORWARD_EMAIL", "deeptidhanwate0@gmail.com")

# Base URL for email action links (boarding pass view, cancellation)
# In development: http://127.0.0.1:5000
# In production:  https://your-domain.com or https://skywings.onrender.com
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
