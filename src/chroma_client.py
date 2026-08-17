import chromadb
from chromadb.utils import embedding_functions
from src.config import CHROMA_PATH

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = _client.get_or_create_collection(
    name="bi_knowledge_base",
    embedding_function=embedding_fn
)