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
        
        # Improved prompt template
        prompt_template = """
You are an ADGM corporate document classifier. Analyze the filename and content to classify the document.

Filename: {filename}
Content: {content}

ADGM Document Types:
1. Articles of Association - Company governance, director powers, shareholder rights
2. Memorandum of Association - Company formation, objects, share capital, subscribers  
3. Board Resolution - Director appointments, authorizations, corporate decisions
4. Register of Members - Shareholder information, share ownership
5. Register of Directors - Director details, appointments, addresses
6. Incorporation Application - ADGM registration application form

Classification Rules:
- Look for keywords in filename: "AOA", "Articles" → Articles of Association
- Look for keywords in filename: "MOA", "Memorandum" → Memorandum of Association
- Look for keywords: "Resolution", "Board" → Board Resolution
- Look for keywords: "Register" + "Directors" → Register of Directors
- Look for keywords: "Register" + "Members" → Register of Members
- Look for keywords: "Application", "Incorporation" → Incorporation Application

Respond with ONLY the document type name from the list above, or "Unknown" if it doesn't match any category.
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
                
                # Get classification with fallback logic
                document_type = self._classify_document(filename, content, analysis_chain)
                
                print(f"🔍 Classifying {filename} → {document_type}")  # Debug output
                
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
    
    def _classify_document(self, filename: str, content: str, analysis_chain) -> str:
        """Enhanced classification with fallback logic"""
        
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Rule-based classification first (more reliable)
        if "aoa" in filename_lower or "articles" in filename_lower:
            return "Articles of Association"
        
        if "moa" in filename_lower or "memorandum" in filename_lower:
            return "Memorandum of Association"
        
        if "resolution" in filename_lower:
            return "Board Resolution"
        
        if "register" in filename_lower:
            if "director" in filename_lower:
                return "Register of Directors"
            elif "member" in filename_lower:
                return "Register of Members"
        
        if "incorporation" in filename_lower or "application" in filename_lower:
            return "Incorporation Application"
        
        # Content-based classification (fallback)
        content_patterns = {
            "Articles of Association": ["articles of association", "company governance", "director powers", "articles", "aoa"],
            "Memorandum of Association": ["memorandum of association", "company objects", "share capital", "memorandum", "moa"],
            "Board Resolution": ["resolution", "resolved", "board of directors", "board resolution"],
            "Register of Directors": ["register of directors", "director details", "director information"],
            "Register of Members": ["register of members", "shareholder", "member information"],
            "Incorporation Application": ["incorporation application", "application for", "registration authority"]
        }
        
        for doc_type, patterns in content_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return doc_type
        
        # LLM classification as last resort
        try:
            llm_result = analysis_chain.invoke({
                'filename': filename, 
                'content': content[:500]
            })
            
            # Multiple regex patterns to catch LLM response
            llm_response = llm_result.content.strip()
            
            # Try different extraction patterns
            patterns = [
                r'Final Classification:\s*(.+?)(?:\n|$)',
                r'Classification:\s*(.+?)(?:\n|$)', 
                r'^(.+?)(?:\n|$)',  # First line
                r'(Articles of Association|Memorandum of Association|Board Resolution|Register of Members|Register of Directors|Incorporation Application)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, llm_response, re.IGNORECASE)
                if match:
                    classification = match.group(1).strip()
                    # Validate against known document types
                    valid_types = ["Articles of Association", "Memorandum of Association", 
                                 "Board Resolution", "Register of Members", 
                                 "Register of Directors", "Incorporation Application"]
                    
                    for valid_type in valid_types:
                        if valid_type.lower() in classification.lower():
                            return valid_type
            
            return "Unknown"
            
        except Exception as e:
            print(f"⚠️ LLM classification failed for {filename}: {e}")
            return "Unknown"



