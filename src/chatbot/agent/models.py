from typing import Annotated

from src.chatbot.core.config import get_settings

from pydantic import BaseModel, Field

settings = get_settings()

class LLMNeedsRagResponse ( BaseModel ):

    requires_retrieval: bool = Field(
        description="True if answering the user's query requires retrieving information "
        "from the RAG knowledge base. False if the query can be answered "
        "without consulting the RAG or can't be answered with the RAG."
    )

class LLMQueryGeneratorResponse( BaseModel ):

    queries: Annotated[list[str], Field(
        min_length=settings.AGENT_QUERY_GENERATION_NUMBER,
        max_length=settings.AGENT_QUERY_GENERATION_NUMBER,
        description="List of queries related to the user input"
    )]

class LLMRetrievalEvaluatorResponse ( BaseModel ):

    is_retrieval_relevant: bool = Field(
        description="True if the query can be answered with the retrieved information, False if not."
    )

# generation doesn't have