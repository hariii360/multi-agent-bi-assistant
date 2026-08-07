import chromadb
from chromadb.utils import embedding_functions
import os
from pypdf import PdfReader

CHROMA_PATH = "chroma_db"
KB_PATH = "data/knowledge_base"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name="bi_knowledge_base",
    embedding_function=embedding_fn
)

def extract_text(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        reader = PdfReader(filepath)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def ingest_documents():
    files = [f for f in os.listdir(KB_PATH) if f.endswith((".txt", ".pdf"))]

    for filename in files:
        filepath = os.path.join(KB_PATH, filename)
        raw_text = extract_text(filepath)

        if not raw_text.strip():
            print(f"Skipped (no extractable text): {filename}")
            continue

        chunks = chunk_text(raw_text)
        ids = [f"{filename}::chunk_{i}" for i in range(len(chunks))]

        collection.upsert(documents=chunks, ids=ids)
        print(f"Ingested: {filename} ({len(chunks)} chunks)")

if __name__ == "__main__":
    ingest_documents()
    print(f"\nTotal chunks in collection: {collection.count()}")