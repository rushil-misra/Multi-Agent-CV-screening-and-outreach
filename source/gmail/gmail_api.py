import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from gmail.google_api import create_service

def init_gmail_service(client_file, api_name = 'gmail', api_version = 'v1',scopes=['https://mail.google.com/']):
    return create_service(client_file,api_name,api_version,scopes)


def _extract_body(payload):
    body = '<Text body not available>'
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return body


def get_email_messages(service, user_id = 'me', label_ids = None,folder_name = 'INBOX', max_results = 5):
    messages = []
    next_page_token = None

    if folder_name:
        label_results = service.users().labels().list(userId = user_id).execute()
        labels = label_results.get('labels',[])
        folder_label_id = next((label['id'] for label in labels if label['name'].lower() == folder_name.lower()),None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids = [folder_label_id]
        else:
            raise ValueError(f"Folder '{folder_name}' not found")
    while True:
        result = service.users().messages().list(
            userId= user_id,
            labelIds = label_ids,
            maxResults = min(500,max_results-len(messages)) if max_results else 500,pageToken = next_page_token
        ).execute()


        messages.extend(result.get('messages', []))

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
        
            break
    return messages[:max_results] if max_results else messages


def get_email_message_details(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    headers = payload.get('headers', [])

    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
    if not subject:
        subject = message.get('subject', 'No subject')

    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No sender')
    recipients = next((header['value'] for header in headers if header['name'] == 'To'), 'No recipients')
    snippet = message.get('snippet', 'No snippet')
    has_attachments = any(part.get('filename') for part in payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No date')
    star = message.get('labelIds', []).count('STARRED') > 0
    label = ', '.join(message.get('labelIds', []))

    body = _extract_body(payload)

    return {
        'subject': subject,
        'sender': sender,
        'recipients': recipients,
        'body': body,
        'snippet': snippet,
        'has_attachments': has_attachments,
        'date': date,
        'star': star,
        'label': label,
    }

    

def send_email(service,to,subject,body,body_type = 'plain',attachment_paths = None):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    
    if body_type.lower() not in ['plain','html']:
        raise ValueError('body type must be either "plain" or "html" ')
    
    message.attach(MIMEText(body,body_type.lower()))

    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):
                filename  = os.path.basename(attachment_path)

            with open(attachment_path,"rb") as attachment:
                part = MIMEBase('aaplication','octet-stream')

                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            part.add_header(
                "Content_Disposition",
                f"attachment: filename = {filename}"
            )

            message.attach(part)
        else:
            raise FileNotFoundError(f'file not found - {filename}')
        
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    sent_message = service.users().messages().send(
        userId = 'me',
        body = {'raw': raw_message}
    ).execute()

    return sent_message


def download_attachments_parent(service,user_id,msg_id,target_dir):
    message = service.users().messages().get(userId = user_id,id = msg_id).execute()

    for part in message['payload']['parts']:
        if part['filename']:
            att_id = part['body']['attachmentId']

            att = service.users().messages().attachments().get(userId = user_id, messageId = msg_id,id = att_id).execute()

            data= att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            file_path = os.path.join(target_dir,part['filename'])
            print('saving attachment to : ', file_path)

            with open(file_path,'wb') as f:
                f.write(file_data)

def download_attachments_all(service, user_id, msg_id, target_dir):
    thread = service.users().threads().get(userId = user_id,id = msg_id).execute()
    for message in thread['messages']:
        for part in message['payload']['parts']:
            if part['filename']:
                att_id = part['body']['attachmentId']
                att = service.users().messages().attachments().get(userId = user_id,messageId = message['id'],id = att_id).execute()
                data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                file_path = os.path.join(target_dir,part['filename'])
                print('saving attachment to : ', file_path)

                with open (file_path,'wb') as f:
                    f.write(file_data)

def trash_email(service,user_id,message_id):
    service.users().messages().trash(userId = user_id,id = message_id).execute()


def batch_trash_emails(service,user_id,message_ids):
    batch = service.new_batch_http_request()
    for message_id in message_ids:
        batch.add(service.users().messages().trash(userId = user_id,id = message_id))
    batch.execute()

def permanently_delete_email(service,user_id,message_id):
    service.users().messages().delete(userId = user_id,id = message_id).execute()



def recover_email(service,user_id,message_id):
    service.users().messages().untrash(userId = user_id,id = message_id).execute()


def batch_recover_emails(service,user_id,message_ids):
    batch = service.new_batch_http_request()
    for message_id in message_ids:
        batch.add(service.users().messages().untrash(userId = user_id,id = message_id))
    batch.execute()


def empty_trash(service):
    page_token = None
    total_deleted = 0

    while True:
        response = service.users().messages().list(
            userId = 'me',
            q = 'in:trash',
            pageToken = page_token,
            maxResults = 500
        ).execute()

        messages = response.get('messages',[])

        if not messages:
            break

        batch = service.new_batch_http_request()

        for message in messages:
            batch.add(service.users().messages().delete(userId = 'me',id = message['id']))
        batch.execute()

        total_deleted += len(messages)

        page_token = response.get('nextPageToken')
        
        if not page_token:
            break

    return total_deleted


def search_emails(service, query, user_id='me', max_results=5):
    messages = []
    next_page_token = None

    while True:
        result = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=min(500, max_results - len(messages)) if max_results else 500,
            pageToken=next_page_token
        ).execute()

        messages.extend(result.get('messages', []))

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages)) >= max_results:
            break

    return messages[:max_results] if max_results else messages


def search_email_conversations(service, query, user_id='me', max_results=5):
    conversations = []
    next_page_token = None

    while True:
        result = service.users().threads().list(
            userId=user_id,
            q=query,
            maxResults=min(500, max_results - len(conversations)) if max_results else 500,
            pageToken=next_page_token
        ).execute()

        conversations.extend(result.get('threads', []))

        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(conversations)) >= max_results:
            break

    return conversations[:max_results] if max_results else conversations

def modify_email_labels(service, user_id, message_id, add_labels=None, remove_labels=None):
    def batch_labels(labels, batch_size=100):
        return [labels[i:i + batch_size] for i in range(0, len(labels), batch_size)]

    if add_labels:
        for batch in batch_labels(add_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'addLabelIds': batch}
            ).execute()

    if remove_labels:
        for batch in batch_labels(remove_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'removeLabelIds': batch}
            ).execute()
