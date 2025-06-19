import os
from typing import List, TypedDict, Annotated
from langgraph.types import interrupt, Command
from langgraph.graph import add_messages

class resumeState(TypedDict):
    resume_path: str

folder_id = "1kDjNAWM4bE_QKpAGd_FPzJY3bhTGPctF"
folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

download_path = r"C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes"

def check_CVs(state: resumeState):
    if os.path.exists(state['resume_path']):
        print("File already exists in designated folder.")
        return state['resume_path']
    else:
        return Command(
            goto="choose_download"
        )

def choose_download(state: resumeState):
    value = interrupt(
        {
            "question": "Provide Google Drive Link for the Resumes:"
        }
    )
    print(f"User asked to download files from: {value}")

    os.system(f"gdown --folder {value}")

    return state


























# import os
# from typing import List, Dict
# from langgraph.types import interrupt, Command
# from typing import TypedDict, Annotated,List,Dict
# from langgraph.graph import add_messages, StateGraph, END
# import os

# folder_id = "1kDjNAWM4bE_QKpAGd_FPzJY3bhTGPctF"

# folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

# class logState(TypedDict):
#     Logs : Annotated[List, add_messages]


# def check_CVs(state : logState):
#     if os.path.exists(r'C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes'):
#         state['Logs'] = f"File already exists in Designated folder "
#         print(state['Logs'][-1])
#         return 'C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes'
#     else:
#         Command(
#             goto=choose_download()
#         )
#         os.system(f"gdown --folder {folder_url}")


#     return os.path.join('.\\','Candidate Resumes')

        
# def choose_download(state : logState):
#     value = interrupt(
#         {
#             "question" : " Provide Google Drive Link for the Resumes : "

#         }
#     )
#     state["Logs"]  = f'user asked to download files in :  {value}'
#     print(state['Logs'][-1])

#     return value



