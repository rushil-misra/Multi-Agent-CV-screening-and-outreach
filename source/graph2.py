from agents.download_cv import check_CVs
from agents.extract_cv import extract_resume
from agents.extract_jd import choose_jd
from subgraph_interview import interview_subgraph, interview_config
import chromadb
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))


client = chromadb.PersistentClient(path="../Databases/Candidate_Database")
corrupt_db = client.get_or_create_collection(name="Corrupt_files")
valid_db = client.get_or_create_collection(name="Valid_candidates")
JD_db = client.get_or_create_collection(name="Job_Descriptions")

class JobState(TypedDict):
    resume_path : str
    logs : Annotated[List, add_messages]
    Job_Description : Dict
    candidates: List[Dict]
    Interview: Dict


def node_check_cvs(state: JobState):
    folder = check_CVs(state) 
    state['folder_path'] = folder
    return state


def node_choose_jd(state: JobState):
    jd = choose_jd(JD_db)  
    state['jd'] = jd
    return state


def node_parse_resumes(state: JobState):
    candidates = extract_resume(state['folder_path'], valid_db, corrupt_db)
    state['candidates'] = candidates
    return state


def node_interview(state: JobState):
    sub_input = {
        "jd": state["Job_Description"],
        "resume": state["candidates"][0],
        "messages": [],
    }
    sub_output = interview_subgraph.invoke(sub_input,config=interview_config)
    state["Interview"] = sub_output
    return state


builder = StateGraph(JobState)

builder.add_node("Check_CVs", node_check_cvs)
builder.add_node("Choose_JD", node_choose_jd)
builder.add_node("Parse_Resumes", node_parse_resumes)
builder.add_node("interview",node_interview)


builder.set_entry_point("Check_CVs")

builder.add_edge("Check_CVs", "Choose_JD")
builder.add_edge("Choose_JD", "Parse_Resumes")
builder.add_edge("Parse_Resumes", "interview")




graph = builder.compile()

