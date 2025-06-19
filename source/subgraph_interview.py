
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated,List,Dict
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage,BaseMessage
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=os.getenv("GEMINI_API_KEY"))

memory = MemorySaver()

langsmith_tracing = os.getenv("LANGSMITH_TRACING")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
langsmith_project = os.getenv("LANGSMITH_PROJECT")

class interviewState(TypedDict):
    jd : Dict
    resume : Dict
    messages : Annotated[List[BaseMessage], add_messages]
    decision : Dict


def agent_employer(state : interviewState):
    employer_message = (llm.invoke([HumanMessage(content=f'''
You are an employer interviewing a candidate. your goal is to ask job related questions.
Ask one question at a time
Job Qualifications :
{state['jd']}

Ask suitable questions related to Job Description only.
Below is the chat history till now. 

{state['messages']}



''')])).content
    state['messages'].append(HumanMessage(content = employer_message))
    print('='*10)
    print(state['messages'][-1])
    return state

def agent_candidate(state : interviewState):
    candidate_message = (llm.invoke([HumanMessage(content=f'''
You are a candidate giving job interview. Answer the question based on your resume.
Resume :
{state['resume']}

Answer Short and precise.
Below is the chat history till now. 

{state['messages']}



''')])).content
    
    state['messages'].append(HumanMessage(content = candidate_message))
    print('='*10)
    print(state['messages'][-1])

    return state

from pydantic import BaseModel, Field

class InterviewDecision(BaseModel):
    status: str = Field(..., description="Shortlisted or Rejected")
    reason: str = Field(..., description="Reason for the decision")

judge_llm = llm.with_structured_output(InterviewDecision)


def agent_judge(state: interviewState):
    messages = state['messages']
    print(f'length of conversation - {len(messages)}')

    if (len(messages)-1)//2 < 3:
        print('conversation too short')
        return "resume"
    elif (len(messages)-1)//2 > 6:
        structured_response = judge_llm.invoke([
        HumanMessage(content=f"""
You are the interviewer. Based on the full conversation, decide whether to Shortlist or Reject the candidate.

Output must follow this structure:
- status: Shortlisted or Rejected
- reason: One-line justification

messages : 

{state['messages']}
""")
])

        state['decision'] = structured_response.model_dump()
        # print(f'Interview logs --- \n {state['messages']} \n')
        print(f'judge made its decision \n {state['decision']}\n')

        return "final"

    judge_check = llm.invoke([
        HumanMessage(content=f"""Would you like to continue the interview?
                     Try to Make a decision within 6 turns of QnA.
                     Respond only with 'Resume' or 'Make a decision'. messages - 
        {state['messages']}"""
    )])

    if "resume" in judge_check.content.lower():
        print('judge decided to continue')
        return "resume"

    structured_response = judge_llm.invoke([
        HumanMessage(content=f"""
You are the interviewer. Based on the full conversation, decide whether to Shortlist or Reject the candidate.

Output must follow this structure:
- status: Shortlisted or Rejected
- reason: One-line justification

messages : 

{state['messages']}
""")
])

    state['decision'] = structured_response.model_dump()
    # print(f'Interview logs --- \n {state['messages']} \n')
    print(f'judge made its decision \n {state['decision']}\n')

    return "final"

builder = StateGraph(interviewState)




builder.add_node("employer",agent_employer)
builder.add_node("candidate",agent_candidate)
builder.add_node("judge",agent_judge)

builder.add_edge('employer','candidate')

builder.set_entry_point('employer')

builder.add_conditional_edges(
    "candidate",
    agent_judge,
    {
        "resume" : "employer",
        "final" : END
    }
)

interview_subgraph = builder.compile(checkpointer=memory)

interview_config = {"configurable": {
    "thread_id": 1
}}

interview_subgraph.invoke(
    {
        'jd' : {'Job_Role':'Process Excellence & Inventory Lead',
                'locations':['Gurugram', 'Bhiwandi', 'Bangalore', 'Kolkata'] ,
                'required_experience':'5' ,
                'Domain_relevance':['B2B', 'B2C operations', 'WMS/OMS platforms', 'logistics'] ,
                'Domain_KRA':['Process Excellence', 'inventory management', 'Manpower Planning', 'Warehouse Utilization', 'SOP Implementation', 'Technology Adoption', 'Safety', 'Security', 'Loss Prevention']},
        'resume' : {"name":"Akshay Bajaj",
                    "experience":["Senior Manager - Operational Excellence & Inventory Management (Seabird Logisolution Pvt ltd):Present","Apollo Supply chain pvt ltd:Oct,24","Oppo Mobiles India Pvt Ltd:Sep,21","Autoliv India Pvt Ltd:Mar  21","Autoliv India Pvt Ltd:Apr 16","Maruti Suzuki India Ltd:Jun 14"],
                    "education":["Delhi Institute of Technology Management, MDU:Bachelor of Technology (Mechanical Engineering)"],
                    "location":"Gurgaon",
                    "skills":["Six Sigma Green Belt","Lean thinking","Process analysis & optimization","Data Analysis","Project management","Communication & collaboration","Problem solving","Leadership"],
                    "email":"bajajakshay13@gmail.com"},
        'messages' : [HumanMessage(content = 'Start the interview')]
    },
    config=interview_config
)
