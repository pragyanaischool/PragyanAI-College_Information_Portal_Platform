"""
src/agents/supervisor.py

Supervisor routing node using Groq LLM (Llama 3.3 70B Versatile).
Classifies user intent, computes prospective lead scores, and routes execution
to specialized sub-agents: ADMISSIONS | COMPLIANCE | OUTREACH | GENERAL_RAG.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentState
from src.core.config import settings

# Initialize Groq inference model
llm = ChatGroq(
    model_name=settings.GROQ_MODEL_NAME,
    groq_api_key=settings.GROQ_API_KEY,
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
    """Evaluates the conversation context and routes to the appropriate worker node."""
    messages = state["messages"]
    user_query = messages[-1].content if messages else ""

    try:
        response = llm.invoke(
            [
                SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
                HumanMessage(content=f"User Message: {user_query}"),
            ]
        )
        content = response.content.strip()

        # Parse token and intent score
        route = "GENERAL_RAG"
        intent = 1

        for line in content.split("\n"):
            if "ROUTE:" in line.upper():
                token = line.split(":")[-1].strip().upper()
                if token in ["ADMISSIONS", "COMPLIANCE", "OUTREACH", "GENERAL_RAG"]:
                    route = token
            elif "INTENT:" in line.upper():
                try:
                    intent = int(line.split(":")[-1].strip())
                except ValueError:
                    intent = 1

        return {
            "current_route": route,
            "lead_intent_score": intent,
            "execution_status": "ROUTED",
        }

    except Exception:
        # Fallback to rule-based routing if LLM call fails
        query_lower = user_query.lower()
        if any(w in query_lower for w in ["cet", "comedk", "rank", "fee", "cutoff", "quota", "roi", "package"]):
            return {"current_route": "ADMISSIONS", "lead_intent_score": 3, "execution_status": "FALLBACK_ROUTED"}
        elif any(w in query_lower for w in ["nba", "naac", "accreditation", "nirf", "patent", "grant"]):
            return {"current_route": "COMPLIANCE", "lead_intent_score": 2, "execution_status": "FALLBACK_ROUTED"}
        elif any(w in query_lower for w in ["webinar", "bootcamp", "school", "register", "event"]):
            return {"current_route": "OUTREACH", "lead_intent_score": 3, "execution_status": "FALLBACK_ROUTED"}
        return {"current_route": "GENERAL_RAG", "lead_intent_score": 1, "execution_status": "FALLBACK_ROUTED"}
