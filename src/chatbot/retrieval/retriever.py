
from src.chatbot.core.config import get_settings
from src.chatbot.retrieval.reranker import rerank

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_chroma import Chroma

settings = get_settings()

embeddings = OpenAIEmbeddings(
    model=settings.EMBEDDINGS_MODEL,
    base_url=settings.BASE_URL,
    max_retries=10,
    api_key=settings.OPENAI_API_KEY
)

db = Chroma(
    persist_directory=settings.RAG_CHROMA_PERSIST_DIR,
    embedding_function=embeddings,
)
all_docs = []
docs = []

BATCH_SIZE = 1000

for offset in range(0, db._collection.count(), BATCH_SIZE):
    data = db.get(
        include=["documents", "metadatas"],
        limit=BATCH_SIZE,
        offset=offset,
    )

    batch_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(data["documents"], data["metadatas"])
    ]

    all_docs.extend(batch_docs)

dense_retriever = db.as_retriever(search_kwargs={"k": settings.RAG_TOP_K})
sparse_retriever = BM25Retriever.from_documents(all_docs) if all_docs else None


ensembled_retriever = EnsembleRetriever(
    retrievers=[dense_retriever,sparse_retriever] if sparse_retriever else [dense_retriever],
    weights=[settings.DENSE_RETRIEVER_WEIGHT, settings.SPARSE_RETRIEVER_WEIGHT]
    )

def retrieve (query: str, top_k: int = settings.RAG_TOP_K) -> list[str]:

    retrieved_docs = ensembled_retriever.invoke(input=query)

    reranked_docs = rerank(query=query, docs=retrieved_docs, top_n=settings.RAG_TOP_N)

    return reranked_docs

