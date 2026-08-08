import pytest

from src.chatbot.agent.graph import AgentState, retrieval_evaluator


RAG_CONTEXT = [
    "RAG (Retrieval Augmented Generation) is a technique that combines "
    "information retrieval with large language model generation. "
    "The system retrieves relevant documents from a vector database "
    "and uses them as context to generate accurate, grounded answers."
]

IRRELEVANT_CONTEXT = [
    "The company offers private medical insurance to all employees. "
    "Coverage includes dental, vision, and general healthcare."
]


@pytest.mark.llm
@pytest.mark.parametrize(
    "user_query, retrieved, expected_relevant",
    [
        # Obvious match: RAG question + RAG docs
        ("What is RAG?", RAG_CONTEXT, True),
        (
            "How does retrieval augmented generation work?",
            RAG_CONTEXT,
            True,
        ),
        # Obvious mismatch: vacation policy question + unrelated docs
        (
            "What is the company vacation policy?",
            IRRELEVANT_CONTEXT,
            False,
        ),
        (
            "How many vacation days do employees get?",
            RAG_CONTEXT,
            False,
        ),
    ],
)
def test_retrieval_evaluator_obvious_context(
    requires_api_key, user_query, retrieved, expected_relevant
):
    state = AgentState(user_query=user_query, retrieved=retrieved)
    result = retrieval_evaluator(state)
    assert result.is_retrieval_relevant is expected_relevant
