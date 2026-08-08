import time
import requests
from src.chatbot.core.config import get_settings

settings = get_settings()


def rerank(
    query: str,
    docs: list,
    top_n: int = 5,
    retries: int = 3,
):

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                "https://api.fireworks.ai/inference/v1/rerank",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.RERANKER_MODEL,
                    "query": query,
                    "documents": [doc.page_content for doc in docs],
                    "top_n": top_n,
                    "return_documents": False,
                },
                timeout=30,
            )
            response.raise_for_status()

            return [
                docs[item["index"]]
                for item in response.json()["data"]
            ]

        except requests.RequestException as error:
            should_stop = (
                attempt == retries
                or (
                    error.response is not None
                    and error.response.status_code < 500
                    and error.response.status_code != 429
                )
            )

            if should_stop:
                raise

            time.sleep(2 ** attempt)

    raise RuntimeError("Reranking failed after all retries")