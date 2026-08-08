import pytest

from src.chatbot.agent.graph import AgentState, router_after_retrieval_evaluator


@pytest.mark.parametrize(
    "state, expected",
    [
        # Relevant docs → generate immediately
        (
            AgentState(
                user_query="What is RAG?",
                retrieved=["RAG stands for Retrieval Augmented Generation."],
                is_retrieval_relevant=True,
                retrieval_retries=1,
            ),
            "generate",
        ),
        # Irrelevant docs but max retries reached → generate anyway
        (
            AgentState(
                user_query="What is RAG?",
                retrieved=["Unrelated content about cooking."],
                is_retrieval_relevant=False,
                retrieval_retries=3,
            ),
            "generate",
        ),
        # Irrelevant docs, retries remaining → retry
        (
            AgentState(
                user_query="What is RAG?",
                retrieved=["Unrelated content about cooking."],
                is_retrieval_relevant=False,
                retrieval_retries=1,
            ),
            "retry",
        ),
        # First attempt failed → retry
        (
            AgentState(
                user_query="What is the vacation policy?",
                rag_queries=["vacation days employees"],
                retrieved=["Information about medical insurance benefits."],
                is_retrieval_relevant=False,
                used_queries=["employee benefits"],
                retrieval_retries=1,
            ),
            "retry",
        ),
    ],
)
def test_router_after_retrieval_evaluator(state, expected):
    assert router_after_retrieval_evaluator(state) == expected
