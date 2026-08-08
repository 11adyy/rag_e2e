from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str
    thread_id: str


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    cached: bool
    used_retrieval: bool
    retrieval_retries: int
    tokens_used: int
    llm_calls: int
