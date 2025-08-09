from crewai import Agent, LLM
from dotenv import load_dotenv
from file_classifier_tool import ADGMDocumentClassifierTool 
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
load_dotenv()
import os

openai_api_key = os.getenv("OPEN_AI_KEY")

file_classifier_tool = ADGMDocumentClassifierTool()
# Document Classifier Agent
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

# Compliance Checker Agent  
ComplianceChecker = Agent(
    role="ADGM Compliance Checker",
    goal="Verify document completeness against ADGM requirements",
    backstory=(
        "You specialize in ADGM Companies Regulations 2020. "
        "You check if all required documents are present for the detected process "
        "and identify any missing items needed for compliance."
    ),
    allow_delegation=False,
    verbose=True,
    # tools=[compliance_checker],
    llm=LLM(
        api_key=openai_api_key,
        model="gpt-4o",
    )
)

# Red Flag Analyzer Agent
RedFlagAnalyzer = Agent(
    role="Red Flag Analyzer", 
    goal="Identify ADGM compliance issues and violations",
    backstory=(
        "You scan documents for common ADGM compliance issues: "
        "incorrect jurisdiction references, missing registered office, "
        "signature problems, and other regulatory violations. "
        "You provide specific citations and fix suggestions."
    ),
    allow_delegation=False,
    verbose=True,
    # tools=[red_flag_analyzer],
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