"""
src/agents/tools.py

Tool execution interfaces for LangGraph agents.
Provides SQL execution against SQLite/PostgreSQL, ChromaDB hybrid vector retrieval,
ROI mathematical modeling, and DuckDuckGo fallback searches.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
import pandas as pd

from src.core.config import settings
from src.rag_engine.hybrid_search import HybridSearchEngine


@tool
def execute_college_sql(query: str) -> str:
    """Executes a SELECT query on the colleges, cutoffs, students, and departments database.
    Available tables:
      - colleges: (code, name, city, naac_grade, nirf_rank_2025, mgmt_fee_cse_lakhs, avg_package_lakhs)
      - cutoffs: (college_code, year, exam, branch, category, cutoff_rank, round_name)
      - students: (usn, full_name, college_code, branch, cgpa, hackathons_won, primary_skills, placement_status, offered_ctc_lpa)
      - departments: (college_code, branch_code, branch_name, hod_name, intake, funded_grants_lakhs)
    """
    clean_query = query.strip().replace("```sql", "").replace("```", "").strip()
    if not clean_query.upper().startswith("SELECT"):
        return "Security Guardrail: Only SELECT queries are permitted on the database."

    try:
        conn = sqlite3.connect(settings.DATABASE_URL.replace("sqlite:///", ""))
        df = pd.read_sql_query(clean_query, conn)
        conn.close()

        if df.empty:
            return "Query executed successfully, but returned 0 rows."
        return df.to_markdown(index=False)
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"


@tool
def query_vector_store_tool(
    query_text: str,
    filter_category: Optional[str] = None,
    top_k: int = 4,
) -> str:
    """Performs hybrid vector and keyword search across raw PDF brochures,
    NAAC SSRs, NBA compliance dossiers, and PPTX CoE facility slides.
    """
    try:
        hybrid_engine = HybridSearchEngine()
        filter_dict = {"doc_category": filter_category} if filter_category else None
        results = hybrid_engine.search(query=query_text, top_k=top_k, filter_dict=filter_dict)

        if not results:
            return "No matching regulatory or brochure records found."

        formatted_chunks = []
        for idx, doc in enumerate(results):
            src = doc.metadata.get("source", "Unknown Document")
            cat = doc.metadata.get("doc_category", "General")
            formatted_chunks.append(f"--- Document [{idx+1}] (Source: {src} | Category: {cat}) ---\n{doc.page_content}")

        return "\n\n".join(formatted_chunks)
    except Exception as e:
        return f"Vector Retrieval Error: {str(e)}"


@tool
def calculate_roi_tool(
    total_4yr_fee_lakhs: float,
    median_ctc_lpa: float,
    living_cost_per_year_lakhs: float = 1.5,
) -> str:
    """Calculates quantitative financial ROI, net earnings after 3 years,
    and payback period in months given total fee and placement compensation.
    """
    total_investment = total_4yr_fee_lakhs + (living_cost_per_year_lakhs * 4.0)
    monthly_take_home_approx = (median_ctc_lpa * 100000.0 * 0.82) / 12.0
    monthly_savings_potential = monthly_take_home_approx * 0.65

    payback_months = (
        (total_investment * 100000.0) / monthly_savings_potential
        if monthly_savings_potential > 0
        else 0
    )

    result = {
        "total_4yr_investment_lakhs": round(total_investment, 2),
        "median_ctc_lpa": median_ctc_lpa,
        "est_monthly_take_home_inr": round(monthly_take_home_approx, 0),
        "payback_period_months": round(payback_months, 1),
        "3_year_net_career_roi": round((median_ctc_lpa * 3.5) - total_investment, 2),
    }
    return json.dumps(result, indent=2)


@tool
def web_search_fallback(query_text: str) -> str:
    """Fallback search tool querying live web results via DuckDuckGo for public news."""
    try:
        search = DuckDuckGoSearchResults(num_results=3)
        return search.run(query_text)
    except Exception:
        return "Web search is currently unavailable. Utilizing internal institutional knowledge base."
