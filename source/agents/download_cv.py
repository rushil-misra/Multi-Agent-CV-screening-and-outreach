import os
from typing import List, Dict
from langgraph.types import interrupt, Command
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
import os

folder_id = "1kDjNAWM4bE_QKpAGd_FPzJY3bhTGPctF"

folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

class logState(TypedDict):
    Logs : Annotated[List, add_messages]


def check_CVs(state : logState):
    if os.path.exists(r'C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes'):
        state['Logs'] = f"File already exists in Designated folder "
        return None
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



