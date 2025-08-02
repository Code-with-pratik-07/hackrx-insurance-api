from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas.models import HackRXRequest, HackRXResponse
from app.services.rag_service import RAGService
from app.core.config import get_settings

router = APIRouter()

# Global RAG service instance
rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        settings = get_settings()
        rag_service = RAGService(settings.groq_api_key)
    return rag_service

def verify_api_key(authorization: str = Header(...)):
    """Verify Bearer token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    settings = get_settings()
    
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

@router.post("/hackrx/run", response_model=HackRXResponse)
async def process_hackrx_request(
    request: HackRXRequest,
    rag_service: RAGService = Depends(get_rag_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Main HackRX API endpoint for insurance document processing
    """
    try:
        response = rag_service.process_hackrx_request(request)
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "HackRX API is running"}
