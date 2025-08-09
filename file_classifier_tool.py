from crewai.tools import BaseTool
from typing import List, Dict, Any
from docx import Document
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
import re

class ADGMDocumentClassifierTool(BaseTool):
    name: str = "ADGM Document Classifier"
    description: str = "Classifies ADGM corporate documents and checks for completeness"
    
    def _run(self) -> Dict[str, Any]:
        # Required documents for incorporation
        REQUIRED_DOCUMENTS = [
            "Articles of Association",
            "Memorandum of Association", 
            "Board Resolution",
            "Register of Members",
            "Register of Directors",
            "Incorporation Application"
        ]
        
        # Always scan the /documents directory for uploaded files
        documents_dir = os.path.join(os.getcwd(), 'documents')
        if not os.path.exists(documents_dir):
            return {
                "error": f"Directory '{documents_dir}' does not exist.",
                "status": "error"
            }

        file_paths = [os.path.join(documents_dir, f) for f in os.listdir(documents_dir) if f.endswith('.docx')]
        
        if not file_paths:
            return {
                "error": "No DOCX files found in documents directory.",
                "status": "error"
            }

        llm = ChatGroq(
            groq_api_key=os.environ['GROQ_API_KEY'],
            model='llama-3.1-8b-instant'
        )
        
        prompt_template = """
You are an ADGM corporate document classification AI.

Given a document's filename and content preview, classify the document type.

**Filename:** {filename}
**Content Preview:** {content}

**Document Classification:**
Select one from: Articles of Association, Memorandum of Association, Board Resolution, Register of Members, Register of Directors, Incorporation Application, Unknown

**Final Classification:** [Document type name only]
"""
        
        prompt = PromptTemplate(
            input_variables=["filename", "content"],
            template=prompt_template
        )
        
        analysis_chain = prompt | llm
        
        # Process all documents
        classified_documents = []
        detected_types = []
        
        for file_path in file_paths:
            try:
                doc = Document(file_path)
                filename = os.path.basename(file_path)
                
                content = ""
                for para in doc.paragraphs[:10]: 
                    if para.text.strip():
                        content += para.text.strip() + " "
                
                # Get classification
                analysis_result = analysis_chain.invoke({
                    'filename': filename, 
                    'content': content[:500]
                })
                
                # Extract final classification
                classification_match = re.search(r'\*\*Final Classification:\*\*\s*(.+?)(?:\n|$)', analysis_result.content)
                document_type = classification_match.group(1).strip() if classification_match else "Unknown"
                
                classified_documents.append({
                    "filename": filename,
                    "document_type": document_type,
                    "status": "success"
                })
                
                if document_type != "Unknown":
                    detected_types.append(document_type)
                
            except Exception as e:
                classified_documents.append({
                    "filename": os.path.basename(file_path),
                    "document_type": "Error",
                    "error": str(e),
                    "status": "error"
                })
        
        # Check completeness
        missing_documents = [doc for doc in REQUIRED_DOCUMENTS if doc not in detected_types]
        present_documents = [doc for doc in REQUIRED_DOCUMENTS if doc in detected_types]
        
        return {
            "classified_documents": classified_documents,
            "present_documents": present_documents,
            "missing_documents": missing_documents,
            "completeness_score": len(present_documents) / len(REQUIRED_DOCUMENTS),
            "is_complete": len(missing_documents) == 0,
            "total_files_processed": len(file_paths),
            "status": "success"
        }
