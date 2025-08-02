from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HackRXRequest(BaseModel):
    documents: str = Field(..., description="URL to the policy PDF document")
    questions: List[str] = Field(..., description="List of questions to answer")

class HackRXResponse(BaseModel):
    answers: List[str] = Field(..., description="Corresponding answers to the questions")

class ClauseMatch(BaseModel):
    clause_id: str
    clause_text: str
    similarity_score: float
    source_document: str
    clause_type: str
    metadata: Dict[str, Any]
