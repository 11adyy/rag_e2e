import pytest

from src.chatbot.agent.graph import AgentState, router_needs_rag


@pytest.mark.llm
@pytest.mark.parametrize(
    "user_query, expected",
    [
        # Obvious RAG questions → needs retrieval
        ("What is RAG (Retrieval Augmented Generation)?", True),
        ("Explain how retrieval augmented generation works.", True),
        ("¿Qué es RAG y cómo funciona el retrieval?", True),
        ("What components does the RAG system have?", True),
        # Obvious non-RAG questions → skip retrieval
        ("Hello, how are you today?", False),
        ("What is 2 + 2?", False),
        ("Tell me a joke about cats.", False),
    ],
)
def test_router_needs_rag_obvious_context(requires_api_key, user_query, expected):
    result = router_needs_rag(AgentState(user_query=user_query))
    assert result is expected
