import os
import base64
import re
import mimetypes
import subprocess
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

def get_latest_pdf(service):
    results = service.users().messages().list(userId='me', q="has:attachment filename:pdf").execute()
    messages = results.get('messages', [])
    if not messages:
        print("No PDF found.")
        return

    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    parts = msg['payload'].get('parts', [])

    for part in parts:
        filename = part.get("filename")
        if filename and filename.lower().endswith(".pdf"):
            attachment_id = part['body'].get('attachmentId')
            if not attachment_id:
                continue
            attachment = service.users().messages().attachments().get(userId='me', messageId=msg['id'], id=attachment_id).execute()
            data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            with open("latest.pdf", "wb") as f:
                f.write(data)
            print(f"Downloaded: {filename} → latest.pdf")
            return
    print("No PDF attachment found.")

def main():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    get_latest_pdf(service)
    # Now call update_site.py to push the file to GitHub:
    subprocess.run(["python3", "update_site.py"])

if __name__ == '__main__':
    main()

