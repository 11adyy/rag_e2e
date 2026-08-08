"""
Main graph of the agentic RAG pipeline.

Invoke with:
    agent_graph.invoke({"user_query": "<your query>"})

Pipeline:
    1. Decide whether retrieval is required.
    2. Generate retrieval queries if needed.
    3. Retrieve documents from the vector database.
    4. Evaluate whether the retrieved documents are relevant.
    5. Retry retrieval if necessary.
    6. Generate the final response using the retrieved context when available.
"""

#-------------------- IMPORTS
# Python imports

from typing import Literal

# Internal imports

from src.chatbot.retrieval import retrieve
from src.chatbot.core.config import get_settings

from .prompts import needs_rag_prompt, query_generator_prompt, retrieval_evaluator_prompt, generator_prompt
from .models import LLMNeedsRagResponse, LLMRetrievalEvaluatorResponse, LLMQueryGeneratorResponse

# Lib imports

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

#-------------------- GLOBAL

settings = get_settings()

#-------------------- AGENT STATE MODEL

class AgentState( BaseModel ):
    """Shared state passed between graph nodes.

    Attributes:
        user_query: Original user query.
        rag_queries: Queries generated for document retrieval.
        retrieved: Retrieved documents.
        is_retrieval_relevant: Whether the retrieved documents are relevant.
        used_queries: Previously unsuccessful retrieval queries.
        retrieval_retries: Number of retrieval attempts.
        llm_calls: Total number of LLM invocations.
        response: Final generated response.
    """

    user_query : str

    rag_queries: list[str] = Field(default_factory=list)
    retrieved: list = Field(default_factory=list)
    is_retrieval_relevant: bool = False
    used_queries: list[str] = Field(default_factory=list)

    retrieval_retries: int = 0
    llm_calls: int = 0
    tokens_used: int = 0
    response: str = ""

#-------------------- GRAPH NODES

def router_needs_rag (state : AgentState) -> bool:
    """
    Determine whether the user's query requires document retrieval.

    Args:
        state: Current graph state.
    Returns:
        True if retrieval is required, otherwise False.
    """
    user_query = state.user_query

    llm = ChatOpenAI(model=settings.AGENT_NEEDS_RAG_MODEL, base_url=settings.BASE_URL, api_key=settings.OPENAI_API_KEY, max_retries=10)
    llm_structured = llm.with_structured_output(LLMNeedsRagResponse, include_raw=True)

    classifier_chain = needs_rag_prompt | llm_structured
    response = classifier_chain.invoke(input={"user_query": user_query})

    state.llm_calls += 1

    state.tokens_used += response["raw"].usage_metadata.get("total_tokens", 0)

    return response["parsed"].requires_retrieval


def query_generator (state: AgentState) -> AgentState:
    """
    Generate retrieval queries from the user's request.

    Args:
        state: Current graph state.
    Returns:
        Updated state containing the generated retrieval queries.
    """

    user_query = state.user_query
    llm = ChatOpenAI(model=settings.AGENT_QUERY_GENERATOR_MODEL, base_url=settings.BASE_URL, api_key=settings.OPENAI_API_KEY, max_retries=10)

    llm_structured = llm.with_structured_output(LLMQueryGeneratorResponse, include_raw=True)

    classifier_chain = query_generator_prompt | llm_structured
    response = classifier_chain.invoke(
        input={
        "user_query": user_query,
        "used_queries": state.used_queries,
        "query_number": settings.AGENT_QUERY_GENERATION_NUMBER
        },
    )
    state.tokens_used += response["raw"].usage_metadata.get("total_tokens", 0)
    state.llm_calls += 1
    state.rag_queries = response["parsed"].queries

    return state

def retrieval(state: AgentState) -> AgentState:
    """
    Retrieve documents for each generated query.

    Args:
        state: Current graph state.
    Returns:
        Updated state containing the retrieved documents.
    """
    state.retrieved = []
    for query in state.rag_queries:
        state.retrieved.extend(retrieve(query, top_k=settings.AGENT_TOP_K))
    state.retrieval_retries += 1
    return state

def retrieval_evaluator(state: AgentState) -> AgentState:
    """
    Evaluate whether the retrieved documents answer the user's query.

    Args:
        state: Current graph state.
    Returns:
        Updated state containing the evaluation result.
    """

    user_query = state.user_query
    llm = ChatOpenAI(model=settings.AGENT_RETRIEVAL_EVALUATOR_MODEL, base_url=settings.BASE_URL, api_key=settings.OPENAI_API_KEY, max_retries=10)
    llm_structured = llm.with_structured_output(LLMRetrievalEvaluatorResponse, include_raw=True)

    chain = retrieval_evaluator_prompt | llm_structured

    response = chain.invoke(input={"user_query": user_query, "retrieved": state.retrieved})

    state.tokens_used += response["raw"].usage_metadata.get("total_tokens", 0)
    state.llm_calls += 1
    state.is_retrieval_relevant = response["parsed"].is_retrieval_relevant

    if not state.is_retrieval_relevant:
        state.used_queries = state.rag_queries
        state.rag_queries = []

    return state

def router_after_retrieval_evaluator (state: AgentState) -> Literal["generate", "retry"]:
    """
    Choose the next step after retrieval evaluation.

    Args:
        state: Current graph state.

    Returns:
        "generate" if the retrieved documents are relevant or the retry limit
        has been reached, otherwise "retry".
    """

    if state.retrieval_retries >= 3 or state.is_retrieval_relevant:
        return "generate"

    return "retry"

def generator (state: AgentState) -> AgentState:
    """
    Generate the final response.
    Uses the retrieved documents as context when available; otherwise,
    generates the response without additional context.

    Args:
        state: Current graph state.
    Returns:
        Updated state containing the generated response.
    """

    user_query = state.user_query
    llm = ChatOpenAI(model=settings.AGENT_GENERATOR_MODEL, base_url=settings.BASE_URL, api_key=settings.OPENAI_API_KEY, max_retries=10)

    chain = generator_prompt | llm
    response = chain.invoke(
        input={
            "user_query": user_query,
            "retrieved": state.retrieved,
        })

    state.tokens_used += response.usage_metadata.get("total_tokens", 0)
    state.llm_calls += 1
    state.response = response.content

    return state

#-------------------- GRAPH BUILD

graph = StateGraph(AgentState)


graph.add_node("query_generator", query_generator)
graph.add_node("retrieval", retrieval)
graph.add_node("retrieval_evaluator", retrieval_evaluator)
graph.add_node("generator", generator)

graph.add_conditional_edges(
    START,
    router_needs_rag,
    {
        True: "query_generator",
        False: "generator"
    }
)

graph.add_edge("query_generator", "retrieval")
graph.add_edge("retrieval", "retrieval_evaluator")

graph.add_conditional_edges(
    "retrieval_evaluator",
    router_after_retrieval_evaluator,
    {
        "generate": "generator",
        "retry": "query_generator"
    }
)

graph.add_edge("generator", END)

#-------------------- GRAPH COMPILING

agent_graph = graph.compile()



