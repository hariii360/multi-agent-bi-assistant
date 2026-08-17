import os
import json
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from src.config import KB_PATH, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, KB_METADATA_FILE
from src.ingest import ingest_documents
from src.chroma_client import collection
from src.logger import logger

router = APIRouter(prefix="/kb", tags=["knowledge_base"])

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class KBFile(BaseModel):
    filename: str
    size_kb: float


class KBStatus(BaseModel):
    total_files: int
    total_chunks: int
    last_ingested: str | None


def safe_filename(filename: str) -> str:
    """Strip any path components and reject traversal attempts."""
    clean_name = os.path.basename(filename)
    if clean_name != filename or clean_name in ("", ".", ".."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return clean_name


def read_last_ingested() -> str | None:
    if not os.path.exists(KB_METADATA_FILE):
        return None
    with open(KB_METADATA_FILE, "r") as f:
        return json.load(f).get("last_ingested")


def write_last_ingested():
    os.makedirs(os.path.dirname(KB_METADATA_FILE), exist_ok=True)
    with open(KB_METADATA_FILE, "w") as f:
        json.dump({"last_ingested": datetime.now(timezone.utc).isoformat()}, f)


@router.get("/list", response_model=list[KBFile])
def list_files():
    files = []
    for f in os.listdir(KB_PATH):
        path = os.path.join(KB_PATH, f)
        if os.path.isfile(path) and os.path.splitext(f)[1] in ALLOWED_EXTENSIONS:
            files.append(KBFile(filename=f, size_kb=round(os.path.getsize(path) / 1024, 2)))
    return files


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = safe_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"[KB] Rejected upload with invalid extension: {filename}")
        raise HTTPException(status_code=400, detail=f"Only {ALLOWED_EXTENSIONS} files are allowed")

    dest_path = os.path.join(KB_PATH, filename)

    size = 0
    with open(dest_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE_BYTES:
                buffer.close()
                os.remove(dest_path)
                logger.warning(f"[KB] Rejected upload exceeding size limit: {filename}")
                raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
            buffer.write(chunk)

    logger.info(f"[KB] Uploaded file: {filename} ({round(size/1024, 1)} KB)")

    # Auto-ingest so the file is searchable immediately
    ingest_documents()
    write_last_ingested()

    return {"filename": filename, "status": "uploaded_and_ingested", "total_chunks": collection.count()}


@router.delete("/{filename}")
def delete_file(filename: str):
    filename = safe_filename(filename)
    file_path = os.path.join(KB_PATH, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

    os.remove(file_path)

    # Clean up this file's chunks from ChromaDB so retrieval doesn't return stale data
    collection.delete(where={"source": filename})

    logger.info(f"[KB] Deleted file and its ChromaDB chunks: {filename}")
    return {"filename": filename, "status": "deleted", "total_chunks": collection.count()}


@router.post("/ingest")
def trigger_ingest():
    try:
        ingest_documents()
        write_last_ingested()
    except Exception as e:
        logger.error(f"[KB] Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

    return {"status": "ingested", "total_chunks": collection.count()}


@router.get("/status", response_model=KBStatus)
def kb_status():
    files = [f for f in os.listdir(KB_PATH) if os.path.splitext(f)[1] in ALLOWED_EXTENSIONS]
    return KBStatus(
        total_files=len(files),
        total_chunks=collection.count(),
        last_ingested=read_last_ingested()
    )