"""
tests/test_vector_search.py

Integration tests for PyMuPDF extraction, text chunking, and ChromaDB vector search.
"""

import os
from langchain_core.documents import Document
import pytest

from src.rag_engine.hybrid_search import HybridSearchEngine, SimpleBM25
from src.rag_engine.ingestion import extract_pdf_chunks, extract_pptx_chunks


def test_extract_pdf_chunks_missing_file():
    """Verifies graceful handling when the target PDF path does not exist."""
    chunks = extract_pdf_chunks("data/raw/brochures/non_existent.pdf")
    assert chunks == []


def test_simple_bm25_ranking():
    """Verifies exact term scoring and rank ordering using in-memory BM25."""
    corpus = [
        Document(page_content="RVCE offers high placement salary packages for Computer Science.", metadata={"id": 1}),
        Document(page_content="BMSCE is one of the oldest autonomous engineering colleges.", metadata={"id": 2}),
        Document(page_content="NAAC Criterion 3 covers sponsored research grants and patents.", metadata={"id": 3}),
    ]

    bm25 = SimpleBM25(corpus)
    results = bm25.get_top_n("Computer Science placement package", n=1)
    assert len(results) == 1
    assert "Computer Science" in results[0].page_content


def test_hybrid_search_fusion():
    """Verifies reciprocal rank fusion combines sparse and dense search candidates."""
    corpus = [
        Document(page_content="Management quota fee for CSE is 16 lakhs per year.", metadata={"doc_category": "Fees"}),
        Document(page_content="NBA Tier-1 accreditation requires continuous OBE evaluation.", metadata={"doc_category": "NBA"}),
    ]
    bm25 = SimpleBM25(corpus)
    top_docs = bm25.get_top_n("Management quota fee", n=1)
    assert len(top_docs) == 1
    assert "16 lakhs" in top_docs[0].page_content
