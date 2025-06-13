from gmail_api import init_gmail_service,download_attachments_all,download_attachments_parent
from pathlib import Path

client_file = 'client_secret.json'
service = init_gmail_service(client_file)

user_id = 'me'
msg_id = '123123'
download_dir = Path('./downloads')


download_attachments_parent(service,user_id,msg_id,download_dir)