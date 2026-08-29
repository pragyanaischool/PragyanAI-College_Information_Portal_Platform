"""
src/agents/compliance_agent.py

Accreditation, NAAC SSR & NBA Outcome-Based Education Compliance Agent.
Retrieves criterion-level audits, faculty Ph.D. cadre ratios, and funded research grants.
"""

from typing import Any, Dict, List
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq

from src.agents.state import AgentActionMedia, AgentState
from src.agents.tools import execute_college_sql, query_vector_store_tool
from src.core.config import settings

llm = ChatGroq(
    model_name=settings.GROQ_MODEL_NAME,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0.1,
)

COMPLIANCE_PROMPT = """You are the Chief Accreditation & Academic Compliance Officer for the PragyanAI Portal.
Your task is to analyze and present institutional regulatory metrics:
1. NAAC Self-Study Report (SSR) Criterion 1-7 scores and CGPA grades.
2. NBA Tier-1 Washington Accord attainment (PEOs, PO1-PO12 outcomes).
3. NIRF Ranking parameters (TLR, RPC, GO, OI, PR).
4. Faculty Cadre Proportion (Prof:Assoc:Asst = 1:2:6), Ph.D. density, and sponsored research grants (DST, AICTE, DRDO).

Always provide factual, audit-ready data accompanied by regulatory document citations.
"""


def compliance_node(state: AgentState) -> Dict[str, Any]:
    """Handles regulatory and accreditation queries using vector store and SQL metrics."""
    user_query = state["messages"][-1].content

    # Retrieve NAAC & NBA Document Chunks
    regulatory_context = query_vector_store_tool.invoke({
        "query_text": user_query,
        "filter_category": None,  # Pull across NBA & NAAC
        "top_k": 3,
    })

    # Pull Faculty & Department grants context from SQL
    sql_context = execute_college_sql.invoke(
        "SELECT c.name, c.naac_grade, c.naac_cgpa, c.nirf_rank_2025, "
        "d.branch_code, d.nba_status, d.funded_grants_lakhs, d.patents_filed "
        "FROM colleges c JOIN departments d ON c.code = d.college_code LIMIT 10;"
    )

    synthesis_prompt = f"""
    {COMPLIANCE_PROMPT}

    [REGULATORY AUDIT CONTEXT]:
    {regulatory_context}

    [INSTITUTIONAL METRICS]:
    {sql_context}

    [USER INQUIRY]:
    {user_query}
    """

    response = llm.invoke([SystemMessage(content=synthesis_prompt)])

    media: List[AgentActionMedia] = [
        {
            "title": "NAAC Self-Study Report (SSR) Executive Audit",
            "media_type": "PDF",
            "url_or_path": "data/raw/regulatory/NAAC_Self_Study_Summary.pdf",
            "description": "Criterion 1-7 quantitative evaluation and academic flexibility scores.",
        },
        {
            "title": "NBA Tier-1 Outcome-Based Education Compliance SAR",
            "media_type": "PDF",
            "url_or_path": "data/raw/regulatory/NBA_Criteria_Compliance_Report.pdf",
            "description": "PO1-PO12 attainment thresholds and faculty cadre proportion metrics.",
        },
    ]

    return {
        "messages": [AIMessage(content=response.content)],
        "suggested_media": media,
        "execution_status": "SUCCESS",
    }
