import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

try:
    import email_config
except ImportError:
    email_config = None

EMAILS_DIR = os.path.join(os.path.dirname(__file__), "sent_emails")
os.makedirs(EMAILS_DIR, exist_ok=True)

def _save_local_email_copy(to_email, subject, html_content):
    """Saves a local HTML copy of sent emails for offline verification and review."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_email = to_email.replace('@', '_at_').replace('.', '_')
    filename = f"{timestamp}_{clean_email}.html"
    filepath = os.path.join(EMAILS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<!-- TO: {to_email} -->\n<!-- SUBJECT: {subject} -->\n<!-- DATE: {datetime.now().isoformat()} -->\n\n" + html_content)
    return filepath

def _dispatch_email(to_email, subject, html_content):
    """
    Central Email Dispatcher:
    1. Always saves an HTML copy to sent_emails/ for audit and record-keeping.
    2. If SMTP is configured and enabled, sends real email over the network (Gmail TLS/SSL).
    3. Prints diagnostic status to the console.
    """
    filepath = _save_local_email_copy(to_email, subject, html_content)
    
    smtp_enabled = getattr(email_config, "SMTP_ENABLED", False) or (os.environ.get("SMTP_ENABLED", "").lower() in ("1", "true", "yes"))
    smtp_host = os.environ.get("SMTP_HOST") or getattr(email_config, "SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT") or getattr(email_config, "SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER") or getattr(email_config, "SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS") or getattr(email_config, "SMTP_PASS", "")
    smtp_from = os.environ.get("SMTP_FROM") or getattr(email_config, "SMTP_FROM", f"SkyWings Aviation <{smtp_user or 'support@skywings.com'}>")
    if isinstance(smtp_from, (tuple, list)):
        smtp_from = smtp_from[1] if len(smtp_from) > 1 else smtp_from[0]
    smtp_from = str(smtp_from)

    if smtp_enabled and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = to_email
            msg.attach(MIMEText(html_content, "html"))

            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, [to_email], msg.as_string())
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, [to_email], msg.as_string())
            print(f"[LIVE EMAIL SENT] Successfully delivered email to: {to_email}")
        except Exception as e:
            print(f"[SMTP DISPATCH WARNING] Could not send live email to {to_email}: {e}")
            print(f"                         (A full HTML copy was safely archived at: {filepath})")
    else:
        print(f"[LOCAL EMAIL ARCHIVED] Email to '{to_email}' saved locally at: {filepath}")
        if not (smtp_user and smtp_pass):
            print(f"  -> To receive live emails in your Gmail inbox, fill in SMTP_USER and SMTP_PASS in email_config.py.")
            
    return filepath

def send_ticket_email(booking, to_email):
    """Sends confirmed flight e-ticket and boarding pass to the passenger's email address."""
    subject = f"✈️ Confirmed Flight E-Ticket & Boarding Pass - PNR: {booking['pnr']}"
    
    base_url = getattr(email_config, "BASE_URL", os.environ.get("BASE_URL", "http://127.0.0.1:5000")).rstrip('/')
    cancel_url = f"{base_url}/cancel-booking/{booking['pnr']}"
    view_url = f"{base_url}/ticket/{booking['pnr']}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
            .email-container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 24px; }}
            .route-box {{ background: #eff6ff; border-radius: 8px; padding: 16px; margin: 16px 0; display: flex; justify-content: space-between; align-items: center; border: 1px solid #bfdbfe; }}
            .details-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
            .details-table td {{ padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            .details-table td.label {{ color: #64748b; font-weight: 600; }}
            .details-table td.val {{ font-weight: 700; color: #0f172a; text-align: right; }}
            .btn {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white !important; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 8px 4px; }}
            .btn-danger {{ background: #dc2626; }}
            .footer {{ background: #0f172a; color: #94a3b8; padding: 16px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1 style="margin: 0; font-size: 22px;">SkyWings Aviation</h1>
                <p style="margin: 6px 0 0; opacity: 0.9;">Booking Confirmed • E-Ticket & Boarding Pass</p>
            </div>
            
            <div class="content">
                <p>Dear <b>{booking['passenger_name']}</b>,</p>
                <p>Thank you for choosing SkyWings. Your flight reservation is confirmed. Below is your official digital boarding pass and travel details:</p>
                
                <!-- Visual Boarding Pass Card inside Email -->
                <div style="background: linear-gradient(135deg, #0f172a, #1e293b); color: #ffffff; border-radius: 10px; padding: 20px; margin: 18px 0; border-left: 6px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed rgba(255,255,255,0.25); padding-bottom: 12px; margin-bottom: 14px;">
                        <div>
                            <span style="font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8;">BOARDING PASS</span>
                            <div style="font-size: 18px; font-weight: 800; color: #60a5fa;">{booking['airline']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8;">PNR CODE</span>
                            <div style="font-size: 18px; font-weight: 800; font-family: monospace; color: #38bdf8;">{booking['pnr']}</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 14px; text-align: left;">
                        <div>
                            <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Passenger</span>
                            <div style="font-weight: 700; font-size: 14px; color: #ffffff;">{booking['passenger_name']}</div>
                        </div>
                        <div>
                            <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Flight</span>
                            <div style="font-weight: 700; font-size: 14px; color: #ffffff;">{booking['flight_number']}</div>
                        </div>
                        <div>
                            <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Seat</span>
                            <div style="font-weight: 800; font-size: 16px; color: #f59e0b;">{booking.get('seat_numbers') or 'Auto'}</div>
                        </div>
                        <div>
                            <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Gate</span>
                            <div style="font-weight: 700; font-size: 14px; color: #34d399;">{booking.get('gate', '12A')}</div>
                        </div>
                    </div>
                    <!-- Barcode Stamp -->
                    <div style="text-align: center; background: #ffffff; color: #000000; padding: 8px 12px; border-radius: 6px; margin-top: 12px;">
                        <div style="font-family: 'Courier New', monospace; font-size: 22px; letter-spacing: 4px; font-weight: 900; line-height: 1;">||| | |||| | || ||| || |||| | ||</div>
                        <div style="font-size: 10px; color: #64748b; font-family: monospace; letter-spacing: 2px; margin-top: 4px;">{booking['pnr']} • ETKT-ELECTRONIC PASS</div>
                    </div>
                </div>

                <div class="route-box">
                    <div>
                        <div style="font-size: 24px; font-weight: 800; color: #1e3a8a;">{booking['origin_code']}</div>
                        <div style="font-size: 12px; color: #475569;">{booking['origin_city']}</div>
                        <div style="font-weight: 700; margin-top: 4px;">{booking['departure_time']}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 12px; color: #64748b;">{booking['duration']}</div>
                        <div style="color: #2563eb; font-size: 18px;">✈ ➔</div>
                        <div style="font-size: 11px; color: #059669; font-weight: 600;">Confirmed</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 24px; font-weight: 800; color: #1e3a8a;">{booking['destination_code']}</div>
                        <div style="font-size: 12px; color: #475569;">{booking['destination_city']}</div>
                        <div style="font-weight: 700; margin-top: 4px;">{booking['arrival_time']}</div>
                    </div>
                </div>

                <table class="details-table">
                    <tr>
                        <td class="label">Booking Reference (PNR)</td>
                        <td class="val" style="color: #2563eb; font-family: monospace; font-size: 16px;">{booking['pnr']}</td>
                    </tr>
                    <tr>
                        <td class="label">Flight Number & Airline</td>
                        <td class="val">{booking['airline']} • {booking['flight_number']}</td>
                    </tr>
                    <tr>
                        <td class="label">Date of Travel</td>
                        <td class="val">{booking['travel_date']}</td>
                    </tr>
                    <tr>
                        <td class="label">Cabin Class</td>
                        <td class="val">{booking['cabin_class']}</td>
                    </tr>
                    <tr>
                        <td class="label">Seat Number(s)</td>
                        <td class="val" style="color: #ea580c;">{booking.get('seat_numbers') or 'Auto-assigned'}</td>
                    </tr>
                    <tr>
                        <td class="label">Terminal / Gate</td>
                        <td class="val">{booking.get('terminal', 'T2')} / Gate {booking.get('gate', '12A')}</td>
                    </tr>
                    <tr>
                        <td class="label">Baggage Allowance</td>
                        <td class="val">{booking.get('baggage_checkin', '15 kg')} Check-in + 7 kg Cabin</td>
                    </tr>
                    <tr>
                        <td class="label">Total Paid</td>
                        <td class="val" style="color: #059669; font-size: 16px;">₹{int(booking['total_price']):,}</td>
                    </tr>
                </table>

                <div style="text-align: center; margin: 24px 0;">
                    <a href="{view_url}" class="btn">View & Print Boarding Pass on Web</a>
                    <a href="{cancel_url}" class="btn btn-danger" onclick="return confirm('Confirm cancellation?')">Cancel Flight (85% Refund)</a>
                </div>

                <p style="font-size: 11px; color: #64748b; line-height: 1.5;">
                    * Web links point to your application server ({base_url}). If clicked on a mobile device while running on local development (127.0.0.1), your browser may say unreachable until the app is deployed online. Your full boarding pass is already displayed above!
                </p>
            </div>

            <div class="footer">
                <p>&copy; 2026 SkyWings Aviation. 24/7 Helpline: 1800-419-WINGS | support@skywings.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return _dispatch_email(to_email, subject, html_content)

def send_cancellation_email(booking, refund_amount, to_email):
    """Sends cancellation receipt and refund breakdown to the passenger."""
    subject = f"⚠️ Flight Cancellation & Refund Confirmation - PNR: {booking['pnr']}"
    
    original_price = int(booking['total_price'])
    cancellation_fee = original_price - int(refund_amount)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
            .email-container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: #dc2626; color: white; padding: 24px; text-align: center; }}
            .content {{ padding: 24px; }}
            .refund-box {{ background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 18px; margin: 16px 0; }}
            .details-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
            .details-table td {{ padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
            .details-table td.label {{ color: #64748b; font-weight: 600; }}
            .details-table td.val {{ font-weight: 700; color: #0f172a; text-align: right; }}
            .footer {{ background: #0f172a; color: #94a3b8; padding: 16px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1 style="margin: 0; font-size: 22px;">SkyWings Cancellation Receipt</h1>
                <p style="margin: 6px 0 0; opacity: 0.9;">Booking Reference: {booking['pnr']} (Cancelled)</p>
            </div>

            <div class="content">
                <p>Dear <b>{booking['passenger_name']}</b>,</p>
                <p>As requested, your booking for flight <b>{booking.get('flight_number', '')}</b> from <b>{booking.get('origin_city', '')}</b> to <b>{booking.get('destination_city', '')}</b> on <b>{booking.get('travel_date', '')}</b> has been successfully cancelled.</p>
                
                <div class="refund-box">
                    <div style="font-size: 13px; color: #991b1b; font-weight: 700; text-transform: uppercase;">Refund Initiated</div>
                    <div style="font-size: 26px; font-weight: 800; color: #b91c1c; margin-top: 4px;">
                        ₹{int(refund_amount):,}
                    </div>
                    <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
                        Credited back to your original payment method ({booking.get('payment_method', 'Card')}) within 3-5 business days.
                    </div>
                </div>

                <table class="details-table">
                    <tr>
                        <td class="label">Original Amount Paid</td>
                        <td class="val">₹{original_price:,}</td>
                    </tr>
                    <tr>
                        <td class="label">Cancellation Fee (15%)</td>
                        <td class="val" style="color: #dc2626;">-₹{cancellation_fee:,}</td>
                    </tr>
                    <tr>
                        <td class="label">Net Refund Amount</td>
                        <td class="val" style="color: #059669; font-size: 16px;">₹{int(refund_amount):,}</td>
                    </tr>
                    <tr>
                        <td class="label">Cancellation Timestamp</td>
                        <td class="val">{datetime.now().strftime('%d %b %Y, %I:%M %p')}</td>
                    </tr>
                </table>

                <p style="font-size: 13px; color: #475569; line-height: 1.6;">
                    If you have any questions regarding your refund status, please reply to this email or reach us at <b>support@skywings.com</b> quoting PNR <b>{booking['pnr']}</b>.
                </p>
            </div>

            <div class="footer">
                <p>&copy; 2026 SkyWings Aviation. 24/7 Helpline: 1800-419-WINGS</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return _dispatch_email(to_email, subject, html_content)

def send_support_complaint(name, sender_email, subject, message, forward_to=None):
    """Forwards customer support complaints to deeptidhanwate0@gmail.com (or configured recipient)."""
    target_forward = forward_to or getattr(email_config, "SUPPORT_FORWARD_EMAIL", "deeptidhanwate0@gmail.com")
    email_subject = f"🚨 New Support Complaint / Feedback from {name}: {subject}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #f8fafc; }}
            .card {{ background: white; padding: 24px; border-radius: 8px; border: 1px solid #cbd5e1; max-width: 600px; margin: 0 auto; }}
            .tag {{ background: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="tag">CUSTOMER COMPLAINT / INQUIRY</span>
            <h2 style="margin: 12px 0; color: #0f172a;">{subject}</h2>
            <p><b>From Customer:</b> {name} ({sender_email})</p>
            <p><b>Recipient:</b> support@skywings.com</p>
            <p><b>Forwarded Directly To:</b> {target_forward}</p>
            <p><b>Received At:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}</p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 16px 0;">
            <p><b>Customer Message:</b></p>
            <div style="background: #f1f5f9; padding: 14px; border-radius: 6px; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">
{message}
            </div>
        </div>
    </body>
    </html>
    """
    
    return _dispatch_email(target_forward, email_subject, html_content)

