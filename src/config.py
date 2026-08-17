import os

KB_PATH = "data/knowledge_base"
CHROMA_PATH = "chroma_db"
KB_METADATA_FILE = "data/kb_metadata.json"
ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_FILE_SIZE_MB = 10

os.makedirs(KB_PATH, exist_ok=True)