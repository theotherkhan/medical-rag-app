from pydantic import BaseModel
from typing import Optional

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