# 0.  Send Emails (SMTP server connection)
# 👉 Using google app password (requires enabling 2FA) - https://myaccount.google.com/apppasswords

# 🔎  Send an email to yourself

import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from a .env file for security best practices
# This prevents hardcoding sensitive passwords in the source code.
load_dotenv()

def send_email():
    # 1. Fetch credentials securely from environment variables
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("GOOGLE_APP_PASSWORD")
    
    # We are sending an email to ourselves, so the receiver is the sender
    receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)

    # Validate that the credentials exist
    if not all([sender_email, app_password]):
        print("❌ Error: Missing email credentials.")
        print("Please create a '.env' file in this directory with the following variables:")
        print("SENDER_EMAIL=your_email@gmail.com")
        print("GOOGLE_APP_PASSWORD=your_16_character_app_password")
        return

    # 2. Construct the Email Message
    msg = EmailMessage()
    msg["Subject"] = "Test Email from Python 🚀"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(
        "Hello!\n\n"
        "If you are reading this, it means your Python script successfully connected "
        "to the Google SMTP server using an App Password.\n\n"
        "Security Note: The credentials were loaded securely from a .env file!\n\n"
        "Great job!"
    )

    # 3. Connect to the SMTP server and send the email
    try:
        print(f"Connecting to SMTP server to send email to {receiver_email}...")
        
        # Connect to Gmail's SMTP server on port 465 (SSL)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            # Login to the server
            smtp_server.login(sender_email, app_password)
            
            # Send the message
            smtp_server.send_message(msg)
            
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send email. Error: {e}")

if __name__ == "__main__":
    send_email()
