
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))

memory = MemorySaver()


class interviewState(TypedDict):
    jd : Dict
    resume : Dict
    messages : Annotated[List, add_messages]
    decision : Dict


def agent_employer(state : interviewState):
    state['messages'] = (llm.invoke([SystemMessage(content=f'''
You are an employer interviewing a candidate. your goal is to ask job related questions.
Job Qualifications :
{state['jd']}

Ask suitable questions related to Job Description only
''')])).content
    return state

def agent_candidate(state : interviewState):
    state['messages'] = (llm.invoke([SystemMessage(content=f'''
You are a candidate giving job interview. Answer the question based on your resume.
Resume :
{state['resume']}
''')])).content
    return state

from pydantic import BaseModel, Field

class InterviewDecision(BaseModel):
    status: str = Field(..., description="Shortlisted or Rejected")
    reason: str = Field(..., description="Reason for the decision")

judge_llm = llm.with_structured_output(InterviewDecision)


def agent_judge(state: interviewState):
    messages = state['messages']

    if len(messages) < 3:
        return "continue"

    judge_check = llm.invoke([
        SystemMessage(content=f"""Would you like to continue the interview? Respond only with 'Continue' or 'Make a decision'. messages - 
        {state['messages']}"""
    )])

    if "continue" in judge_check.content.lower():
        return "continue"

    structured_response = judge_llm.invoke([
        SystemMessage(content=f"""
You are the interviewer. Based on the full conversation, decide whether to Shortlist or Reject the candidate.

Output must follow this structure:
- status: Shortlisted or Rejected
- reason: One-line justification

messages : 

{state['messages']}
""")
])

    state['decision'] = structured_response.model_dump()
    print(f'Interview logs --- \n {state['messages']} \n')

    return "final"

builder = StateGraph(interviewState)




builder.add_node("employer",agent_employer)
builder.add_node("candidate",agent_candidate)
builder.add_node("judge",agent_judge)

builder.add_edge('employer','candidate')
builder.add_edge('candidate','judge')

builder.set_entry_point('employer')

builder.add_conditional_edges(
    "judge",
    agent_judge,
    {
        "continue" : "employer",
        "final" : END
    }
)

interview_subgraph = builder.compile(checkpointer=memory)

interview_config = {"configurable": {
    "thread_id": 1
}}