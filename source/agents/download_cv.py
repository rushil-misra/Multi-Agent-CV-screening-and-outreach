import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime,timedelta
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, END
from agents.functions import extract_resume, download_cv
from agents.functions2 import extract_qualifications,shortlisting
from agents.functions3 import connect_sheet,push_data_to_sheet
from agents.functions4 import email_shortlist
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
import os

folder_id = "1kDjNAWM4bE_QKpAGd_FPzJY3bhTGPctF"

folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

class logState(TypedDict):
    Logs : Annotated[List, add_messages]


def check_CVs(state : logState):
    if os.path.exists(r'C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes'):
        state['Logs'] = f"File already exists in Designated folder "
        return "CVs are downloaded"
    else:
        link = choose_download()
        os.system(f"gdown --folder {folder_url}")

    return os.path.join('.\\','Candidate Resumes')

        
def choose_download(state : logState):
    value = interrupt(
        {
            "question" : " Provide Google Drive Link for the Resumes : "

        }
    )
    state["Logs"]  = f'user asked to download files in :  {value}'
    return value



