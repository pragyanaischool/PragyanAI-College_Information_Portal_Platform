"""
src/agents/admissions_agent.py

Admissions & Placement ROI Worker Agent.
Synthesizes SQL queries across Cutoff/Fee tables, pulls admission brochures,
and generates structured admission feasibility recommendations.
"""

from typing import Any, Dict, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentActionMedia, AgentState
from src.agents.tools import calculate_roi_tool, execute_college_sql, query_vector_store_tool
from src.core.config import settings

llm = ChatGroq(
    model_name=settings.GROQ_MODEL_NAME,
    groq_api_key=settings.GROQ_API_KEY,
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
    """Generates SQL queries, retrieves brochure data, and synthesizes answers."""
    user_query = state["messages"][-1].content

    # Step 1: Generate SQL query based on user question
    sql_gen_prompt = (
        "Generate a SQLite query for tables 'colleges', 'cutoffs', 'students' to answer: "
        f"'{user_query}'. Return ONLY the raw SQL query without quotes, explanation, or markdown fences."
    )
    sql_query = llm.invoke(sql_gen_prompt).content.strip().replace("```sql", "").replace("```", "")
    db_context = execute_college_sql.invoke(sql_query)

    # Step 2: Retrieve Admission Brochure Chunks
    brochure_context = query_vector_store_tool.invoke({
        "query_text": user_query,
        "filter_category": "Admissions & Fees",
        "top_k": 2,
    })

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

    response = llm.invoke([SystemMessage(content=synthesis_prompt)])

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
        "messages": [AIMessage(content=response.content)],
        "sql_query": sql_query,
        "sql_result": db_context,
        "suggested_media": media,
        "execution_status": "SUCCESS",
    }
