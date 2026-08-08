import uuid
import asyncio
import os

import pytest
import httpx


pytestmark = pytest.mark.live


def _live_server_available(url: str) -> bool:
    try:
        with httpx.Client(timeout=2.0) as client:
            client.get(f"{url}/docs")
        return True
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


@pytest.fixture(scope="module")
def live_server(live_server_url):
    if os.environ.get("RUN_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_TESTS=1 to run live server tests")
    if not _live_server_available(live_server_url):
        pytest.skip(f"Server not reachable at {live_server_url}")
    return live_server_url


async def chat_async(message, thread_id=None, client=None, base_url=None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    close_client = False
    if client is None:
        client = httpx.AsyncClient()
        close_client = True

    try:
        r = await client.post(
            f"{base_url}/api/chat",
            json={"query": message, "thread_id": thread_id},
            timeout=300,
        )
        assert r.status_code == 200
        data = r.json()
        assert "response" in data
        assert "thread_id" in data
        return data
    finally:
        if close_client:
            await client.aclose()


@pytest.mark.asyncio
async def test_known_questions(live_server):
    questions = [
        "¿Qué es RAG?",
        "Explícame Retrieval Augmented Generation.",
        "¿Cómo funciona el retrieval?",
        "¿Qué hace needs_rag?",
    ]

    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *[chat_async(q, client=client, base_url=live_server) for q in questions]
        )

    for r in responses:
        assert len(r["response"]) > 30


@pytest.mark.asyncio
async def test_unknown_information(live_server):
    questions = [
        "¿Cuál es el color favorito del creador?",
        "¿Cuál es el salario del CEO?",
        "¿Qué desayunó ayer el desarrollador?",
    ]

    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *[chat_async(q, client=client, base_url=live_server) for q in questions]
        )

    forbidden = ["según la documentación", "el documento indica"]
    for r in responses:
        text = r["response"].lower()
        for phrase in forbidden:
            assert phrase not in text


@pytest.mark.asyncio
async def test_languages(live_server):
    questions = [
        "What is RAG?",
        "Explain retrieval.",
        "Comment fonctionne RAG ?",
    ]

    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *[chat_async(q, client=client, base_url=live_server) for q in questions]
        )

    for r in responses:
        assert len(r["response"]) > 20


@pytest.mark.asyncio
async def test_special_characters(live_server):
    questions = [
        "¿Qué es RAG? 😊",
        "<script>alert(1)</script>",
        "' OR 1=1 --",
    ]

    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *[chat_async(q, client=client, base_url=live_server) for q in questions]
        )

    for r in responses:
        assert isinstance(r["response"], str)
