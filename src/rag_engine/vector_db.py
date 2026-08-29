"""
src/rag_engine/vector_db.py

ChromaDB Persistent Vector Store interface for PragyanAI College Intelligence Hub.
Provides document upsertion, metadata-filtered similarity queries, and collection management.
"""

import os
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.core.config import settings
from src.rag_engine.embeddings import get_embedding_function
from src.rag_engine.ingestion import ingest_all_raw_documents


class ChromaVectorStore:
    """Persistent vector store manager backed by ChromaDB and SentenceTransformers."""

    def __init__(
        self,
        persist_directory: str = settings.CHROMA_PERSIST_DIRECTORY,
        collection_name: str = settings.CHROMA_COLLECTION_NAME,
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_fn = get_embedding_function()

        os.makedirs(self.persist_directory, exist_ok=True)
        self._init_vector_store()

    def _init_vector_store(self) -> None:
        """Initializes the Chroma persistent client and LangChain Chroma interface."""
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.vector_store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embedding_fn,
            persist_directory=self.persist_directory,
        )

    def add_documents(self, documents: List[Document]) -> None:
        """Adds a list of LangChain Document objects to the Chroma collection."""
        if not documents:
            return
        self.vector_store.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = settings.TOP_K_RETRIEVAL,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Executes a dense cosine similarity search with optional metadata filtering."""
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def similarity_search_with_score(
        self,
        query: str,
        k: int = settings.TOP_K_RETRIEVAL,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """Returns similarity search results accompanied by their cosine distance scores."""
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict,
        )

    def build_or_refresh_index(self) -> int:
        """Parses all raw files in data/raw/ and populates the persistent vector index."""
        docs = ingest_all_raw_documents()
        if docs:
            # Recreate collection to prevent duplicates
            try:
                self.client.delete_collection(name=self.collection_name)
            except Exception:
                pass
            self._init_vector_store()
            self.add_documents(docs)
        return len(docs)

    def count(self) -> int:
        """Returns the total number of indexed document chunks."""
        try:
            col = self.client.get_collection(name=self.collection_name)
            return col.count()
        except Exception:
            return 0
