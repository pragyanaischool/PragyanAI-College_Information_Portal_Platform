"""
src/agents/state.py

LangGraph AgentState schema definition for PragyanAI College Intelligence Hub.
Maintains conversational messages, router tokens, tool execution contexts,
dynamic citation links (PDFs, PPTXs, YouTube URLs), and lead intent scoring.
"""

import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
from langchain_core.messages import BaseMessage


class AgentActionMedia(TypedDict):
    """Structured media asset returned for multimodal UI rendering."""
    title: str
    media_type: str  # PDF, Video, PPTX, Table, ActionLink
    url_or_path: str
    description: Optional[str]


class AgentState(TypedDict):
    """Central state container passed across all LangGraph nodes."""

    # Append-only conversation history reducer
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # Active routing decision token: ADMISSIONS | COMPLIANCE | OUTREACH | GENERAL_RAG
    current_route: str

    # Structured SQL context extracted during database queries
    sql_query: Optional[str]
    sql_result: Optional[str]

    # Vector store document passages and citation chunks
    retrieved_docs: List[Dict[str, Any]]

    # Media attachments (Admission Flyers, YouTube Walkthroughs, Regulatory PDFs)
    suggested_media: List[AgentActionMedia]

    # Prospective Parent/Student Lead scoring (1: Casual to 5: High-Intent Admission Escalation)
    lead_intent_score: int

    # Current user persona: Aspirant, School Counselor, Recruiter, Dean
    user_role: str

    # Operational status: SUCCESS | ERROR | ESCALATE_TO_CRM
    execution_status: str
