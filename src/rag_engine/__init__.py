"""
src/rag_engine/__init__.py

Multimodal Document Ingestion, Embeddings, Vector Database, and Hybrid Retrieval
package for PragyanAI College Intelligence Hub.
"""

from src.rag_engine.embeddings import EmbeddingEngine, get_embedding_function
from src.rag_engine.hybrid_search import HybridSearchEngine
from src.rag_engine.ingestion import (
    DocumentIngestionPipeline,
    extract_pdf_chunks,
    extract_pptx_chunks,
    ingest_all_raw_documents,
)
from src.rag_engine.vector_db import ChromaVectorStore
from src.rag_engine.youtube_loader import YouTubeMediaLoader

__all__ = [
    "EmbeddingEngine",
    "get_embedding_function",
    "extract_pdf_chunks",
    "extract_pptx_chunks",
    "ingest_all_raw_documents",
    "DocumentIngestionPipeline",
    "ChromaVectorStore",
    "YouTubeMediaLoader",
    "HybridSearchEngine",
]
