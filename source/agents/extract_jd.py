import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
import chromadb

load_dotenv()



import warnings
warnings.filterwarnings("ignore", message="CropBox missing from /Page")

client = chromadb.PersistentClient(path="../Databases/Candidate_Database")
JD_db = client.get_or_create_collection(name="Job_Descriptions")




llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))



def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
    

class Qualifications(BaseModel):
    """Required qualifications for the job role"""
    Job_Role : str = Field(description='name of the Job Role')
    locations: List[str] = Field(..., description="Locations of offices for work")
    required_experience: str = Field(..., description="Minimum number of experience required in years")
    Domain_relevance: List[str] = Field(..., description="Relevant Domains for job")
    Domain_KRA: List[str] = Field(..., description="Key Skills required in that Area")


qualify_llm = llm.with_structured_output(Qualifications)


def modify_qual(response):
    review = input(f"current qualifications : \n {response} \n would you like to suggest changes ? (yes/no)")
    if review.lower() == "no":
        return False,None
    else:
        feedback = input('tell what changes should be made to the qualifications')
        return True,feedback


def extract_qualifications(file_path):
    try:
        if file_path.endswith(".pdf"):
            content =  extract_text_from_pdf(file_path)
    except:
        return "file is corrupt"
    
    response = qualify_llm.invoke(f''' You have to go through the job descriptions and find relevant job qualifications :
                       Job_Role = Name of the job role
                       Locations = [location1,location2,...]
                       required_experience = 5 (minimum years of experience)
                       Domain_relevance = [Domain1,Domain2,...]
                       Domain_KRA = [skill1,skill2,...]

                       Job Description = 
                       {content}
                       ''')
    review, feedback = modify_qual(response)
    if review:
        res = qualify_llm.invoke(f'''
                                modify the previous job qualifications with changes suggested by the user 
                                previous qualifications = 
                                {response}

                                suggested modifications = 
                                
                                {feedback}


                                ''')
    else:
        res = response
    res = res.model_dump()

    JD_db.add(
    ids=[res["Job_Role"]],
    documents=[str(res)]
    )
    return res

def choose_jd(JD_Db):
    existing_job_roles = JD_Db.get()
    choose = input(f"These are the existing Job roles in the Database -- \n {existing_job_roles['ids']} \n Type 1 to choose existing and 0 to enter a new JD")
    if choose == '1':
        option = input('write down the existing job role you choose--')
        jd = JD_Db.get(ids=[option], include=["documents"])

        return jd
    else:
        jd_path = input('enter path of the new job role -- ')
        return extract_qualifications(jd_path)
    
        
