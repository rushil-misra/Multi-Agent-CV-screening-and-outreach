from gmail_api import init_gmail_service,search_emails,trash_email,batch_trash_emails,empty_trash, recover_email,get_email_message_details,modify_email_labels


client_file = 'client_secret.json'
service = init_gmail_service(client_file)


query = 'Frome:me'

email_messages = search_emails(service,query,max_results=5)

for email_message in email_messages:
    email_message_detail  = get_email_message_details(service,email_message['id'])
    trash_email(service,'me',email_message['id'])
    print(f'email <{email_message_detail}> moved to trash')

    # recover email 

query = 'In:trash'

email_messages = search_emails(service,query,max_results=2)

for email_message in email_messages:
    email_message_detail  = get_email_message_details(service,email_message['id'])
    print(f'email <{email_message_detail}> are recovered')
    recover_email(service,'me',email_message['id'])

    modify_email_labels(service,'me',email_message['id'],add_labels = ['INBOX'])


