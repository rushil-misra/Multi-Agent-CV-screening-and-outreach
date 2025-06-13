import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime,timedelta

import io
import contextlib


load_dotenv()



import warnings
warnings.filterwarnings("ignore", message="CropBox missing from /Page")



import chromadb

client = chromadb.PersistentClient(path="../Databases/Candidate_Database")


collection = client.get_or_create_collection(name="Task")








llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))



# class Candidate(BaseModel):
#     """Information about the resume"""

#     name: str = Field(..., description="Name of the Candidate")
#     language: Dict[str, int] = Field(..., description="Key: job role, Value: duration in months")
#     education: Dict[str, str] = Field(..., description="Key: institute name, Value: course")
#     location: str = Field(..., description="State the candidate lives in")
#     skills: List[str] = Field(..., description="List of skills written by user")
 
class Candidate(BaseModel):
    """Information about the resume"""

    name: str = Field(..., description="Name of the Candidate")
    experience: str = Field(..., description="job role : duration in years ")
    education: str = Field(..., description="Key: institute name, Value: course")
    location: str = Field(..., description="State the candidate lives in")
    skills: List[str] = Field(..., description="List of skills written by user")
    email : str = Field(...,description="Email of the user")


structured_llm = llm.with_structured_output(Candidate)






folder_id = "1kDjNAWM4bE_QKpAGd_FPzJY3bhTGPctF"

folder_url = f"https://drive.google.com/drive/folders/{folder_id}"



def download_cv():
    if os.path.exists('Candidate Resumes'):
        pass
    else:
        os.system(f"gdown --folder {folder_url}")

    return os.path.join('.\\','Candidate Resumes')



def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):        
            print (f"opening {file_path} as pdf")
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    print (f"opening {file_path} as docx")
    return "\n".join([para.text for para in doc.paragraphs])

def load_resume(file_path):
    try:
        if file_path.endswith(".pdf"):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            return extract_text_from_docx(file_path)
    except Exception as e:
        print(f'Error processing file {file_path}')
        collection.add(
            documents=[os.path.basename(file_path)],
            metadatas=[{"status": "corrupt"}],
            ids=[os.path.basename(file_path)]
        )
        return None





def is_already_processed(filename):
    try:
        print(f"checking existence of {filename}")
        result = collection.get(ids=[filename])
        
        if not result['ids']:
            print(f'new file - {filename}')
            return False  # Not processed before

        metadata = result['metadatas'][0]  # get metadata of the found ID
        processed_date_str = metadata.get("date")

        if processed_date_str:
            processed_date = datetime.strptime(processed_date_str, "%Y-%m-%d")
            if datetime.now() - processed_date <= timedelta(days=30):
                print(f'\nThis file was already processed within the last 30 days: {processed_date_str}\n')
                return True
            else:
                print(f'\nThis file was processed more than 30 days ago: {processed_date_str}\n')
                return False
        else:
            print("No date in metadata, treating as new.")
            return False
    except Exception as e:
        print(f"Error checking DB: {e}")
        return False




def extract_resume(folder_path):
    current_date = datetime.now().strftime("%Y-%m-%d")

    list_of_candidates = []

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)


            if is_already_processed(filename):
                print(f"{filename} already processed.")
                continue


            content = load_resume(full_path)

            if content is None:
                continue
            response = structured_llm.invoke(f'''Extract the following information from the resume text below:
- Name
- Years of Experience (numeric if possible)
- Education (degree + college)
- Location (city or region)
- Skills (comma-separated)
- Email 


RESUME TEXT:
{content}
            
''')

            
            print(f"adding new candidate for shortlisting --- {response.name}")
            print(f'\n {response} \n')

            list_of_candidates.append(response.model_dump())

            collection.add(
            documents=[response.name],
            metadatas=[{"status": "valid",
                        "date" : current_date}],
            ids=[filename]
            )
        


        return list_of_candidates



# print(extract_resume(r'C:\Users\Rushil Misra\Documents\projects\Sanskar\Task_1\agents\Candidate Resumes'))


# from langgraph.graph import StateGraph, END
# from langchain_core.runnables import RunnableLambda
# from functions import extract_resume
# from functions2 import shortlisting
# from typing import TypedDict, Annotated,List,Dict
# from langgraph.graph import add_messages, StateGraph, END
# from langchain_core.messages import AIMessage, HumanMessage


# class agent1_state(TypedDict):
#     filePath : str
#     candidate_list : List


# graph = StateGraph(agent1_state)

# def agent(state: agent1_state):
#     return {
#         "candidate_list": [extract_resume(state["filePath"])], 
#     }

