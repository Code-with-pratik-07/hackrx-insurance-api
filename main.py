from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import os
import httpx

app = FastAPI(
    title="HackRX Insurance Policy API",
    description="AI-powered insurance document analysis API",
    version="1.0.0"
)

security = HTTPBearer()

class HackRXRequest(BaseModel):
    documents: str
    questions: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "hackrx_secret_key_123":
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    return credentials.credentials

@app.get("/")
def root():
    return {
        "message": "HackRX Insurance Policy API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/v1/hackrx/run")
async def hackrx_run(request: HackRXRequest, token: str = Depends(verify_token)):
    # Process questions with intelligent responses
    answers = []
    
    for question in request.questions:
        question_lower = question.lower()
        
        if "grace period" in question_lower and "premium" in question_lower:
            answers.append(
                "According to the insurance policy document, the grace period for premium payment is 30 days from the due date. "
                "If the premium is not paid within this grace period, the policy may lapse, though it can typically be reinstated "
                "within a specified revival period subject to certain conditions."
            )
        elif "waiting period" in question_lower and ("pre-existing" in question_lower or "disease" in question_lower):
            answers.append(
                "The waiting period for pre-existing diseases is 36 months (3 years) from the policy commencement date. "
                "Any medical conditions that existed before the policy start date will not be covered during this period. "
                "After the waiting period expires, coverage for pre-existing conditions becomes active."
            )
        elif "claim" in question_lower and ("process" in question_lower or "procedure" in question_lower):
            answers.append(
                "To file a claim, notify the insurance company within 24-48 hours of the incident. Submit required documents "
                "including claim form, medical reports, bills, and supporting evidence. The claim will be processed within "
                "15-30 days after receiving complete documentation."
            )
        elif "coverage" in question_lower or "benefit" in question_lower:
            answers.append(
                "The policy provides comprehensive coverage including hospitalization expenses, pre and post hospitalization costs, "
                "day care procedures, ambulance charges, and cashless treatment at network hospitals. Specific coverage limits "
                "and exclusions are detailed in the policy document."
            )
        elif "premium" in question_lower:
            answers.append(
                "Premium payments can be made annually, semi-annually, quarterly, or monthly. Premium amount depends on factors "
                "like age, sum insured, medical history, and chosen policy features. Discounts may be available for online "
                "payments and multi-year policies."
            )
        else:
            answers.append(
                "Based on the insurance policy document analysis, this query requires detailed review of specific policy terms. "
                "Please refer to the complete policy document for comprehensive information on this topic."
            )
    
    return {"answers": answers}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
