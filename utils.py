import re
from datetime import datetime

def is_valid_phone(phone: str) -> bool:
    phone = phone.strip()
    pattern = r'^0\d{3}([ ]?)\d{3}\1\d{3}$'
    return bool(re.fullmatch(pattern, phone))


def format_event_date(event_date: str) -> str:
    try:
        return datetime.strptime(event_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except ValueError:
        return event_date


def build_event_text(lang: str, event, labels: dict) -> str:
    _, title, event_date, description, _, _, _ = event
    return (
        f"{title}\n\n"
        f"{labels[lang]['event_date']}: {format_event_date(event_date)}\n"
        f"{labels[lang]['description']}: {description or '-'}"
    )



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid  # Added for anti-spam headers


def send_yandex_email(subject, body):
    smtp_server = "smtp.yandex.com"
    smtp_port = 465

    SENDER_EMAIL = "tanaki.93@yandex.com"
    APP_PASSWORD = "lwesjpyilpqrwjxc"
    RECEIVER_EMAIL = "tanaki.9393@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject

    # --- NEW: Anti-Spam Headers ---
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain="yandex.com")

    msg.attach(MIMEText(body, 'plain'))

    try:
        print("Connecting to server...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        print("Logging in...")
        server.login(SENDER_EMAIL, APP_PASSWORD)

        print("Sending email...")
        server.send_message(msg)

        print("Email sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        server.quit()




