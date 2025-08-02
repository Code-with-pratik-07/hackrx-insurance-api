import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.models import ClauseMatch

class SemanticSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = None
        self.document_store = []
        
    def process_documents(self, text_chunks: List[str], metadata: List[Dict]):
        """Process and index documents using TF-IDF"""
        # Store documents
        for i, (text, meta) in enumerate(zip(text_chunks, metadata)):
            self.document_store.append({
                'id': i,
                'text': text,
                'metadata': meta
            })
        
        # Create TF-IDF vectors
        self.document_vectors = self.vectorizer.fit_transform(text_chunks)
        return True
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[ClauseMatch]:
        """Perform TF-IDF based search"""
        if self.document_vectors is None:
            return []
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get top results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self.document_store):
                doc = self.document_store[idx]
                clause_match = ClauseMatch(
                    clause_id=f"clause_{doc['id']}",
                    clause_text=doc['text'],
                    similarity_score=float(similarities[idx]),
                    source_document=doc['metadata'].get('source', 'unknown'),
                    clause_type=self._classify_clause_type(doc['text']),
                    metadata=doc['metadata']
                )
                results.append(clause_match)
        
        return results
    
    def _classify_clause_type(self, text: str) -> str:
        """Classify clause type based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['exclusion', 'exclude', 'not covered']):
            return 'exclusion'
        elif any(word in text_lower for word in ['coverage', 'benefit', 'covered']):
            return 'coverage'
        elif any(word in text_lower for word in ['waiting period', 'wait']):
            return 'waiting_period'
        elif any(word in text_lower for word in ['claim', 'settlement']):
            return 'claims'
        else:
            return 'general'
