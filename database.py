import os
import time
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import config

@st.cache_resource(show_spinner=False)
def get_vector_db_retriever():
    """Initializes, populates, and caches the vector database retriever."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2-preview")
    
    # Ingestion pipeline runs only if directory is missing
    if not os.path.exists(config.PERSIST_DIRECTORY):
        print("Entering")
        if not os.path.exists(config.PDF_FILE_PATH):
            raise FileNotFoundError(f"Source file {config.PDF_FILE_PATH} not found.")
            
        pdf = PdfReader(config.PDF_FILE_PATH)
        loaded_docs = []
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text.strip():
                loaded_docs.append(
                    Document(
                        page_content=text, 
                        metadata={"source": config.PDF_FILE_PATH, "page": page_num + 1}
                    )
                )
                
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
        split_docs = text_splitter.split_documents(loaded_docs)

        # Copy the page number explicitly onto every single chunk
        for chunk in split_docs:
            if "page" not in chunk.metadata:
                chunk.metadata["page"] = chunk.metadata.get("page", "Unknown")
        
        chroma_db = Chroma(persist_directory=config.PERSIST_DIRECTORY, embedding_function=embeddings)
        
        # Batch upload to respect API rate limits
        batch_size = 50
        for i in range(0, len(split_docs), batch_size):
            batch = split_docs[i: i + batch_size]
            chroma_db.add_documents(documents=batch)
            if i + batch_size < len(split_docs):
                time.sleep(60) # Free tier cooldown
                
    else:
        chroma_db = Chroma(persist_directory=config.PERSIST_DIRECTORY, embedding_function=embeddings)
        
    return chroma_db.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k":25, "where": {"page": {"$nin": ["6", "7", "13", "14", "15"]}}})

