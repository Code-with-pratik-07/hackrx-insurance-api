import requests
import tempfile
import os
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def process_pdf_content(self, pdf_content: bytes) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Process PDF content and return chunks with metadata"""
        documents = []
        metadata = []
        
        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text from PDF
            reader = PdfReader(tmp_file_path)
            full_text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                full_text += page_text + "\n"
                
                # Store page-level metadata
                if page_text.strip():
                    documents.append(page_text)
                    metadata.append({
                        'source': 'policy_document.pdf',
                        'page_number': page_num + 1,
                        'total_pages': len(reader.pages),
                        'content_length': len(page_text)
                    })
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
        
        # Split into chunks
        final_chunks = []
        final_metadata = []
        
        for doc, meta in zip(documents, metadata):
            chunks = self.text_splitter.split_text(doc)
            
            for i, chunk in enumerate(chunks):
                final_chunks.append(chunk)
                chunk_meta = meta.copy()
                chunk_meta.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'chunk_length': len(chunk)
                })
                final_metadata.append(chunk_meta)
        
        return final_chunks, final_metadata
