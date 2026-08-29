"""
src/rag_engine/hybrid_search.py

Hybrid Search Fusion Engine combining Dense Vector Cosine Similarity (ChromaDB)
with Sparse BM25 Keyword Search using Reciprocal Rank Fusion (RRF).
"""

import math
import re
from typing import Any, Dict, List, Optional
from langchain_core.documents import Document

from src.core.config import settings
from src.rag_engine.vector_db import ChromaVectorStore


class SimpleBM25:
    """Lightweight in-memory BM25 ranker for exact keyword and term matching."""

    def __init__(self, corpus: List[Document], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_len = [len(self._tokenize(doc.page_content)) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 1.0
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self._initialize()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def _initialize(self) -> None:
        n_docs = len(self.corpus)
        for doc in self.corpus:
            tokens = set(self._tokenize(doc.page_content))
            for token in tokens:
                self.df[token] = self.df.get(token, 0) + 1

        for token, freq in self.df.items():
            self.idf[token] = math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    def get_top_n(self, query: str, n: int = 5) -> List[Document]:
        """Calculates BM25 relevance scores for all documents given a query string."""
        tokens = self._tokenize(query)
        scores = []

        for idx, doc in enumerate(self.corpus):
            score = 0.0
            doc_tokens = self._tokenize(doc.page_content)
            doc_len = self.doc_len[idx]

            for token in tokens:
                if token in self.idf:
                    tf = doc_tokens.count(token)
                    numerator = self.idf[token] * tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                    score += numerator / (denominator + 1e-6)

            scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scores[:n] if score > 0.0]


class HybridSearchEngine:
    """Combines dense semantic vector retrieval with sparse BM25 keyword matching."""

    def __init__(self, vector_store: Optional[ChromaVectorStore] = None):
        self.vector_store = vector_store or ChromaVectorStore()
        self.bm25_index: Optional[SimpleBM25] = None
        self._build_bm25_index()

    def _build_bm25_index(self) -> None:
        """Pulls all indexed documents to build the in-memory BM25 keyword cache."""
        try:
            # Query broad vector search to pull documents for BM25 indexing
            results = self.vector_store.similarity_search("engineering college admissions", k=300)
            if results:
                self.bm25_index = SimpleBM25(results)
        except Exception:
            self.bm25_index = None

    def search(
        self,
        query: str,
        top_k: int = settings.TOP_K_RETRIEVAL,
        rrf_k: int = 60,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Executes Reciprocal Rank Fusion (RRF) across Vector Search and BM25 results.
        Score = 1 / (rrf_k + rank_vector) + 1 / (rrf_k + rank_bm25)
        """
        # 1. Fetch Dense Vector Results
        dense_results = self.vector_store.similarity_search(query, k=top_k * 2, filter_dict=filter_dict)

        # 2. Fetch Sparse BM25 Results
        sparse_results: List[Document] = []
        if self.bm25_index:
            sparse_results = self.bm25_index.get_top_n(query, n=top_k * 2)

        # 3. Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        doc_lookup: Dict[str, Document] = {}

        for rank, doc in enumerate(dense_results):
            doc_id = doc.page_content[:150]
            doc_lookup[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))

        for rank, doc in enumerate(sparse_results):
            doc_id = doc.page_content[:150]
            doc_lookup[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (rrf_k + rank + 1))

        # Sort combined results by RRF score descending
        sorted_doc_ids = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        return [doc_lookup[doc_id] for doc_id in sorted_doc_ids[:top_k]]
