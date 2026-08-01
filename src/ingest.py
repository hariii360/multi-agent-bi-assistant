import chromadb
from chromadb.utils import embedding_functions
import os

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

def ingest_documents():
    files = [f for f in os.listdir(KB_PATH) if f.endswith(".txt")]

    for filename in files:
        filepath = os.path.join(KB_PATH, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        collection.upsert(
            documents=[content],
            ids=[filename]
        )
        print(f"Ingested: {filename}")

if __name__ == "__main__":
    ingest_documents()
    print(f"\nTotal documents in collection: {collection.count()}")