from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_chroma import Chroma
from src.chatbot.core.config import get_settings
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from pathlib import Path
import shutil

settings = get_settings()

embeddings = OpenAIEmbeddings(
    model=settings.EMBEDDINGS_MODEL,
    base_url=settings.BASE_URL,
    max_retries=10,
    api_key=settings.OPENAI_API_KEY
)

db = Chroma(
    embedding_function=embeddings,
    persist_directory=settings.RAG_CHROMA_PERSIST_DIR,
    #collection_metadata={
        #"hnsw:space": settings.RAG_HNSW_M,
        #"hnsw:construction_ef": settings.RAG_HNSW_EF_CONSTRUCTION,
        #"hnsw:M": settings.RAG_HNSW_M,
        #"hnsw:search_ef": settings.RAG_HNSW_EF_SEARCH,
    #}
)

splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP
    )

def ingest_data_folder ():
    paths_to_check = {
        "TO_INDEX_PATH": settings.TO_INDEX_PATH,
        "INDEXED_PATH": settings.INDEXED_PATH
    }

    for name, path_str in paths_to_check.items():
        # Convertir a objeto Path
        path_obj = Path(path_str)

        # .resolve() te da el full path absoluto
        full_path = path_obj.resolve()

        if path_obj.exists():
            print(f"✅ {name} existe.")
            print(f"   Ruta absoluta: {full_path}")
        else:
            print(f"❌ {name} NO existe.")
            print(f"   Se esperaba en: {full_path}")

    dir_loader = DirectoryLoader(
        path=settings.TO_INDEX_PATH,
        loader_cls=UnstructuredFileLoader,
        recursive=True,
    )

    docs = dir_loader.load()
    shutil.move(settings.TO_INDEX_PATH, settings.INDEXED_PATH)
    splits = splitter.split_documents(docs)

    db.add_documents(
        splits,
        persist_directory=settings.RAG_CHROMA_PERSIST_DIR
    )

def ingest_docs(docs: list[Document]):
    print("lol")
    splits = splitter.split_documents(docs)
    print(len(splits))
    vectors = embeddings.embed_documents(
        [doc.page_content for doc in splits[:10]]
    )
    print("vector finished")
    batch_size = len(splits) // int(16)

    for i in range(int(16)):
        start = i * batch_size
        end = (i + 1) * batch_size if i < int(16) else len(splits)

        batch = splits[start:end]

        print(f"Batch {i + 1}/16: {len(batch)} documentos", flush=True)

        db.add_documents(batch)

    print("Terminado", flush=True)
    print("assfa")

if __name__ == "__main__":
    ingest_data_folder()