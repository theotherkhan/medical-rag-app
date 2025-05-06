import os
from typing import List, Dict
import numpy as np
import faiss
from openai import OpenAI
from sqlalchemy.orm import Session
from models import Document
from database import get_db

class VectorStore:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=self.api_key)
        self.dimension = 1536  # OpenAI's text-embedding-3-small dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents: List[Dict] = []  # Store document metadata

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text using OpenAI's embedding model."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding, dtype=np.float32)

    def add_document(self, document: Document):
        """Add a document to the vector store."""
        # Create document text by combining title and content
        text = f"Title: {document.title}\nContent: {document.content}"
        
        # Get embedding
        embedding = self.get_embedding(text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding]))
        
        # Store document metadata
        self.documents.append({
            "id": document.id,
            "title": document.title,
            "content": document.content
        })

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for similar documents using a query string."""
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search in FAISS index
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        # Return matching documents
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx != -1:  # FAISS returns -1 for empty slots
                doc = self.documents[idx]
                doc["similarity_score"] = float(1 / (1 + distance))  # Convert distance to similarity score
                results.append(doc)
        
        return results

def initialize_vector_store():
    """Initialize the vector store with all documents from the database."""
    vector_store = VectorStore()
    
    # Get database session
    db = next(get_db())
    
    # Get all documents
    documents = db.query(Document).all()
    
    # Add each document to the vector store
    for doc in documents:
        vector_store.add_document(doc)
    
    return vector_store

# Create a singleton instance
vector_store = initialize_vector_store() 