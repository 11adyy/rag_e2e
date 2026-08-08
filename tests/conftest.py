import os
from unittest.mock import patch

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "llm: tests that call real LLM APIs")
    config.addinivalue_line("markers", "live: tests that require a running server")


@pytest.fixture
def mock_redis():
    """Avoid Redis connection errors in API integration tests."""
    with patch("src.chatbot.infra.caching.r") as mock_r:
        mock_r.get.return_value = None
        mock_r.set.return_value = True
        yield mock_r


@pytest.fixture
def requires_api_key():
    from src.chatbot.core.config import get_settings

    if not get_settings().OPENAI_API_KEY:
        pytest.skip("OPENAI_API_KEY not set")


@pytest.fixture
def live_server_url():
    url = os.environ.get("LIVE_SERVER_URL", "http://127.0.0.1:8000")
    return url.rstrip("/")
