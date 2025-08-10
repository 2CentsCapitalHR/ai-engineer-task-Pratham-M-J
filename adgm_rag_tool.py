from crewai.tools import BaseTool
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from typing import Dict, Any

class ADGMRAGTool(BaseTool):
    name: str = "ADGM Regulations RAG Tool"
    description: str = "Retrieves ADGM compliance rules and citations from knowledge base"
    
    # Class-level variables to ensure single initialization
    _vectorstore = None
    _rag_chain = None
    _initialized = False
    
    def __init__(self):
        super().__init__()
        if not self._initialized:
            self._setup_rag_pipeline()
            ADGMRAGTool._initialized = True
    
    def _setup_rag_pipeline(self):
        """Setup RAG pipeline only once"""
        
        db_path = 'db'
        documents_path = './rag_docs'
        
        embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
        )
        
        # Check if vector store already exists and has data
        if os.path.exists(db_path) and self._vector_store_has_data(db_path):
            print("📂 Loading existing vector store...")
            ADGMRAGTool._vectorstore = Chroma(
                collection_name='policy',
                embedding_function=embeddings,
                persist_directory=db_path
            )
        else:
            print("🔨 Creating new vector store...")
            adgm_docs = self._load_documents(documents_path)
            
            if not adgm_docs:
                raise ValueError("No ADGM documents found to create vector store")
            
            text_splitter = CharacterTextSplitter(
                chunk_size=400,
                chunk_overlap=20,
                separator="\n"
            )
            texts = text_splitter.split_documents(adgm_docs)
            print(f"📄 Created {len(texts)} text chunks")
            
            ADGMRAGTool._vectorstore = Chroma(
                collection_name='policy',
                embedding_function=embeddings,
                persist_directory=db_path
            )
            ADGMRAGTool._vectorstore.add_documents(texts)
            print("✅ Vector store created and persisted")
        
        retriever = ADGMRAGTool._vectorstore.as_retriever(
            search_type='mmr',
            search_kwargs={'k': 5, 'fetch_k': 10}
        )
        
        llm = ChatOpenAI(
            model='gpt-4o-mini', 
            openai_api_key=os.environ['OPEN_AI_KEY'],
            temperature=0.3,  
            max_tokens=512,
        )
        
        prompt = ChatPromptTemplate.from_template("""
You are an ADGM compliance expert. Answer the question based only on the following ADGM regulation context.
If you cannot find the answer in the context, say "I don't have enough information about this in the ADGM regulations provided."

Context: {context}
Question: {input}

Answer:
""")
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        ADGMRAGTool._rag_chain = create_retrieval_chain(retriever, document_chain)
        
        print("🎯 RAG pipeline initialized successfully")
    
    def _vector_store_has_data(self, db_path: str) -> bool:
        """Check if vector store exists and has data"""
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name='sentence-transformers/all-MiniLM-L6-v2',
            )
            temp_store = Chroma(
                collection_name='policy',
                embedding_function=embeddings,
                persist_directory=db_path
            )
            # Try a simple query to check if data exists
            results = temp_store.similarity_search("test", k=1)
            return len(results) > 0
        except Exception:
            return False
    
    def _load_documents(self, directory: str):
        """Load documents from directory"""
        documents = []
        
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist")
            return documents
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            try:
                if filename.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                    
                elif filename.endswith('.txt'):
                    loader = TextLoader(file_path, encoding='utf8')
                    docs = loader.load()
                    documents.extend(docs)
                    
                print(f"Loaded: {filename} ({len(docs)} pages/chunks)")
                
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        
        print(f"total documents loaded: {len(documents)}")
        return documents
    
    def _run(self, query: str) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            if not ADGMRAGTool._rag_chain:
                raise ValueError("RAG chain not initialized")
            
            response = ADGMRAGTool._rag_chain.invoke({"input": query})
            
            return {
                "query": query,
                "answer": response["answer"],
                "status": "success"
            }
            
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "status": "error"
            }


