# 1. Send Emails
# 👉 Using google app password (requires enabling 2FA) - https://myaccount.google.com/apppasswords

# 🔎  Send an email to yourself

import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email():
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("GOOGLE_APP_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)

    if not all([sender_email, app_password]):
        print("❌ Error: Missing email credentials.")
        print("Please create a '.env' file with:")
        print("SENDER_EMAIL=your_email@gmail.com")
        print("GOOGLE_APP_PASSWORD=your_16_character_app_password")
        return

    msg = EmailMessage()
    msg["Subject"] = "Test Email from Python 🚀"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(
        "Hello!\n\n"
        "If you are reading this, your Python script successfully connected "
        "to the Google SMTP server using an App Password.\n\n"
        "Great job!"
    )

    try:
        print(f"Connecting to SMTP server to send email to {receiver_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender_email, app_password)
            smtp_server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email. Error: {e}")

if __name__ == "__main__":
    send_email()
