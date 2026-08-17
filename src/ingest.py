import os
from pypdf import PdfReader
from src.config import KB_PATH, ALLOWED_EXTENSIONS
from src.chroma_client import collection
from src.logger import logger


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
    files = [f for f in os.listdir(KB_PATH) if os.path.splitext(f)[1] in ALLOWED_EXTENSIONS]

    for filename in files:
        filepath = os.path.join(KB_PATH, filename)
        raw_text = extract_text(filepath)

        if not raw_text.strip():
            logger.warning(f"[Ingest] Skipped (no extractable text): {filename}")
            continue

        chunks = chunk_text(raw_text)
        ids = [f"{filename}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]

        collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
        logger.info(f"[Ingest] Ingested: {filename} ({len(chunks)} chunks)")

    logger.info(f"[Ingest] Total chunks in collection: {collection.count()}")


if __name__ == "__main__":
    ingest_documents()