import os
import imaplib, email
from email.header import decode_header

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

    # Search for any email with a PDF attachment
    typ, data = mail.search(None, '(HASATTACHMENT)')
    ids = data[0].split()
    if not ids:
        print("No messages with attachments found.")
        return

    # We'll iterate from newest to oldest
    for msgid in reversed(ids):
        typ, msg_data = mail.fetch(msgid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            if part.get_content_type() == "application/pdf":
                filename = part.get_filename()
                if filename:
                    print(f"Downloading {filename} → {OUTPUT_FILE}")
                    with open(OUTPUT_FILE, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    mail.logout()
                    return

    print("No PDF attachment found in recent emails.")
    mail.logout()

if __name__ == "__main__":
    fetch_latest_pdf()
