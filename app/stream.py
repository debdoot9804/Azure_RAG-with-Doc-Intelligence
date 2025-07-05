import streamlit as st
import os
from ingestion import uploader, parser, chunker
from backend import embedder, vectordb, search
from backend.logger import setup_logger
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger()

st.title("📄 Multimodal Document RAG (Azure)")

uploaded_file = st.file_uploader("Upload a PDF file")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())
    logger.info(f"User uploaded file: {uploaded_file.name}")

    blob_url = uploader.upload_to_blob("temp.pdf", "docs", uploaded_file.name)
    extracted_text = parser.parse_pdf_with_document_ai(blob_url)
    chunks = chunker.chunk_text(extracted_text)

    embedder.create_embeddings_index(chunks)
    st.success("Document uploaded, parsed, and indexed!")

    query = st.text_input("Ask a question from the document:")
    if query:
        result = search.search_query(query)
        st.write(result)
