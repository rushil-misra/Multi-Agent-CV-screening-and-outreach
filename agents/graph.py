from langgraph.graph import StateGraph, END
from functions import extract_resume, download_cv
from functions2 import extract_qualifications,shortlisting
from functions3 import connect_sheet,push_data_to_sheet
from functions4 import email_shortlist
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage
import os


class jobState(TypedDict):
    resume_path: str
    candidate_list : List[Dict]
    candidate : Dict
    Result_list : List[Dict]

    
langsmith_tracing = os.getenv("LANGSMITH_TRACING")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")


def agent_0(state : jobState):
    download_cv()
    return None

def agent_1(state: jobState):
    return {
        "candidate_list": [extract_resume(state["resume_path"])], 
    }

def agent_2(state : jobState):
    result_list = []
    filepath = r'C:\Users\Rushil Misra\Documents\projects\Sanskar\Task_1\agents\JD.pdf'
    qualifications = extract_qualifications(filepath)


    for candidate in state['candidate_list'][0]:
        result = shortlisting(candidate,qualifications)
        result_list.append(result)
        print(f'\n{result}\n')

    print(f"result --- {result_list}")

    return {
        "Result_list" : result_list
    }

def agent_3(state : jobState):
    sheet = connect_sheet("Task_1")
    push_data_to_sheet(sheet,state['Result_list'])
    return None

def agent_4(state : jobState):
    return email_shortlist()



graph = StateGraph(jobState)
graph.add_node('agent_0',agent_0)
graph.add_node('agent_1', agent_1)
graph.add_node('agent_2',agent_2)
graph.add_node('agent_3',agent_3)
graph.add_node('agent_4',agent_4)

graph.add_edge("agent_0","agent_1")
graph.add_edge("agent_1","agent_2")
graph.add_edge("agent_2","agent_3")
graph.add_edge("agent_3","agent_4")



graph.set_entry_point("agent_0")

multi_agent = graph.compile()

from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod




multi_agent.invoke({'resume_path': r'C:\Users\Rushil Misra\Documents\projects\Sanskar\Task_1\agents\Candidate Resumes'})

# search_app.invoke({"messages": [HumanMessage(content="How is the weather in Chennai?")]})






'''
AGENT 1
# ● Input: CVs from a Google Drive folder or email inbox.
# ● Use memory or DB to check if a candidate has already been screened in the past 30 days.

AGENT 2
# Allow screening criteria to be updated dynamically by a Meta-Agent or manually
through an admin dashboard.

AGENT 3
# ● For each decision, generates a 1-liner plain-English justification
    e.g., “Rejected due to location mismatch”

This agent logs patterns over time (e.g., 40% rejected for location) and submits summary
stats to the Meta-Agent weekly.


AGENT 4 
● Log all outreach attempts and statuses (opened, replied, clicked link) in a central store.


'''














































# def resume_agent_node(state):
#     print("🧾 Extracting resumes...")
#     candidates = extract_resume(state["folder_path"])
#     return {"candidates": candidates}

# def screening_agent_node(state):
#     print("✅ Screening candidates...")
#     results = []
#     for candidate in state["candidates"]:
#         result = shortlisting(candidate)
#         results.append({
#             "candidate": candidate,
#             "decision": result
#         })
#     return {"screened": results}

# builder = StateGraph()

# builder.add_node("Extract_Resumes", RunnableLambda(resume_agent_node))
# builder.add_node("Screen_Candidates", RunnableLambda(screening_agent_node))

# builder.set_entry_point("Extract_Resumes")
# builder.add_edge("Extract_Resumes", "Screen_Candidates")
# builder.add_edge("Screen_Candidates", END)

# graph = builder.compile()

# # Run
# output = graph.invoke({"folder_path": r"C:\Users\Rushil Misra\Documents\projects\Sanskar\Task_1\agents\Candidate Resumes"})
