import os
from docx import Document
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
import os


load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))


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



class interviewState(TypedDict):
    messages : Annotated[List, add_messages]

# def agent_candidate(state : interviewState):
