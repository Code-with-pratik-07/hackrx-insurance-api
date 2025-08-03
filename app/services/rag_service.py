from typing import List
from app.services.semantic_search import SemanticSearchEngine
from app.services.document_processor import DocumentProcessor
from app.services.llm_service import LLMService
from app.schemas.models import HackRXRequest, HackRXResponse

class RAGService:
    def __init__(self, groq_api_key: str):
        self.search_engine = SemanticSearchEngine()
        self.document_processor = DocumentProcessor()
        self.llm_service = LLMService(groq_api_key)
        self.is_initialized = False
    
    def process_hackrx_request(self, request: HackRXRequest) -> HackRXResponse:
        """Main function to process HackRX API request"""
        
        # Step 1: Download and process document
        if not self.is_initialized:
            pdf_content = self.document_processor.download_document(request.documents)
            text_chunks, metadata = self.document_processor.process_pdf_content(pdf_content)
            
            # Step 2: Index documents for semantic search
            self.search_engine.process_documents(text_chunks, metadata)
            self.is_initialized = True
        
        # Step 3: Process each question
        answers = []
        for question in request.questions:
            # Find relevant clauses
            relevant_clauses = self.search_engine.semantic_search(question, top_k=5)
            
            # Generate answer using LLM
            answer = self.llm_service.answer_question(question, relevant_clauses)
            answers.append(answer)
        
        return HackRXResponse(answers=answers)

