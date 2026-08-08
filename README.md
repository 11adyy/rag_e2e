# Agentic RAG System

This repository contains a complete, end-to-end Agentic Retrieval-Augmented Generation (RAG) system. The application is built using FastAPI and LangGraph, providing a robust chatbot capable of answering questions based on a knowledge base of documents. It features a self-correcting retrieval mechanism, input/output guardrails, and caching.

## Architecture

The core of the application is a stateful graph built with LangGraph. This graph defines the flow of logic for processing a user's query and generating a response.

The agent pipeline follows these steps:
1.  **Needs RAG Router**: First, the agent determines if the user's query requires accessing the knowledge base. Simple greetings or off-topic questions are handled directly by the generator model.
2.  **Query Generator**: If retrieval is necessary, this node generates multiple distinct search queries based on the user's input to explore different facets of the topic. It avoids using queries that have failed in previous attempts.
3.  **Retrieval**: The system performs a hybrid search using an `EnsembleRetriever` that combines dense (ChromaDB with OpenAI embeddings) and sparse (BM25) retrieval methods. The results are then passed to a reranker model (`qwen3-reranker-8b`) to select the most relevant documents.
4.  **Retrieval Evaluator**: After retrieval, the agent evaluates whether the retrieved documents are relevant to the user's query.
5.  **Conditional Routing**:
    *   If the documents are relevant, the process continues to the final response generation.
    *   If the documents are not relevant, the agent loops back to the **Query Generator** to create new queries. This retry loop is attempted up to three times.
    *   If the retry limit is reached, the agent proceeds to generation without context.
6.  **Generator**: The final response is generated using the retrieved context (if available). The model is instructed to ground its answers strictly in the provided documents and cite its sources.

### Technology Stack
-   **Web Framework**: FastAPI
-   **Agent & Orchestration**: LangChain & LangGraph
-   **Vector Store**: ChromaDB for dense retrieval
-   **Sparse Retrieval**: `rank-bm25`
-   **LLMs & Embeddings**: Fireworks.ai is used as the default provider for various models (generation, classification, reranking).
-   **Caching**: Redis is used to cache responses for repeated queries, reducing latency and cost.
-   **Containerization**: Docker and Docker Compose for easy deployment.

## Features

-   **Agentic RAG Pipeline**: A multi-step, stateful process for intelligent query handling.
-   **Self-Correction**: The agent can evaluate the quality of its retrieval and automatically retry with new queries if the results are unsatisfactory.
-   **Hybrid Search**: Combines dense and sparse retrieval techniques for more robust document matching.
-   **Response Reranking**: Improves the relevance of documents fed into the final generation step.
-   **Input/Output Guardrails**: Implements checks to detect and handle:
    -   Prompt injection attempts.
    -   PII (Personally Identifiable Information) and secrets, which are automatically redacted.
    -   Generation of dangerous or harmful content.
-   **Redis Caching**: Caches final responses to identical queries for instant results and reduced LLM usage.
-   **Asynchronous API**: Built with FastAPI for high performance.

## Getting Started

### Prerequisites
-   Python 3.14+
-   Docker and Docker Compose
-   `uv` Python package manager (`pip install uv`)

### 1. Clone the Repository

```bash
git clone https://github.com/11adyy/rag_e2e.git
cd rag_e2e
```

### 2. Configure Environment Variables

Create a `.env` file by copying the example file:
```bash
cp .env.example .env
```
Now, open the `.env` file and fill in the required values, especially your API key for the LLM provider. This project is configured for Fireworks.ai, but the variable is named `OPENAI_API_KEY` for compatibility.

```env
# Your Fireworks.ai API key
OPENAI_API_KEY=your_api_key_here

# The base URL for the Fireworks.ai API
BASE_URL=https://api.fireworks.ai/inference/v1/

# Other configurations can be left as default or customized
...
```

### 3. Install Dependencies

Install the required Python packages using `uv`.
```bash
uv sync
```

### 4. Ingest Data

The system is designed to work with a knowledge base. A script is provided to download and ingest a dataset of RAG-related academic papers from Hugging Face into the ChromaDB vector store.

Run the ingestion script:
```bash
uv run python -m src.chatbot.scripts.ingest_rag_dataset
```
This will download the data, process it into chunks, generate embeddings, and store them in the local ChromaDB instance located at `src/chatbot/chroma_db/`.

### 5. Run the Application

The easiest way to run the application and its dependencies (like Redis) is with Docker Compose.

```bash
docker-compose up --build
```
The API will be available at `http://127.0.0.1:8000`. You can access the OpenAPI documentation at `http://127.0.0.1:8000/docs`.

## Usage

You can interact with the chatbot by sending POST requests to the `/api/chat` endpoint.

**Request Body:**
-   `query` (str): The user's question.
-   `thread_id` (str): A unique identifier for the conversation thread.

**Example `curl` Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What is Retrieval Augmented Generation?",
  "thread_id": "your-unique-thread-id"
}'
```

**Example Response:**
```json
{
  "response": "Retrieval Augmented Generation (RAG) is a technique that combines a retrieval system with a large language model to generate more accurate and factual answers. It fetches relevant documents from a knowledge base to use as context for the response.",
  "thread_id": "your-unique-thread-id",
  "cached": false,
  "used_retrieval": true,
  "retrieval_retries": 1,
  "tokens_used": 1234,
  "llm_calls": 3
}
```

## Testing

The repository includes a suite of unit and integration tests. To run the tests, use `pytest`.

```bash
pytest
```

Some tests are marked and can be run selectively:
-   `@pytest.mark.llm`: These tests make live calls to the LLM API and require an `OPENAI_API_KEY` to be set in your `.env` file.
-   `@pytest.mark.live`: These tests are designed to run against a live, running instance of the application. You must set the `RUN_LIVE_TESTS=1` environment variable to execute them.

```bash
# Run only local unit tests
pytest -m "not llm and not live"

# Run tests that hit the LLM API
pytest -m llm
