from crewai.tools import BaseTool
from typing import Dict, Any
import os

class SimpleFileWriterTool(BaseTool):
    name: str = "Simple File Writer Tool"
    description: str = "Opens/creates file and writes content - that's it"
    
    def _run(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Simple file writer - open/create/write
        Args:
            filename: Name of file (e.g., "AOA.docx" or "AOA.txt")
            content: Text content to write
        """
        
        # Create corrected_files directory
        output_dir = os.path.join(os.getcwd(), "corrected_documents")
        os.makedirs(output_dir, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(output_dir, filename)
        
        try:
            # Open -> Create -> Write
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Written: {filename}")
            
            return {
                "status": "success",
                "filename": filename,
                "path": file_path,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "filename": filename,
                "error": str(e)
            }
