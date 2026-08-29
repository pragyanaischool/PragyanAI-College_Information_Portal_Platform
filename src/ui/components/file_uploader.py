"""
src/ui/components/file_uploader.py

Component to upload required institutional documents (PDF/PPTX), save them
to appropriate raw storage paths, and trigger vector store re-indexing.
"""

from pathlib import Path
import shutil
import streamlit as st
from src.core.config import settings
from src.rag_engine.ingestion import extract_pdf_chunks, extract_pptx_chunks
from src.rag_engine.vector_db import ChromaVectorStore


def render_document_uploader():
    """Renders a file upload panel with category selection and automatic vector indexing."""
    st.subheader("📤 Institutional Document Ingestion Portal")
    st.caption(
        "Upload verified admission flyers, regulatory dossiers (NAAC/NBA), or CoE slides to update the RAG knowledge base."
    )

    col_cat, col_replace = st.columns([2, 1])
    with col_cat:
        doc_category = st.selectbox(
            "Select Document Category:",
            [
                "Admissions & Fees (Brochures)",
                "NAAC SSR Audit (Regulatory)",
                "NBA Accreditation (Regulatory)",
                "Centers of Excellence (Presentations)",
            ],
        )

    # Route save path based on selected category
    if "Brochures" in doc_category:
        target_dir = settings.BROCHURES_DIR
        allowed_types = ["pdf"]
    elif "Regulatory" in doc_category:
        target_dir = settings.REGULATORY_DIR
        allowed_types = ["pdf"]
    else:
        target_dir = settings.PRESENTATIONS_DIR
        allowed_types = ["pptx"]

    uploaded_files = st.file_uploader(
        f"Upload {', '.join(allowed_types).upper()} Document(s):",
        type=allowed_types,
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("🚀 Process & Ingest to Vector Database", type="primary", use_container_width=True):
            saved_paths = []
            target_dir.mkdir(parents=True, exist_ok=True)

            with st.spinner("Saving documents and chunking for ChromaDB vector embeddings..."):
                for uploaded_file in uploaded_files:
                    dest_path = target_dir / uploaded_file.name
                    with open(dest_path, "wb") as f_out:
                        shutil.copyfileobj(uploaded_file, f_out)
                    saved_paths.append(dest_path)

                # Incremental chunk extraction and vector store upsert
                all_new_chunks = []
                for p in saved_paths:
                    if p.suffix.lower() == ".pdf":
                        chunks = extract_pdf_chunks(str(p), doc_category=doc_category.split(" (")[0])
                        all_new_chunks.extend(chunks)
                    elif p.suffix.lower() == ".pptx":
                        chunks = extract_pptx_chunks(str(p), doc_category="Centers of Excellence")
                        all_new_chunks.extend(chunks)

                if all_new_chunks:
                    try:
                        vstore = ChromaVectorStore()
                        vstore.add_documents(all_new_chunks)
                        st.success(
                            f"Successfully ingested {len(uploaded_files)} file(s) ({len(all_new_chunks)} semantic chunks) into ChromaDB!"
                        )
                    except Exception as e:
                        st.warning(
                            f"Files saved locally, but vector indexing encountered an issue: {e}"
                        )
                else:
                    st.success(f"Successfully saved {len(uploaded_files)} document(s) to {target_dir.name}/.")
