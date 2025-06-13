import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict

load_dotenv()



import warnings
warnings.filterwarnings("ignore", message="CropBox missing from /Page")




llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))



def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
    

class Qualifications(BaseModel):
    """Required qualifications for the job role"""

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
                       Locations = [location1,location2,...]
                       required_experience = 5 (minimum years of experience)
                       Domain_relevance = [Domain1,Domain2,...]
                       Domain_KRA = [skill1,skill2,...]

                       Job Description = 
                       {content}
                       ''')
    review, feedback = modify_qual(response)
    if review:
        return qualify_llm.invoke(f'''
                                modify the previous job qualifications with changes suggested by the user 
                                previous qualifications = 
                                {response}

                                suggested modifications = 
                                
                                {feedback}


                                ''')
    else:
        return response
    # allow user to make changes using human in the loop later
    
class Shortlist(BaseModel):
    """shortlisting or rejecting the candidate based on their skill vs qualification"""
    Name : str = Field(..., description="Name of the ")
    Status: str = Field(..., description="Shortlisted/Rejected")
    Reason: str = Field(..., description="reason for shortlisting/rejecting the candidate")
    Email: str = Field(...,description="Email of the Candidate")



Shortlister= llm.with_structured_output(Shortlist)


def shortlisting(candidate,qualification_for_job):

    
    response = Shortlister.invoke(f''' Compare the candidate skills and job qualification criteria and decide whether to reject the candidate or shortlist.
                            possible decision criteria could be - not being in the same location as the job, having low experience, irrevelant skills,etc.
                            Name : Name of the Candidate
                            Status : shortlisted / rejected
                            Reason : reason for shortlisting/rejecting
                            Email : Email of the Candidate

                            Candidate info = 
                            {candidate}

                            
                            job qualifications = 
                            {qualification_for_job}
                            ''')
        
    return response.model_dump()

