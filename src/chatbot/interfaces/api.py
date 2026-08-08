
from src.chatbot.agent.graph import agent_graph
from src.chatbot.interfaces.models import ChatRequest, ChatResponse
from src.chatbot.guardrails.guards import check_text, clean_text
from src.chatbot.infra.caching import get_cache, set_cache, normalize_and_hash_for_cache

from .router import api_router

from fastapi import HTTPException
from langsmith import traceable



@traceable()
@api_router.post("/api/chat", response_model=ChatResponse)
async def send_chat(body: ChatRequest):

    query = body.query
    print(query)
    thread_id = body.thread_id

    # CACHE GET

    hashed_query = normalize_and_hash_for_cache(query)

    if cached_response := get_cache(hashed_query):
        return ChatResponse(
            response=cached_response,
            thread_id=thread_id,
            cached=True,
            used_retrieval=False,
            retrieval_retries=0,
            tokens_used=0,
            llm_calls=0,
        )

    # INPUT GUARDRAILS

    clean_input: str = ""
    input_check = check_text("input", query)
    print(input_check)
    if input_check == "delete":
        raise HTTPException(400, "Your query was deleted automatically by our systems.")
    elif input_check == "clean":
        clean_input = clean_text("input", query)
    else:
        clean_input = query
    print("clean input: " + clean_input)

    # AGENT CALL
    print("before agent")
    output = await agent_graph.ainvoke({"user_query": clean_input})
    print(output)
    print("AFTER agent")

    # OUTPUT GUARDRAILS

    clean_output: str = ""
    output_check = check_text("output", output["response"])

    if output_check == "delete":
        raise HTTPException(400, "The bot's response was deleted automatically by our systems.")
    if output_check == "clean":
        clean_output = clean_text("output", output["response"])
    else:
        clean_output = output["response"]

    # CACHE SET
    set_cache(hashed_query, clean_output)

    return ChatResponse(
        response=clean_output,
        thread_id=thread_id,
        cached=False,
        used_retrieval=bool(output.get("retrieved")),
        retrieval_retries=output.get("retrieval_retries", 0),
        llm_calls=output.get("llm_calls", 0),
        tokens_used=output.get("tokens_used", 0),
    )