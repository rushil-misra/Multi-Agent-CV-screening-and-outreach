from gmail_api import init_gmail_service,get_email_messages,get_email_message_details

client_file = 'client_secret.json'

service = init_gmail_service(client_file)


messages = get_email_messages(service,max_results=5)

for msg in messages:
    details = get_email_message_details(service,msg['id'])

    if details:
        print(f"subject : {details['subject']}")
        print(f"from : {details['sender']}")
        print(f"recipients: {details['recipients']}")
        print(f"body : {details['body'][:100]}....")
        print(f"Snippet: {details['snippet']}")
        print(f"has_attachments : {details['has_attachments']}")
        print(f"date : {details['date']}")
        print(f"star : {details['star']}")
        print(f"label : {details['label']}")
        print("-" * 50)
