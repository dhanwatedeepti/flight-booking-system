"""
SkyWings Email Verification & Diagnostic Tool
Run: python test_live_email.py
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import email_config
from email_service import send_support_complaint, send_ticket_email

print("=" * 65)
print("       SkyWings Aviation - Live Email Diagnostic Tool       ")
print("=" * 65)

print(f"SMTP Enabled:         {email_config.SMTP_ENABLED}")
print(f"SMTP Server:          {email_config.SMTP_HOST}:{email_config.SMTP_PORT}")
print(f"Configured Sender:    {email_config.SMTP_USER or '(Not set yet)'}")
print(f"Support Forward To:   {email_config.SUPPORT_FORWARD_EMAIL}")
print("-" * 65)

if not email_config.SMTP_USER or not email_config.SMTP_PASS:
    print("\n[NOTE] LIVE EMAIL DISPATCH IS CURRENTLY WAITING FOR CREDENTIALS:")
    print("   Your system generated the full HTML emails and saved them safely")
    print(f"   in the local folder: {os.path.abspath('sent_emails')}")
    print("\n[STEPS] HOW TO RECEIVE LIVE EMAILS IN YOUR GMAIL INBOX:")
    print("   1. Open: https://myaccount.google.com/apppasswords")
    print("      (Make sure 2-Step Verification is active on your Google account)")
    print("   2. App Name: type 'SkyWings', click Create.")
    print("   3. Copy the 16-character code (e.g. 'abcd efgh ijkl mnop').")
    print("   4. Open 'email_config.py' in this project folder and set:")
    print('      SMTP_USER = "your_email@gmail.com"')
    print('      SMTP_PASS = "your_16_char_app_password"')
    print("   5. Re-run: python test_live_email.py")
    print("-" * 65)
    print("Testing local email generation...")
else:
    print("\nCredentials detected! Attempting to send live test email...")

# Trigger a test complaint email
saved_file = send_support_complaint(
    name="System Test",
    sender_email="passenger.test@skywings.com",
    subject="Diagnostic Test Email",
    message="This is a test notification to verify that flight confirmations and customer support complaints are arriving directly to your inbox.",
    forward_to=email_config.SUPPORT_FORWARD_EMAIL
)

print(f"\n[DONE] Diagnostic run complete.")
print(f"   Archived file: {saved_file}")
print("=" * 65)
