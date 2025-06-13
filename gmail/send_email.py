from gmail_api import init_gmail_service,send_email
from pathlib import Path

client_file = 'client_secret.json'
service = init_gmail_service(client_file)

to_address = "rushilmisra@gmail.com"

email_subject = 'test mail '
email_body = "test"

attachment_dir = Path('./attachments')
attachment_files = list(attachment_dir.glob('*'))

response_email_sent = send_email(
    service,
    to_address,
    email_subject,
    email_body,
    body_type='plain',
    attachment_paths=attachment_files
)
print(response_email_sent)