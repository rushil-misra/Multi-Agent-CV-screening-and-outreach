from agents.download_cv import check_CVs
from agents.extract_cv import extract_resume
from agents.extract_jd import choose_jd
from agents.functions3 import connect_sheet,push_data_to_sheet
from agents.functions4 import email_shortlist
from subgraph_interview import interview_subgraph, interview_config
import chromadb
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import interrupt, Command

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))




langsmith_tracing = os.getenv("LANGSMITH_TRACING")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")


client = chromadb.PersistentClient(path="../Databases/Candidate_Database2")
corrupt_db = client.get_or_create_collection(name="Corrupt_files")
valid_db = client.get_or_create_collection(name="Valid_candidates")
JD_db = client.get_or_create_collection(name="Job_Descriptions")

class JobState(TypedDict):
    resume_path : str
    logs : Annotated[List, add_messages]
    Job_Description : Dict
    candidates: List[Dict]
    Interview: List[Dict]
    Result_list: List


def node_check_cvs(state: JobState):
    check_cv_input = {
        'resume_path' : state['resume_path']
    }
    folder = check_CVs(check_cv_input) 
    state['resume_path'] = folder
    print("="*10,"resumes download done","="*10)
    return state


def node_choose_jd(state: JobState):
    jd = choose_jd(JD_db)  
    state['Job_Description'] = jd
    print("="*10, 'extracting jd done',"="*10)
    print(f'current jd Database \n {JD_db.get()} \n ')
    return state


def node_parse_resumes(state: JobState):
    candidates = extract_resume(state['resume_path'], valid_db, corrupt_db)
    state['candidates'] = candidates
    print("="*10,'extracting resumes done',"="*10)
    print(f' current corrupt file database \n {corrupt_db.get()} \n')
    print(f'current valid candidate database \n {valid_db.get()} \n ')
    print(f'candidate list -- \n {candidates} \n ')
    return state


def node_new_candidate(state :JobState):
    if len(state['candidates']) < 1:
        print('No new Candidates ')
        print('='*20)
        return Command(
            goto = 'End'
        )
        
    else:
        return state

def node_interview(state: JobState):
    if len(state['candidates']) < 1:
        print('ALL CANDIDATES ARE ALREADY PROCESSED')
        return None

    candidate = state["candidates"][0]
    
    sub_input = {
        "jd": state["Job_Description"],
        "resume": candidate,
        "messages": [],
    }

    sub_output = interview_subgraph.invoke(sub_input, config=interview_config)
    print("sub_output returned:", sub_output)
    state["Interview"].append(sub_output)
    print("="*10, 'interview done', "="*10)
    print(f' result \n {state["Interview"]} \n')
    
    
    decision = sub_output.get("decision", {})

    result_row = [
        candidate.get("name", ""),
        decision.get("status", ""),
        decision.get("reason", ""),
        candidate.get("email", "")
    ]
    
    state["Result_list"].append(result_row)


    return state


def node_sheet(state : JobState):
    print('RESULT LIST -- \n', state['Interview'], 'Result list new -- \n', state['Result_list'])
    sheet = connect_sheet("Task_1")
    push_data_to_sheet(sheet,state['Result_list'])
    return None

def node_email(state : JobState):
    return email_shortlist()


builder = StateGraph(JobState)

builder.add_node("Check_CVs", node_check_cvs)
builder.add_node("Choose_JD", node_choose_jd)
builder.add_node("Parse_Resumes", node_parse_resumes)
builder.add_node("check new candidates",node_new_candidate)
builder.add_node("interview",node_interview)
builder.add_node('Sheet',node_sheet)
builder.add_node('Email', node_email)
# builder.add_node('END',END)


builder.set_entry_point("Check_CVs")

builder.add_edge("Check_CVs", "Choose_JD")
builder.add_edge("Choose_JD", "Parse_Resumes")
builder.add_edge("Parse_Resumes", "check new candidates")
builder.add_edge("check new candidates","interview")
builder.add_edge("interview", "Sheet")
builder.add_edge("Sheet", "Email")
# builder.add_edge("Email", "END")

builder.set_finish_point('Email')





graph = builder.compile()

# graph.get_graph().print_ascii()



graph.invoke({"resume_path" : r"C:\Users\Rushil Misra\Documents\projects\Multi Agent CV screener\source\Candidate Resumes",
              "Interview": [],
              'Result_list': []
              })
