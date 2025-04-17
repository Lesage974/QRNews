import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying these scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate():
    """
    Authenticate with Gmail API using credentials.json and token.json on disk.
    Assumes credentials.json and token.json have been created beforehand (e.g. by CI workflow).
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the refreshed token.json
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return creds


def get_latest_pdf(service):
    """
    Downloads the first PDF attachment from the latest email matching query.
    """
    results = service.users().messages().list(
        userId='me', q="has:attachment filename:pdf"
    ).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No PDF found.")
        return

    msg = service.users().messages().get(
        userId='me', id=messages[0]['id']
    ).execute()
    parts = msg['payload'].get('parts', [])

    for part in parts:
        filename = part.get('filename', '')
        if filename.lower().endswith('.pdf'):
            attach_id = part['body'].get('attachmentId')
            if not attach_id:
                continue
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=msg['id'], id=attach_id
            ).execute()
            data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
            with open('latest.pdf', 'wb') as f:
                f.write(data)
            print(f"✔ Downloaded: {filename} → latest.pdf")
            return
    print("No PDF attachment found.")


def main():
    # Authenticate and download the PDF
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    get_latest_pdf(service)

if __name__ == '__main__':
    main()
