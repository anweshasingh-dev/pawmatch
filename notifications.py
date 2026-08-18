import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration (for local testing, you can use Mailtrap or Gmail App Passwords)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Replace with generated App Password

def send_match_notification(user_email: str, pet_name: str, score: float, match_url: str):
    """Sends an email alert when a high-probability match is identified."""
    if not user_email or "@" not in user_email:
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = user_email
    msg['Subject'] = f"🐾 Potential Match Found for {pet_name or 'your pet'}! ({score}% Match)"

    body = f"""
    Hi there,

    PawMatch found a potential match for your report with a confidence score of {score}%!

    View details and contact information here:
    {match_url}

    Best,
    PawMatch AI Team
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            print(f"Match notification sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")