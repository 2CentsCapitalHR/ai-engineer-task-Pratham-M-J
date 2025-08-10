from crewai.tools import BaseTool
from typing import Dict, Any
from docx import Document
import os


class SimpleFileReaderTool(BaseTool):
    name: str = "Simple File Reader Tool"
    description: str = "Reads all DOCX files from documents directory"
    
    def _run(self) -> Dict[str, Any]:
        """
        Simple file reader - always reads from documents directory, no parameters needed
        """
        
        # Always read from documents directory
        documents_dir = os.path.join(os.getcwd(), "documents")
        
        print(f"🔍 Reading from: {documents_dir}")
        
        if not os.path.exists(documents_dir):
            return {
                "error": f"Directory '{documents_dir}' does not exist",
                "file_contents": {},
                "status": "error"
            }
        
        # Get all DOCX files
        docx_files = [f for f in os.listdir(documents_dir) if f.endswith('.docx')]
        
        if not docx_files:
            return {
                "error": f"No DOCX files found in '{documents_dir}'",
                "file_contents": {},
                "status": "error"  
            }
        
        file_contents = {}
        successfully_read = 0
        
        for filename in docx_files:
            file_path = os.path.join(documents_dir, filename)
            
            try:
                doc = Document(file_path)
                
                # Extract all text content
                content = ""
                for para in doc.paragraphs:
                    if para.text.strip():
                        content += para.text.strip() + "\n"
                
                file_contents[filename] = {
                    "content": content,
                    "word_count": len(content.split()),
                    "status": "success"
                }
                successfully_read += 1
                print(f"✅ Read: {filename} ({len(content.split())} words)")
                
            except Exception as e:
                file_contents[filename] = {
                    "error": f"Error reading {filename}: {str(e)}",
                    "status": "error"
                }
                print(f"❌ Failed: {filename} - {str(e)}")
        
        return {
            "file_contents": file_contents,
            "files_read": successfully_read,
            "total_files": len(docx_files),
            "status": "success" if successfully_read > 0 else "error"
        }
