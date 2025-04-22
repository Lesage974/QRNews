import os
import imaplib
import email
from email.policy import default

# Credentials from environment
USER = os.environ['GMAIL_USERNAME']
PASS = os.environ['GMAIL_APP_PASSWORD']

IMAP_SERVER = "imap.gmail.com"
IMAP_FOLDER = "INBOX"
OUTPUT_FILE = "latest.pdf"

def fetch_latest_pdf():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(USER, PASS)
    mail.select(IMAP_FOLDER)

    # Use Gmail's X‑GM‑RAW to search like Gmail web: has:attachment filename:pdf
    typ, data = mail.search(None, 'X-GM-RAW', 'has:attachment filename:pdf')
    if typ != 'OK':
        print("Error searching mailbox:", data)
        return

    ids = data[0].split()
    if not ids:
        print("No PDF attachments found.")
        return

    # Iterate newest→oldest
    for msgid in reversed(ids):
        typ, msg_data = mail.fetch(msgid, "(RFC822)")
        if typ != 'OK':
            continue

        msg = email.message_from_bytes(msg_data[0][1], policy=default)
        for part in msg.iter_attachments():
            if part.get_content_type() == "application/pdf":
                filename = part.get_filename()
                print(f"Downloading {filename} → {OUTPUT_FILE}")
                with open(OUTPUT_FILE, "wb") as f:
                    f.write(part.get_payload(decode=True))
                mail.logout()
                return

    print("No PDF attachment found in recent messages.")
    mail.logout()

if __name__ == "__main__":
    fetch_latest_pdf()
