from gmail_api import init_gmail_service, get_email_message_details, search_emails, search_email_conversations

client_file = 'client_secret.json'
service = init_gmail_service(client_file)

print("Gmail v1 service created successfully")

query = 'from:me'
email_messages = search_emails(service, query, max_results=30)

for message in email_messages:
    email_detail = get_email_message_details(service, message['id'])
    print(f"ID: {message['id']}")
    print(f"Subject: {email_detail['subject']}")
    print(f"Date: {email_detail['date']}")
    print(f"Label: {email_detail['label']}")
    print(f"Snippet: {email_detail['snippet']}")
    print(f"Body: {email_detail['body']}")
    print('-' * 50)
