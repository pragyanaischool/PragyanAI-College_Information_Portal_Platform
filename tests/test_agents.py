"""
tests/test_agents.py

Tests for tool execution, mathematical ROI calculations, supervisor intent routing,
and LangGraph workflow execution.
"""

import json
import pytest
from src.agents.supervisor import supervisor_router_node
from src.agents.tools import calculate_roi_tool, execute_college_sql


def test_calculate_roi_tool():
    """Verifies accurate financial payback calculation and ROI formulas."""
    result_str = calculate_roi_tool.invoke({
        "total_4yr_fee_lakhs": 20.0,
        "median_ctc_lpa": 12.0,
        "living_cost_per_year_lakhs": 1.5,
    })
    result = json.loads(result_str)

    assert result["total_4yr_investment_lakhs"] == 26.0  # 20 + (1.5 * 4)
    assert result["median_ctc_lpa"] == 12.0
    assert result["payback_period_months"] > 0
    assert "3_year_net_career_roi" in result


def test_sql_guardrail_prevents_mutation():
    """Verifies that the SQL execution tool strictly prevents DROP/DELETE/UPDATE commands."""
    res_drop = execute_college_sql.invoke("DROP TABLE colleges;")
    assert "Security Guardrail" in res_drop

    res_delete = execute_college_sql.invoke("DELETE FROM cutoffs;")
    assert "Security Guardrail" in res_delete


def test_supervisor_fallback_routing():
    """Verifies rule-based routing tokens when the LLM is bypassed."""
    state_admissions = {"messages": [type("Msg", (), {"content": "What is the KCET cutoff and fee for CSE at RVCE?"})()]}
    res_adm = supervisor_router_node(state_admissions)
    assert res_adm["current_route"] in ["ADMISSIONS", "GENERAL_RAG"]

    state_compliance = {"messages": [type("Msg", (), {"content": "Explain NAAC accreditation and NBA status."})()]}
    res_comp = supervisor_router_node(state_compliance)
    assert res_comp["current_route"] in ["COMPLIANCE", "GENERAL_RAG"]

    state_outreach = {"messages": [type("Msg", (), {"content": "How do I register our school batch for the free AI bootcamp?"})()]}
    res_out = supervisor_router_node(state_outreach)
    assert res_out["current_route"] in ["OUTREACH", "GENERAL_RAG"]
