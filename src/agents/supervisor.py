"""
src/agents/supervisor.py

Supervisor routing node using Groq LLM.
Classifies user intent, computes prospective lead scores, and routes execution
to specialized sub-agents: ADMISSIONS | COMPLIANCE | OUTREACH | GENERAL_RAG.
"""

import logging
from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentState
from src.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq inference model with safe configuration fallbacks
llm = ChatGroq(
    model_name=getattr(settings, "GROQ_MODEL_NAME", "llama3-70b-8192"),
    groq_api_key=getattr(settings, "OPENAI_API_KEY", "your-api-key-here"),
    temperature=0.0,
)

SUPERVISOR_SYSTEM_PROMPT = """You are the Lead Intelligence Supervisor of the PragyanAI College Decision Hub.
Analyze the user's latest message and conversation history to:
1. Classify the user query into exactly ONE of the following routing tokens:
   - 'ADMISSIONS': For entrance exam cutoffs (KCET, COMEDK, JEE), management quota fees, rank predictions, scholarships, seat matrices, or placement ROI calculations.
   - 'COMPLIANCE': For NAAC accreditation, NBA Tier-1 OBE criteria, NIRF ranks, faculty Ph.D. density, research grants, patents, and statutory compliance.
   - 'OUTREACH': For school partner onboarding, free AI/ML bootcamps, robotics workshops, upcoming webinars, stream selector tests, or booking faculty 1-on-1 sessions.
   - 'GENERAL_RAG': For campus facility tours, student clubs, alumni networks, HOD messages, and general exploration.

2. Compute an 'Intent Score' (integer from 1 to 5):
   - 1: Casual exploration or general question.
   - 3: Academic interest in a specific branch or cutoff.
   - 5: High-intent admission query (asking about management fee payment, immediate seat booking, direct phone contact, or scholarship application).

Output your response strictly in the following format:
ROUTE: <TOKEN>
INTENT: <1-5>
"""


def supervisor_router_node(state: AgentState) -> Dict[str, Any]:
    """Evaluates the conversation context and routes to the appropriate worker node securely."""
    messages = state.get("messages", [])
    user_query = messages[-1].content if messages else ""

    try:
        response = llm.invoke(
            [
                SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
                HumanMessage(content=f"User Message: {user_query}"),
            ]
        )
        content = response.content.strip()

        # Parse token and intent score with high fault tolerance
        route = "GENERAL_RAG"
        intent = 1

        for line in content.split("\n"):
            upper_line = line.upper()
            if "ROUTE:" in upper_line:
                # Clean up potential markdown formatting like **ROUTE:** or backticks
                clean_line = upper_line.replace("*", "").replace("`", "")
                token = clean_line.split(":")[-1].strip()
                if token in ["ADMISSIONS", "COMPLIANCE", "OUTREACH", "GENERAL_RAG"]:
                    route = token
            elif "INTENT:" in upper_line:
                try:
                    clean_intent_line = upper_line.replace("*", "").replace("`", "")
                    intent = int(clean_intent_line.split(":")[-1].strip())
                    intent = max(1, min(5, intent))  # Clamp between 1 and 5
                except ValueError:
                    intent = 1

        return {
            "current_route": route,
            "lead_intent_score": intent,
            "execution_status": "ROUTED",
        }

    except Exception as e:
        logger.warning(f"Supervisor LLM routing failed, falling back to rule-based routing: {e}")
        query_lower = user_query.lower()
        
        if any(w in query_lower for w in ["cet", "comedk", "rank", "fee", "cutoff", "quota", "roi", "package", "admission", "seat"]):
            return {"current_route": "ADMISSIONS", "lead_intent_score": 3, "execution_status": "FALLBACK_ROUTED"}
        elif any(w in query_lower for w in ["nba", "naac", "accreditation", "nirf", "patent", "grant", "faculty", "citation"]):
            return {"current_route": "COMPLIANCE", "lead_intent_score": 2, "execution_status": "FALLBACK_ROUTED"}
        elif any(w in query_lower for w in ["webinar", "bootcamp", "school", "register", "event", "mou", "certificate"]):
            return {"current_route": "OUTREACH", "lead_intent_score": 3, "execution_status": "FALLBACK_ROUTED"}
        
        return {"current_route": "GENERAL_RAG", "lead_intent_score": 1, "execution_status": "FALLBACK_ROUTED"}
        
