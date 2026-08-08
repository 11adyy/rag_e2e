import pytest

from src.chatbot.agent.graph import agent_graph


@pytest.mark.llm
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        "What is RAG?",
        "Hello, how are you?",
    ],
)
async def test_graph_invoke_no_errors(requires_api_key, query):
    result = await agent_graph.ainvoke({"user_query": query})

    assert isinstance(result, dict)
    assert "response" in result
    assert isinstance(result["response"], str)
    assert len(result["response"]) > 0
    assert result["llm_calls"] >= 1


@pytest.mark.llm
@pytest.mark.asyncio
async def test_graph_rag_question_uses_retrieval(requires_api_key):
    result = await agent_graph.ainvoke(
        {"user_query": "What is Retrieval Augmented Generation (RAG)?"}
    )

    assert result["llm_calls"] >= 2
    assert isinstance(result["response"], str)
    assert len(result["response"]) > 20
