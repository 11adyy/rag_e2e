from datasets import load_dataset
from langchain_core.documents import Document
from .ingest import ingest_docs
print(0)
ds = load_dataset("GXMZU/llm-rag-agent-papers")

documents = []
print(1)
for row in ds["rag"]:
    document = Document(
        page_content=row["content"],
        metadata={
            "id": row["id"],
            "paper_id": row["paper_id"],
            "title": row["title"].replace("\n", " "),
            "year": row["year"],
            "link": row["link"],
            "file_name": row["file_name"],
            "category": row["category"],
        }
    )
    print(2)
    documents.append(document)

print(3)

ingest_docs(documents)
print(4)