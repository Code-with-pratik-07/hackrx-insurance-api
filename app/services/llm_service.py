from typing import List
from groq import Groq

# Import models (will work after we create models.py)
try:
    from app.schemas.models import ClauseMatch
except ImportError:
    from pydantic import BaseModel
    from typing import Dict, Any
    class ClauseMatch(BaseModel):
        clause_id: str
        clause_text: str
        similarity_score: float
        source_document: str
        clause_type: str
        metadata: Dict[str, Any]

class LLMService:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def answer_question(self, question: str, relevant_clauses: List[ClauseMatch]) -> str:
        """Generate answer based on question and relevant clauses"""
        
        # Prepare context from clauses
        context_parts = []
        for i, clause in enumerate(relevant_clauses[:5]):  # Top 5 clauses
            context_parts.append(f"""
Context {i+1} (Similarity: {clause.similarity_score:.3f}):
{clause.clause_text}
""")
        
        context = "\n".join(context_parts)
        
        prompt = f"""
You are an expert insurance policy analyst. Based on the provided policy document context, 
answer the following question accurately and concisely.

Question: {question}

Relevant Policy Context:
{context}

Instructions:
1. Answer based ONLY on the provided context
2. Be specific and cite relevant policy terms
3. If the context doesn't contain enough information, state that clearly
4. Keep the answer focused and professional
5. Include specific details like timeframes, amounts, conditions when available

Answer:"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
