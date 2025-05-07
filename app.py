from fastapi import FastAPI, Query, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json
from datetime import datetime
import openai
from dotenv import load_dotenv
import os

from database import engine, get_db
from llm_service import llm_service
from vector_store import vector_store
from icd_service import icd_service

from models import Base as BaseModel, Document
from schemas import (
    DocumentCreate, 
    Document as DocumentSchema, 
    SummarizationResponse,
    SearchQuery,
    SearchResult,
    QuestionRequest,
    QuestionResponse,
    StructuredExtraction
)


# Create database tables
BaseModel.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Workflow Automation",
    description="API for medical workflow automation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint that redirects to the API documentation.
    """
    return RedirectResponse(url="/docs")

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

@app.post("/search/", response_model=List[SearchResult])
async def search_documents(query: SearchQuery):
    """
    Search for similar documents using semantic search.
    """
    results = vector_store.search(query.query, k=query.k)
    return results

@app.post("/answer_question/", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    """
    Answer a question using relevant documents and LLM.
    """
    try:
        # Get relevant documents using vector search
        relevant_docs = vector_store.search(request.question, k=request.k)
        
        if not relevant_docs:
            return QuestionResponse(
                answer="I couldn't find any relevant information to answer your question.",
                relevant_documents=[],
                error=None
            )
        
        # Generate answer using LLM
        answer = await llm_service.answer_question(request.question, relevant_docs)
        
        if answer is None:
            return QuestionResponse(
                answer="",
                relevant_documents=[],
                error="Failed to generate answer. Please try again later."
            )
        
        return QuestionResponse(
            answer=answer,
            relevant_documents=relevant_docs,
            error=None
        )
    except Exception as e:
        return QuestionResponse(
            answer="",
            relevant_documents=[],
            error=f"An error occurred: {str(e)}"
        )

@app.post("/extract_structured", response_model=StructuredExtraction)
async def extract_structured(note: DocumentCreate):
    """
    Extract structured data from a medical note and include ICD codes for conditions.
    """
    try:
        # First, use GPT to extract structured data
        prompt = f"""
        Extract structured data from the following medical note. Return the data in JSON format with the following structure:
        {{
            "patient_info": {{
                "name": "string",
                "age": "string",
                "gender": "string",
                "dob": "string (YYYY-MM-DD)"
            }},
            "conditions": [
                {{
                    "condition": "string",
                    "status": "string (active/resolved)",
                    "onset_date": "string (YYYY-MM-DD)"
                }}
            ],
            "medications": [
                {{
                    "name": "string",
                    "dosage": "string",
                    "frequency": "string",
                    "start_date": "string (YYYY-MM-DD)"
                }}
            ],
            "procedures": [
                {{
                    "name": "string",
                    "date": "string (YYYY-MM-DD)",
                    "provider": "string"
                }}
            ],
            "allergies": ["string"],
            "vitals": {{
                "blood_pressure": "string",
                "heart_rate": "string",
                "temperature": "string",
                "weight": "string",
                "height": "string"
            }},
            "lab_results": [
                {{
                    "test_name": "string",
                    "value": "string",
                    "unit": "string",
                    "reference_range": "string",
                    "date": "string (YYYY-MM-DD)"
                }}
            ]
        }}

        Medical Note:
        {note}
        """

        response = await llm_service.extract_structured(prompt)

        structured_data = json.loads(response.choices[0].message.content)

        # Look up ICD codes for each condition
        for condition in structured_data["conditions"]:
            print("\n\nCondition: ", condition)
            icd_result = await icd_service.get_icd_code(condition["condition"])
            if icd_result:
                condition["icd_code"] = icd_result["icd_code"]
                #condition["icd_code"] = icd_result["destination_entities"][0]["theCode"]
                condition["icd_description"] = icd_result["icd_description"]


        return structured_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

