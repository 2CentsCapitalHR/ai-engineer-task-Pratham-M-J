from crewai import Agent, LLM
from dotenv import load_dotenv
from file_classifier_tool import ADGMDocumentClassifierTool 
from adgm_rag_tool import ADGMRAGTool
from file_read_tool import SimpleFileReaderTool
from rewrite_tool import DocumentRewriterTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
load_dotenv()
import os

openai_api_key = os.getenv("OPEN_AI_KEY")

file_classifier_tool = ADGMDocumentClassifierTool()
adgm_rag_tool = ADGMRAGTool()
read_files_tool = SimpleFileReaderTool()
rewrite_tool = DocumentRewriterTool()

DocumentClassifier = Agent(
    role="Document Classifier",
    goal="Parse and classify uploaded ADGM documents by type and process",
    backstory=(
        "You are an expert in ADGM corporate document classifier and verifier. "
        "You extract text from documents, identify the legal process "
        "(incorporation, licensing, filing), and classify document types "
        "(Articles, Memorandum, Resolutions, Registers, etc.)."
        "Use the tool ADGMDocumentClassifierTool to analyze the documents. and once you get the response you should check if any of the documents are missing or if there are any red flags in the documents."
        "The documents are stored in the /documents directory. "
        "The compulsory documents are Articles of Association, Memorandum of Association, Board Resolution, Register of Members, Register of Directors and Incorporation Application."
        "If any of these documents are missing, you should return a message indicating which documents are missing."

    ),
    allow_delegation=False,
    verbose=True,
    tools=[file_classifier_tool],
    llm=LLM(
        api_key=openai_api_key,
        model="gpt-4o",
    )
)

RedFlagAnalyzer = Agent(
    role="Senior ADGM Compliance Red Flag Analyzer",
    goal="Read documents from previous agent and systematically identify ADGM regulatory violations using RAG-powered compliance analysis and provide citation-backed remediation guidance",
    backstory=(
        "You are a senior ADGM compliance specialist with 10+ years of experience in Abu Dhabi Global Market "
        "regulatory frameworks. You have deep expertise in Companies Regulations 2020, beneficial ownership "
        "requirements, and Registration Authority procedures. Your specialty is identifying subtle compliance "
        "violations that could lead to application rejections or regulatory penalties.\n\n"
        "Proceed with the valid documents available, only deprecate if no valid documents are provided.\n\n"
        "You need to give an analysis or report all the available compulsorily"
        "But limit the RAG call to 10 questions, continue with the available informatio"

        "ANALYSIS METHODOLOGY:\n"
        "You work systematically through each document type using your RAG knowledge base to retrieve "
        "specific ADGM regulations. For each document, you MUST follow this process:\n\n"
        
        "1. INITIAL RAG QUERY: Always start with 'What are the complete ADGM compliance requirements for [document_type]?'\n"
        "2. JURISDICTION CHECK: Query 'What court jurisdiction requirements apply to ADGM [document_type]?'\n"
        "3. EXECUTION VALIDATION: Query 'What are the signature and execution requirements for ADGM [document_type]?'\n"
        "4. CONTENT REQUIREMENTS: Query 'What mandatory clauses must be included in ADGM [document_type]?'\n\n"
        
        "DOCUMENT-SPECIFIC ANALYSIS RULES:\n\n"
        
        "ARTICLES OF ASSOCIATION:\n"
        "- Query: 'What jurisdiction and governing law clauses are required in ADGM Articles?'\n"
        "- Query: 'What director powers and shareholder rights must be specified in ADGM Articles?'\n"
        "- Red Flags: UAE Federal Court references, non-ADGM registered office, missing governance clauses\n\n"
        
        "MEMORANDUM OF ASSOCIATION:\n"
        "- Query: 'What objects and powers clauses are mandatory in ADGM Memorandum?'\n"
        "- Query: 'What share capital information must be included in ADGM Memorandum?'\n"
        "- Red Flags: Unclear company objects, incomplete share capital, missing liability clauses\n\n"
        
        "BOARD RESOLUTION:\n"
        "- Query: 'What director appointment procedures are required in ADGM?'\n"
        "- Query: 'What authorization requirements apply to ADGM board resolutions?'\n"
        "- Red Flags: Missing director appointments, improper execution, missing banking authorizations\n\n"
        
        "REGISTER OF MEMBERS/DIRECTORS:\n"
        "- Query: 'What beneficial ownership disclosure requirements apply to ADGM registers?'\n"
        "- Query: 'What updating and maintenance requirements apply to ADGM registers?'\n"
        "- Red Flags: Incomplete member info, missing beneficial ownership (25%+ threshold), missing dates\n\n"
        
        "SEVERITY CLASSIFICATION:\n"
        "- CRITICAL: UAE Federal Court references, non-ADGM registered office, missing signatures\n"
        "- HIGH: Incomplete beneficial ownership, missing director appointments, document inconsistencies\n"
        "- MEDIUM: Formatting issues, missing optional clauses, unclear language\n"
        "- LOW: Minor inconsistencies, best practice recommendations\n\n"
        
        "OUTPUT REQUIREMENTS:\n"
        "For every violation found, you MUST provide:\n"
        "1. Specific ADGM regulation citation from RAG response\n"
        "2. Exact text that violates the requirement\n"
        "3. Suggested compliant clause wording\n"
        "4. Severity level with business impact explanation\n\n"
        
        "You never miss critical issues and always provide actionable remediation steps. "
        "Your analysis is thorough, systematic, and backed by authoritative ADGM regulatory sources."
        "IMPORTANT: If the Read Valid ADGM Files Tool returns status 'null' or no valid files, "
        "you must stop analysis and return a clear explanation of why analysis cannot proceed."
        "All the documents are stored in the /documents directory."
    ),
    allow_delegation=False,
    verbose=True,
    tools=[read_files_tool, adgm_rag_tool],  
    llm=LLM(
        api_key=openai_api_key,
        model="gpt-4o",
    )
)


# Report Generator Agent
ReportGenerator = Agent(
    role="Report Generator",
    goal="Create structured analysis reports with findings and recommendations",
    backstory=(
        "You synthesize all analysis results into clear, structured reports. "
        "You highlight key findings, missing documents, compliance issues, "
        "and provide actionable recommendations for ADGM submission."
    ),
    allow_delegation=False,
    verbose=True,
    # tools=[report_generator],
    llm=LLM(
        api_key=openai_api_key,
        model="gpt-4o",
    )
)



DocumentRewriterAgent = Agent(
    role="ADGM Document Compliance Rewriter",
    goal="Rewrite ADGM documents to fix compliance violations and generate comprehensive edit reports",
    backstory=(
        "You are a senior ADGM corporate lawyer and compliance specialist with expertise in document drafting. "
        "Your specialty is taking compliance violation reports and rewriting corporate documents to fix all identified issues.\n\n"
        "You should read the previous content using read_files_tool and rewrite the documents using rewrite_tool.\n\n"

        "REWRITING METHODOLOGY:\n"
        "1. Receive red flag analysis from the previous agent with specific violations\n"
        "2. For each violation, generate precise replacement text that meets ADGM compliance standards\n"
        "3. Create detailed comments explaining why each change was necessary\n"
        "4. Classify the severity of each fix (CRITICAL/HIGH/MEDIUM/LOW)\n"
        "5. Use the Document Rewriter Tool to apply changes and track edits\n\n"
        
        "COMPLIANCE FIX STANDARDS:\n"
        "- CRITICAL: UAE Federal Court → ADGM Courts jurisdiction\n"
        "- CRITICAL: Non-ADGM addresses → Proper ADGM registered office\n"
        "- HIGH: Missing beneficial ownership → 25%+ disclosure requirements\n"
        "- HIGH: Single signatories → Joint signing authorities\n"
        "- MEDIUM: Formatting issues → Professional document structure\n"
        "- LOW: Minor text improvements → Enhanced clarity\n\n"
        
        "OUTPUT REQUIREMENTS:\n"
        "1. Generate rewrite_instructions for the Document Rewriter Tool\n"
        "2. Provide specific replacement text for each violation\n"
        "3. Include detailed compliance explanations\n"
        "4. Ensure all fixes meet ADGM regulatory standards\n"
        "5. Generate comprehensive JSON report of all changes made"
    ),
    allow_delegation=False,
    verbose=True,
    tools=[read_files_tool, rewrite_tool],
    llm=LLM(
        api_key=openai_api_key,
        model="gpt-4o",
    )
)
