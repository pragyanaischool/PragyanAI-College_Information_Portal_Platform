"""
src/agents/admissions_agent.py

Admissions & Placement ROI Worker Agent.
Synthesizes SQL queries across Cutoff/Fee tables, pulls admission brochures,
and generates structured admission feasibility recommendations.
"""

import logging
from typing import Any, Dict, List
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentActionMedia, AgentState
from src.agents.tools import execute_college_sql, query_vector_store_tool
from src.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq Chat Client
llm = ChatGroq(
    model_name=getattr(settings, "GROQ_MODEL_NAME", "llama3-70b-8192"),
    groq_api_key=settings.OPENAI_API_KEY,  # or settings.GROQ_API_KEY depending on setup
    temperature=0.1,
)

ADMISSIONS_PROMPT = """You are the Admissions and Financial ROI Lead at PragyanAI College Intelligence Hub.
Your task is to provide transparent, accurate, and data-backed guidance regarding:
1. KCET, COMEDK, and JEE cutoffs across branches and quota categories.
2. Government Tuition vs COMEDK vs Management Quota Fee structures.
3. Salary benchmarks (Median, Average, Highest CTC) and ROI payback timelines.

Follow these execution rules:
- Directly cite verified numbers from the provided Database / Document Context.
- Structure responses with markdown tables and bullet points for instant readability.
- If a candidate is on the borderline of a merit rank, explain institutional management seat options.
"""


def admissions_node(state: AgentState) -> Dict[str, Any]:
    """Generates SQL queries, retrieves brochure data, and synthesizes answers securely."""
    messages = state.get("messages", [])
    if not messages:
        return {
            "messages": [AIMessage(content="Hello! How can I assist you with admissions, cutoffs, or fee structures today?")],
            "execution_status": "ERROR",
        }

    user_query = messages[-1].content

    # Step 1: Generate SQL query safely
    sql_query = ""
    db_context = "Database context unavailable."
    try:
        sql_gen_prompt = (
            "Generate a SQLite SELECT query using tables 'colleges', 'cutoffs', 'students' to answer: "
            f"'{user_query}'. Return ONLY the raw SQL query without markdown formatting fences like ```sql."
        )
        raw_sql = llm.invoke(sql_gen_prompt).content.strip()
        # Clean markdown formatting if present
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
        
        if sql_query.lower().startswith("select"):
            db_context = execute_college_sql.invoke(sql_query)
        else:
            sql_query = "SELECT name, city, nirf_rank_2025, median_ctc_lpa FROM colleges LIMIT 5;"
            db_context = execute_college_sql.invoke(sql_query)
    except Exception as e:
        logger.warning(f"SQL generation or execution failed: {e}")
        db_context = f"Fallback database notice: Unable to execute dynamic query ({e})."

    # Step 2: Retrieve Admission Brochure Chunks safely
    brochure_context = "No specific brochure chunks retrieved."
    try:
        brochure_context = query_vector_store_tool.invoke({
            "query_text": user_query,
            "filter_category": "Admissions & Fees",
            "top_k": 2,
        })
    except Exception as e:
        logger.warning(f"Vector store query failed: {e}")

    # Step 3: Synthesize Final Expert Response
    synthesis_prompt = f"""
    {ADMISSIONS_PROMPT}

    [DATABASE SQL CONTEXT]:
    Query Executed: {sql_query}
    Results:
    {db_context}

    [OFFICIAL BROCHURE CONTEXT]:
    {brochure_context}

    [USER INQUIRY]:
    {user_query}
    """

    try:
        response = llm.invoke([SystemMessage(content=synthesis_prompt)])
        response_content = response.content
    except Exception as e:
        logger.error(f"LLM synthesis failed: {e}")
        response_content = f"I retrieved the relevant data for your query, but encountered an error synthesizing the final report: {e}"

    # Media attachments for Admissions Desk
    media: List[AgentActionMedia] = [
        {
            "title": "Management Quota Fee & Scholarship Flyer (PDF)",
            "media_type": "PDF",
            "url_or_path": "data/raw/brochures/Admission_Flyer_2026.pdf",
            "description": "Official 2026-27 Fee Bifurcation, Merit Waivers & Seat Matrix.",
        },
        {
            "title": "4-Year Salary & ROI Payback Report (PDF)",
            "media_type": "PDF",
            "url_or_path": "data/raw/brochures/Placement_ROI_Report_2026.pdf",
            "description": "Comparative Placement Packages & Financial Breakeven Curves.",
        },
    ]

    return {
        "messages": [AIMessage(content=response_content)],
        "sql_query": sql_query,
        "sql_result": db_context,
        "suggested_media": media,
        "execution_status": "SUCCESS",
    }
    
