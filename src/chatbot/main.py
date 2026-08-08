from fastapi import FastAPI
from src.chatbot.interfaces.router import api_router
from src.chatbot.interfaces import api  # noqa: F401 — registers /api/chat routes
from src.chatbot.core import get_settings

settings = get_settings()
app = FastAPI(
    version=settings.VERSION,
    title="RAG Chatbot system, use /api/chat to chat with the RAG"
)

app.include_router(api_router)
