"""
src/rag_engine/embeddings.py

SentenceTransformers and HuggingFace Embeddings wrapper for PragyanAI College Intelligence Hub.
Provides persistent, local vector embedding computations with batching support.
"""

from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

from src.core.config import settings


class EmbeddingEngine:
    """Singleton wrapper for managing Dense Vector Embeddings."""

    _instance = None
    _langchain_embeddings = None
    _raw_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance

    def _initialize_models(self) -> None:
        """Loads the sentence-transformers model into CPU/GPU memory."""
        model_name = settings.EMBEDDING_MODEL_NAME
        # Initialize LangChain compatible wrapper
        self._langchain_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        # Initialize raw SentenceTransformer instance for direct numpy queries
        self._raw_model = SentenceTransformer(model_name)

    @property
    def langchain_client(self) -> HuggingFaceEmbeddings:
        """Returns the LangChain-compatible embedding instance."""
        return self._langchain_embeddings

    def embed_query(self, text: str) -> List[float]:
        """Generates a normalized embedding vector for a search query string."""
        return self._langchain_embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates a batch of embedding vectors for document chunks."""
        return self._langchain_embeddings.embed_documents(texts)


def get_embedding_function() -> HuggingFaceEmbeddings:
    """Helper factory returning the application's LangChain embeddings client."""
    return EmbeddingEngine().langchain_client
