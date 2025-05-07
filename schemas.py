from pydantic import BaseModel
from typing import Optional, List, Dict

class DocumentBase(BaseModel):
    title: str
    content: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int

    class Config:
        from_attributes = True

class SummarizationResponse(BaseModel):
    summary: str
    error: Optional[str] = None 

class SearchQuery(BaseModel):
    query: str
    k: int = 3

class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    similarity_score: float

class QuestionRequest(BaseModel):
    question: str
    k: int = 3  # Number of relevant documents to retrieve

class QuestionResponse(BaseModel):
    answer: str
    relevant_documents: List[Document]
    error: Optional[str] = None

class Condition(BaseModel):
    name: str
    icd_code: str
    icd_description: str
    confidence: float

class Treatment(BaseModel):
    name: str
    type: str  # medication, procedure, lifestyle, etc.
    details: Optional[str] = None


class StructuredExtractionResponse(BaseModel):
    conditions: List[Condition]
    treatments: List[Treatment]
    error: Optional[str] = None

class StructuredExtraction(BaseModel):
    patient_info: Dict[str, str]
    conditions: List[Dict[str, str]]
    medications: List[Dict[str, str]]
    procedures: List[Dict[str, str]]
    allergies: List[str]
    vitals: Dict[str, str]
    lab_results: List[Dict[str, str]]

    class Config:
        from_attributes = True