from agents.download_cv import check_CVs
from agents.extract_cv import extract_resume
from agents.extract_jd import choose_jd
import chromadb
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
import os


client = chromadb.PersistentClient(path="../Databases/Candidate_Database")
corrupt_db = client.get_or_create_collection(name="Corrupt_files")
valid_db = client.get_or_create_collection(name="Valid_candidates")
JD_db = client.get_or_create_collection(name="Job_Descriptions")

class JobState(TypedDict):
    resume_path : str
    logs : Annotated[List, add_messages]
    Job_Description : Dict
    candidates: List[Dict]


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

builder = StateGraph(JobState)

builder.add_node("Check_CVs", node_check_cvs)
builder.add_node("Choose_JD", node_choose_jd)
builder.add_node("Parse_Resumes", node_parse_resumes)

builder.set_entry_point("Check_CVs")

builder.add_edge("Check_CVs", "Choose_JD")
builder.add_edge("Choose_JD", "Parse_Resumes")
builder.add_edge("Parse_Resumes", END)

graph = builder.compile()

