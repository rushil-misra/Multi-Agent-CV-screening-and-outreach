from functions3 import connect_sheet

from gmail.gmail_api import init_gmail_service,send_email
from pathlib import Path




def email_shortlist():
    sheet = connect_sheet('Task_1')


    raw_values = sheet.get_all_values()


    addressees = []

    for row in raw_values:
        if row[1] == "Shortlisted":
            addressees.append(row[3])


    client_file = r'..\gmail\client_secret.json'
    service = init_gmail_service(client_file)


    to_address = "rushilmisra@gmail.com"
    email_subject = 'Congratulations, You are shortlisted!'
    email_body = "Join this link for meeting ------meeting link------------------"


    for addressee in addressees:
        print(f"addressees -- {addressee}")
        response_email_sent = send_email(
        service,
        to_address,
        email_subject,
        email_body,
        body_type='plain',

    )

    return response_email_sent

email_shortlist()