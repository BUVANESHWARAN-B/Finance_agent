from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import traceback
import json

app = FastAPI()

# Initialize the embedding model (Consider initializing this once globally)
embeddings_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
vector_db: Optional[FAISS] = None  # Initialize vector_db with Optional type hint

def initialize_vector_db(texts: List[str]):
    """Initializes the vector database with the given texts."""
    global vector_db
    texts_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = texts_splitter.create_documents(texts)
    try:
        embeddings = embeddings_model.encode(
            [doc.page_content for doc in docs]
        ).tolist()  # type: ignore
        vector_db = FAISS.from_embeddings(
            text_embeddings=list(zip([str(i) for i in range(len(docs))], embeddings)),
            embedding_function=embeddings_model.encode,
        )
        print("FAISS index initialized successfully.")
    except Exception as e:
        print(f"Error initializing FAISS index: {e}")
        traceback.print_exc()  # Print the full traceback
        vector_db = None  # Ensure vector_db is None in case of failure

def add_to_vector_db(text: str):
    """Adds a single text to the vector database."""

    global vector_db
    texts_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = texts_splitter.create_documents([text])
    try:
        embeddings = embeddings_model.encode(
            [doc.page_content for doc in docs]
        ).tolist()  # type: ignore
        new_db = FAISS.from_embeddings(
            text_embeddings=list(zip([str(i) for i in range(len(docs))], embeddings)),
            embedding_function=embeddings_model.encode,
        )
        if vector_db is None:
            vector_db = new_db
        else:
            vector_db.merge_from(new_db)
        print("Text added to FAISS index.")
    except Exception as e:
        print(f"Error adding text to FAISS index: {e}")
        traceback.print_exc()

def process_and_index(urls: List[str] = [], pdf_files: List[str] = []):
    """Processes URLs and PDF files, and indexes their content."""

    texts: List[str] = []
    all_loaded_data: List[str] = []  # Keep track of all loaded data

    for url in urls:
        try:
            loader = WebBaseLoader(url)
            data = loader.load()
            loaded_texts = [doc.page_content for doc in data]
            texts.extend(loaded_texts)
            all_loaded_data.extend(loaded_texts)
            print(f"Successfully loaded data from URL: {url}")
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            traceback.print_exc()

    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            data = loader.load()
            loaded_texts = [doc.page_content for doc in data]
            texts.extend(loaded_texts)
            all_loaded_data.extend(loaded_texts)
            print(f"Successfully loaded data from PDF: {pdf_file}")
        except Exception as e:
            print(f"Error processing PDF {pdf_file}: {e}")
            traceback.print_exc()

    if texts:
        print("Data loaded successfully. Initializing FAISS.")
        initialize_vector_db(texts)
    else:
        print("No data loaded from URLs or PDFs. FAISS index not initialized.")

    print("All loaded data (for debugging):", all_loaded_data)  # Print all loaded data

def retrieve_relevant_content(query: str) -> List[str]:
    """Retrieves the most relevant content from the vector database for a given query."""

    if vector_db is None:
        print("FAISS index is not initialized. Cannot retrieve content.")
        return []

    try:
        embedding_vector = embeddings_model.encode(query).tolist()
        _, search_results = vector_db.similarity_search_with_relevance_scores(
            embedding_vector, k=2
        )
        relevant_content = [doc.page_content for doc, _ in search_results]
        print("Retrieved relevant content:", relevant_content)
        return relevant_content
    except Exception as e:
        print(f"Error retrieving relevant content: {e}")
        traceback.print_exc()
        return []

@app.post("/process_and_index/")
async def process_agent_indexing(payload: Dict):
    """API endpoint to process and index content from URLs and PDF files."""

    urls: List[str] = payload.get("urls", [])
    pdf_files: List[str] = payload.get("pdf_files", [])  # Assuming you might add PDF support
    process_and_index(urls, pdf_files)
    return {"status": "indexing completed"}

@app.post("/retrieve_relevant_content/")
async def retrieve_agent_content(payload: Dict):
    """API endpoint to retrieve relevant content based on a query."""

    query: str = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query not provided")
    return retrieve_relevant_content(query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)