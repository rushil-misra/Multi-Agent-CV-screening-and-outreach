from agents.functions3 import connect_sheet
from gmail.gmail_api import init_gmail_service, send_email
from pathlib import Path

def email_shortlist():
    sheet = connect_sheet('Task_1')
    all_rows = sheet.get_all_values()

    # Assume first row is header
    header = all_rows[0]
    rows = all_rows[1:]

    # Find the column indexes
    name_col = header.index("Name")
    email_col = header.index("Email")
    status_col = header.index("Status")
    contact_col = header.index("Contact")

    client_file = r'C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\gmail\client_secret.json'
    service = init_gmail_service(client_file)

    email_subject = 'Congratulations, You are shortlisted!'
    email_body = "Join this link for meeting ------meeting link------------------"

    for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header
        status = row[status_col].strip().lower()
        contact_status = row[contact_col].strip().lower() if len(row) > contact_col else ""

        if status == "shortlisted" and contact_status != "yes":
            to_address = row[email_col]
            print(f"Sending to: {to_address}")

            send_email(
                service,
                'swmonke@gmail.com',
                email_subject,
                email_body,
                body_type='plain',
            )

            sheet.update_cell(i, contact_col + 1, "Yes") 

    print(" Emails sent and sheet updated")
