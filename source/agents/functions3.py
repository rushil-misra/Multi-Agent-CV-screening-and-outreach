import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))

def connect_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\gSpread_key.json", scope)
    client = gspread.authorize(creds)
    for spreadsheet in client.openall():
        print(spreadsheet.title)
    sheet = client.open(sheet_name).sheet1
    return sheet



def summarize_reason(long_reason: str) -> str:
    prompt = f"Summarize this candidate rejection/shortlisting reason in one short sentence:\n{long_reason}"
    return llm.invoke(prompt).content.strip()

def push_data_to_sheet(sheet, data_list):
    if sheet.row_count == 0 or not sheet.get_all_values():
        sheet.append_row(["Name", "Status", "Short Reason", "Email","Date","Contact"])

    for entry in data_list:
        long_reason = entry.get("Reason", "")
        short_reason = summarize_reason(long_reason) if long_reason else ""

        row = [
            entry.get("Name", ""),
            entry.get("Status", ""),
            short_reason,
            entry.get("Email", ""),
            datetime.now().strftime("%Y-%m-%d")
        ]
        sheet.append_row(row)

        



# sheet = connect_sheet("Task_1")

# push_data_to_sheet(sheet,data )

