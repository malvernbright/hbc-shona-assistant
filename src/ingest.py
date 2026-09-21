import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledgebase"
DB_DIR = BASE_DIR / "chroma_db"

def ingest_documents():
    # 1. Initialize the offline embedding model
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 2. Load all PDFs from the knowledgebase folder
    documents = []
    for pdf_file in KNOWLEDGE_BASE_DIR.glob("*.pdf"):
        print(f"Loading {pdf_file.name}...")
        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())
        
    if not documents:
        print("No PDFs found in knowledgebase directory.")
        return

    # 3. Chunk the documents preserving the SBP stages
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\nSTAGE", "\nCHIKAMU", "\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 4. Save to local ChromaDB
    print("Saving to ChromaDB...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )
    print("Ingestion complete! Database saved to ./chroma_db")

if __name__ == "__main__":
    ingest_documents()