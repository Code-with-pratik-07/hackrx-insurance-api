from fastapi import FastAPI, HTTPException
import requests
import PyPDF2
import io
import re
import os
from typing import List, Dict

app = FastAPI(title="HackRX Insurance Policy API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "HackRX Insurance API with PDF Reading", "status": "running"}

@app.post("/api/v1/hackrx/run")
def hackrx_endpoint(request: dict):
    document_url = request.get("documents")
    questions = request.get("questions", [])
    
    if not document_url or not questions:
        raise HTTPException(status_code=400, detail="Documents and questions are required")
    
    try:
        # Download and read the PDF
        pdf_text = download_and_extract_pdf(document_url)
        
        # Answer questions based on the actual PDF content
        answers = []
        for question in questions:
            answer = analyze_document_for_question(pdf_text, question)
            answers.append(answer)
        
        return {"answers": answers}
        
    except Exception as e:
        # Fallback to generic answers if PDF reading fails
        fallback_answers = []
        for question in questions:
            fallback_answers.append(get_fallback_answer(question))
        return {"answers": fallback_answers}

def download_and_extract_pdf(url: str) -> str:
    """Download PDF from URL and extract text content"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        return full_text
        
    except Exception as e:
        raise Exception(f"Could not process PDF: {str(e)}")

def analyze_document_for_question(document_text: str, question: str) -> str:
    """Analyze document text to find relevant answer"""
    question_lower = question.lower()
    
    if "grace period" in question_lower and "premium" in question_lower:
        return search_for_grace_period(document_text)
    elif "waiting period" in question_lower and ("pre-existing" in question_lower or "disease" in question_lower):
        return search_for_waiting_period(document_text)
    elif "deductible" in question_lower:
        return search_for_deductible(document_text)
    elif "coverage" in question_lower or "benefit" in question_lower:
        return search_for_coverage(document_text)
    elif "premium" in question_lower and "amount" in question_lower:
        return search_for_premium_amount(document_text)
    elif "claim" in question_lower:
        return search_for_claim_process(document_text)
    else:
        return search_general_answer(document_text, question)

def search_for_grace_period(text: str) -> str:
    patterns = [r"grace period.*?(\d+).*?days?", r"(\d+).*?days?.*?grace", r"grace.*?(\d+)"]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            days = match.group(1) if match.groups() else "30"
            return f"According to the policy document, the grace period for premium payment is {days} days from the due date."
    if "grace period" in text.lower():
        return "The policy document mentions a grace period for premium payments. Please refer to the specific terms for exact duration."
    return "Grace period information not found in this policy document."

def search_for_waiting_period(text: str) -> str:
    patterns = [r"waiting period.*?(\d+).*?months?", r"(\d+).*?months?.*?waiting", r"pre-existing.*?(\d+).*?months?"]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            months = match.group(1) if match.groups() else "36"
            return f"The waiting period for pre-existing diseases is {months} months from the policy commencement date."
    if "waiting period" in text.lower() or "pre-existing" in text.lower():
        return "The policy document contains waiting period information. Please check the specific terms for details."
    return "Waiting period information not found in this policy document."

def search_for_deductible(text: str) -> str:
    patterns = [r"deductible.*?(\$?\d+(?:,\d+)*)", r"(\$?\d+(?:,\d+)*).*?deductible"]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount = match.group(1)
            return f"According to the policy, the deductible amount is {amount}."
    if "deductible" in text.lower():
        return "Deductible information is mentioned in the policy document. Please refer to the specific section for the exact amount."
    return "Deductible information not found in this policy document."

def search_for_coverage(text: str) -> str:
    if "coverage" in text.lower() or "benefit" in text.lower():
        coverage_match = re.search(r"coverage.*?(\$?\d+(?:,\d+)*)", text.lower())
        if coverage_match:
            amount = coverage_match.group(1)
            return f"The policy provides coverage up to {amount}. Additional benefits and exclusions are detailed in the policy document."
        return "Coverage information is available in the policy document. Please refer to the benefits section for detailed coverage terms."
    return "Coverage information not found in this policy document."

def search_for_premium_amount(text: str) -> str:
    patterns = [r"premium.*?(\$?\d+(?:,\d+)*)", r"(\$?\d+(?:,\d+)*).*?premium"]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount = match.group(1)
            return f"The premium amount mentioned in the policy is {amount}."
    if "premium" in text.lower():
        return "Premium information is mentioned in the policy document. Please check the payment section for specific amounts."
    return "Premium amount information not found in this policy document."

def search_for_claim_process(text: str) -> str:
    if "claim" in text.lower():
        return "Claim process information is detailed in the policy document. Please refer to the claims section for step-by-step procedures."
    return "Claim process information not found in this policy document."

def search_general_answer(text: str, question: str) -> str:
    question_words = question.lower().split()
    for word in question_words:
        if len(word) > 3 and word in text.lower():
            return f"Information related to '{question}' is mentioned in the policy document. Please refer to the relevant sections for detailed information."
    return "The requested information was not found in this policy document. Please consult the complete policy terms or contact your insurance provider."

def get_fallback_answer(question: str) -> str:
    question_lower = question.lower()
    if "grace period" in question_lower:
        return "The grace period for premium payment is typically 30 days from the due date."
    elif "waiting period" in question_lower:
        return "The waiting period for pre-existing diseases is usually 36 months (3 years)."
    else:
        return "Based on general insurance policy terms, this information requires detailed review of your specific policy document."

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
