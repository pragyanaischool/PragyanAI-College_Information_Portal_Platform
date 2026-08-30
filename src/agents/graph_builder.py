"""
src/agents/graph_builder.py

Compiled LangGraph StateGraph Workflow for PragyanAI College Intelligence Hub.
Implements the Supervisor-Worker state machine with conditional branch routing
and fallback handling.
"""

import logging
from typing import Any, Dict, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph

from src.agents.admissions_agent import admissions_node
from src.agents.compliance_agent import compliance_node
from src.agents.outreach_agent import outreach_node
from src.agents.state import AgentActionMedia, AgentState
from src.agents.supervisor import supervisor_router_node
from src.agents.tools import query_vector_store_tool
from src.core.config import settings

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model_name=getattr(settings, "GROQ_MODEL_NAME", "llama3-70b-8192"),
    groq_api_key=getattr(settings, "OPENAI_API_KEY", "your-api-key-here"),
    temperature=0.1,
)


def general_rag_node(state: AgentState) -> Dict[str, Any]:
    """Fallback node handling general campus explorations and facility tours securely."""
    messages = state.get("messages", [])
    user_query = messages[-1].content if messages else "Tell me about the campus."
    
    docs_context = "General campus documents unavailable."
    try:
        docs_context = query_vector_store_tool.invoke({"query_text": user_query, "top_k": 2})
    except Exception as e:
        logger.warning(f"Vector retrieval failed in general_rag_node: {e}")

    general_prompt = f"""
    You are the Campus Experience Ambassador for PragyanAI College Hub.
    Answer the visitor's question using the context below:

    [CAMPUS CONTEXT]:
    {docs_context}

    [VISITOR QUERY]:
    {user_query}
    """
    
    try:
        response = llm.invoke([SystemMessage(content=general_prompt)])
        response_content = response.content
    except Exception as e:
        logger.error(f"LLM invocation failed in general_rag_node: {e}")
        response_content = f"Welcome to PragyanAI College Hub! I am currently unable to process your request due to a network error: {e}"

    media: list[AgentActionMedia] = [
        {
            "title": "Campus Labs & Facilities Virtual Tour",
            "media_type": "Video",
            "url_or_path": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "description": "360-degree walkthrough of innovation labs and campus maker spaces.",
        }
    ]

    return {
        "messages": [AIMessage(content=response_content)],
        "suggested_media": media,
        "execution_status": "SUCCESS",
    }


def build_college_agent_graph():
    """Builds and compiles the complete LangGraph multi-agent workflow."""
    workflow = StateGraph(AgentState)

    # 1. Add Workflow Nodes
    workflow.add_node("supervisor_node", supervisor_router_node)
    workflow.add_node("admissions_worker", admissions_node)
    workflow.add_node("compliance_worker", compliance_node)
    workflow.add_node("outreach_worker", outreach_node)
    workflow.add_node("general_rag_worker", general_rag_node)

    # 2. Set Workflow Entry Point
    workflow.set_entry_point("supervisor_node")

    # 3. Define Conditional Branching Edges from Supervisor
    def route_decision(state: AgentState) -> str:
        route = state.get("current_route", "GENERAL_RAG")
        if route == "ADMISSIONS":
            return "admissions_worker"
        elif route == "COMPLIANCE":
            return "compliance_worker"
        elif route == "OUTREACH":
            return "outreach_worker"
        return "general_rag_worker"

    workflow.add_conditional_edges(
        "supervisor_node",
        route_decision,
        {
            "admissions_worker": "admissions_worker",
            "compliance_worker": "compliance_worker",
            "outreach_worker": "outreach_worker",
            "general_rag_worker": "general_rag_worker",
        },
    )

    # 4. Leaf nodes route directly to END
    workflow.add_edge("admissions_worker", END)
    workflow.add_edge("compliance_worker", END)
    workflow.add_edge("outreach_worker", END)
    workflow.add_edge("general_rag_worker", END)

    return workflow.compile()


class CollegeAgentWorkflow:
    """Singleton execution wrapper for compiled LangGraph agent graph."""

    _compiled_graph = None

    @classmethod
    def get_graph(cls):
        if cls._compiled_graph is None:
            try:
                cls._compiled_graph = build_college_agent_graph()
            except Exception as e:
                logger.error(f"Failed to build college agent graph: {e}")
                cls._compiled_graph = None
        return cls._compiled_graph


def get_agent_response(
    user_input: str,
    user_role: str = "Student & Parent Aspirant",
    conversation_history: Optional[list] = None,
) -> Dict[str, Any]:
    """Helper method invoked by the Streamlit frontend to run the graph securely with fallbacks."""
    graph = CollegeAgentWorkflow.get_graph()

    messages = list(conversation_history) if conversation_history else []
    messages.append(HumanMessage(content=user_input))

    initial_state: AgentState = {
        "messages": messages,
        "current_route": "PENDING",
        "sql_query": None,
        "sql_result": None,
        "retrieved_docs": [],
        "suggested_media": [],
        "lead_intent_score": 1,
        "user_role": user_role,
        "execution_status": "INITIALIZED",
    }

    if not graph:
        # Graceful fallback if graph compilation fails
        return {
            "response_text": "I am operating in fallback mode. Please check your system configuration or database connectivity.",
            "route_taken": "FALLBACK",
            "lead_intent_score": 1,
            "suggested_media": [],
            "sql_query": None,
        }

    try:
        result_state = graph.invoke(initial_state)
        latest_message = result_state.get("messages", [AIMessage(content="No response generated.")])[-1].content

        return {
            "response_text": latest_message,
            "route_taken": result_state.get("current_route", "GENERAL_RAG"),
            "lead_intent_score": result_state.get("lead_intent_score", 1),
            "suggested_media": result_state.get("suggested_media", []),
            "sql_query": result_state.get("sql_query"),
        }
    except Exception as e:
        logger.error(f"Error invoking LangGraph workflow: {e}")
        return {
            "response_text": f"An error occurred while routing your query through the agent network: {e}",
            "route_taken": "ERROR_FALLBACK",
            "lead_intent_score": 1,
            "suggested_media": [],
            "sql_query": None,
        }
        
