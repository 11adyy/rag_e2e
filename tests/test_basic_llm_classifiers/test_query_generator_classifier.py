import pytest

from src.chatbot.agent.graph import AgentState, query_generator
from src.chatbot.core.config import get_settings


@pytest.mark.llm
def test_query_generator_produces_english_rag_queries(requires_api_key):
    settings = get_settings()
    state = query_generator(
        AgentState(user_query="Explain how RAG retrieval and generation work together.")
    )

    assert len(state.rag_queries) == settings.AGENT_QUERY_GENERATION_NUMBER
    assert all(isinstance(q, str) and len(q.strip()) > 0 for q in state.rag_queries)

    combined = " ".join(state.rag_queries).lower()
    rag_keywords = ("rag", "retriev", "generat", "augment", "vector", "document")
    assert any(keyword in combined for keyword in rag_keywords)
