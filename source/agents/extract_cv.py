import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime,timedelta
import chromadb
import warnings
import io
import contextlib

load_dotenv()
warnings.filterwarnings("ignore", message="CropBox missing from /Page")



client = chromadb.PersistentClient(path="../Databases/Candidate_Database")
corrupt_db = client.get_or_create_collection(name="Corrupt_files")
valid_db = client.get_or_create_collection(name="Valid_candidates")




llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))


class Candidate(BaseModel):
    """Information about the resume"""

    name: str = Field(..., description="Name of the Candidate")
    experience: str = Field(..., description="job role : duration in years ")
    education: str = Field(..., description="Key: institute name, Value: course")
    location: str = Field(..., description="State the candidate lives in")
    skills: List[str] = Field(..., description="List of skills written by user")
    email : str = Field(...,description="Email of the user")


structured_llm = llm.with_structured_output(Candidate)



def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):        
            print (f"opening {file_path} as pdf")
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    print (f"opening {file_path} as docx")
    return "\n".join([para.text for para in doc.paragraphs])

def load_resume(file_path,corrupt_db):
    try:
        if file_path.endswith(".pdf"):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            return extract_text_from_docx(file_path)
    except Exception as e:
        print(f'Error processing file {file_path}')
        corrupt_db.add(
            documents=[os.path.basename(file_path)],
            metadatas=[{"status": "corrupt"}],
            ids=[os.path.basename(file_path)]
        )
        return None





def is_already_processed(filename,valid_db):
    try:
        print(f"checking existence of {filename}")
        result = valid_db.get(ids=[filename])
        
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




def extract_resume(folder_path,valid_db,corrupt_db):
    current_date = datetime.now().strftime("%Y-%m-%d")

    list_of_candidates = []

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            full_path = os.path.join(folder_path, filename)


            if is_already_processed(filename,valid_db):
                print(f"{filename} already processed.")
                continue


            content = load_resume(full_path,corrupt_db)

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

            valid_db.add(
            documents=[response.model_dump_json()],
            metadatas=[{"status": "valid",
                        "date" : current_date}],
            ids=[filename]
            )
        


        return list_of_candidates

