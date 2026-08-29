"""
src/agents/outreach_agent.py

Institutional Feeder Network & Outreach Worker Agent.
Coordinates partner high school / PU college bulk onboarding, masterclass scheduling,
and free technical workshop discovery (Generative AI, Robotics, VLSI).
"""

from typing import Any, Dict, List
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentActionMedia, AgentState
from src.agents.tools import execute_college_sql
from src.core.config import settings

llm = ChatGroq(
    model_name=settings.GROQ_MODEL_NAME,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0.1,
)

OUTREACH_PROMPT = """You are the Institutional Outreach Coordinator at PragyanAI College Hub.
Your task is to assist School Principals, PU College Counselors, and Prospective Students to:
1. Discover free online masterclasses (Generative AI & LangGraph, Robotics & IoT, VLSI, KCET Option Entry).
2. Explain the School Partner Bulk Registration process for classroom cohorts.
3. Provide schedules, speaker backgrounds, and verifiable e-certificate issuance guidelines.

Encourage collaborative learning and highlight that all outreach bootcamps are 100% free.
"""


def outreach_node(state: AgentState) -> Dict[str, Any]:
    """Pulls upcoming outreach masterclasses and formats registration instructions."""
    user_query = state["messages"][-1].content

    # Query active events and partner institutions
    events_sql = execute_college_sql.invoke(
        "SELECT event_id, title, track, speaker_name, event_date, event_time, platform, registration_fee "
        "FROM outreach_events;"
    )

    synthesis_prompt = f"""
    {OUTREACH_PROMPT}

    [ACTIVE MASTERCLASSES & WEBINARS]:
    {events_sql}

    [USER INQUIRY]:
    {user_query}
    """

    response = llm.invoke([SystemMessage(content=synthesis_prompt)])

    media: List[AgentActionMedia] = [
        {
            "title": "Generative AI & Agentic AI Masterclass Deck (PPTX)",
            "media_type": "PPTX",
            "url_or_path": "data/raw/presentations/COE_and_Department_Infrastructure.pptx",
            "description": "High Performance Computing & AI Labs Overview.",
        },
        {
            "title": "Live Masterclass Link & Event Brochure",
            "media_type": "ActionLink",
            "url_or_path": "https://meet.google.com/xyz-ai-masterclass",
            "description": "Instant 1-Click Meeting Access for Registered Batches.",
        },
    ]

    return {
        "messages": [AIMessage(content=response.content)],
        "suggested_media": media,
        "execution_status": "SUCCESS",
    }
