from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db
from models import Base, Document
from schemas import DocumentCreate, Document as DocumentSchema, SummarizationResponse
from llm_service import llm_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Workflow Automation",
    description="API for medical workflow automation",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the server is running.
    Returns a simple status confirmation.
    """
    return {"status": "ok"}

@app.post("/documents/", response_model=DocumentSchema)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """
    Create a new document.
    """
    db_document = Document(title=document.title, content=document.content)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@app.post("/summarize_note/", response_model=SummarizationResponse)
async def summarize_note(document: DocumentCreate):
    """
    Summarize a medical note using LLM.
    """
    summary = await llm_service.summarize_medical_note(document.content)
    if summary is None:
        return SummarizationResponse(
            summary="",
            error="Failed to generate summary. Please try again later."
        )
    return SummarizationResponse(summary=summary)

@app.get("/documents/", response_model=List[DocumentSchema])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of documents.
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@app.get("/documents/{document_id}", response_model=DocumentSchema)
def read_document(document_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific document by ID.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document 

