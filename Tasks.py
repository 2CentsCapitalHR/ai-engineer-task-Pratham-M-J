from crewai import Task
from Agents import DocumentClassifier, RedFlagAnalyzer, DocumentRewriterAgent
from crewai import Task


from crewai import Task

document_classification = Task(
    description=(
        "1. Use ADGMDocumentClassifierTool to classify all documents\n"
        "2. Check completeness against required ADGM documents\n"
        "3. Determine if sufficient valid documents exist for compliance analysis\n"
        "4. If insufficient documents, end workflow with detailed gap analysis\n"
        "5. If sufficient documents, prepare validated document list for next stage"
    ),
    expected_output=(
        "Classification report with decision on workflow continuation:\n"
        "- List of valid documents for analysis\n"
        "- Missing documents identification\n"
        "- CONTINUE/STOP decision with reasoning\n"
        "- Filtered document list ready for red-flag analysis"
    ),
    name="Document Classification and Flow Control",
    agent=DocumentClassifier
)

red_flag_analysis = Task(
    description=(
        "1. Continue to process the available valid documents; deprecate only if no valid documents are provided\n"
        "2. Use RAG tool to retrieve compliance rules for each valid document type\n"
        "3. Analyze each valid document for red flags and violations\n"
        "4. Do not skip analysis if documents are incomplete; list any missing or incomplete documents\n"
        "5. Generate compliance report for available valid documents only, with per-document sections"
    ),
    expected_output=(
        "Compliance report with detailed analysis for each valid document:\n"
        "Articles of Association"
            "Articles of Association Compliance Report:\n"
            "- Jurisdiction & Governing Law: [PASS/FAIL] with citations\n"
            "- Director Powers & Shareholder Rights: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Memorandum of Association"
            "Memorandum of Association Compliance Report:\n"
            "- Objects & Powers Clauses: [PASS/FAIL] with citations\n"
            "- Share Capital Information: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Board Resolution"
            "Board Resolution Compliance Report:\n"
            "- Director Appointment Procedures: [PASS/FAIL] with citations\n"
            "- Authorization Requirements: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Register of Members"
            "Register of Members Compliance Report:\n"
            "- Beneficial Ownership Disclosure: [PASS/FAIL] with citations\n"
            "- Updating & Maintenance Requirements: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Register of Directors"
            "Register of Directors Compliance Report:\n"
            "- Beneficial Ownership Disclosure: [PASS/FAIL] with citations\n"
            "- Updating & Maintenance Requirements: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Incorporation Application"
            "Incorporation Application Compliance Report:\n"
            "- Mandatory Sections & Declarations: [PASS/FAIL] with citations\n"
            "- Registered Office & Lease Agreement: [PASS/FAIL] with citations\n"
            "- Authorized Signatory Qualifications: [PASS/FAIL] with citations\n"
            "- Red Flags Identified: [list]\n"
            "- Recommended Remediation: [text]\n"
        
        "Missing or Unknown Documents"
            "Incomplete Documents Report:\n"
            "- Documents not provided or unrecognized: [list]\n"
            "- Impact on Analysis: [text]\n"
            "- Next Steps: Please upload missing documents to complete compliance checking\n"
        
    ),
    name="Conditional Red Flag Analysis with Per-Document Output",
    agent=RedFlagAnalyzer,
 
)



document_rewriting = Task(
    description=(
        "1. Analyze the red flag violations from the previous compliance analysis\n"
        "2. For each document with violations, generate specific compliance fixes:\n"
        "   - Create exact replacement text that meets ADGM standards\n"
        "   - Write detailed comments explaining each compliance fix\n"
        "   - Classify severity levels for each correction\n"
        "3. Use Document Rewriter Tool to apply all fixes to the uploaded documents\n"
        "4. Generate comprehensive JSON report of all edits made\n"
        "5. Save corrected documents with compliance annotations\n\n"
        "MANDATORY: Process all documents that had compliance violations identified in the previous analysis."
    ),
    expected_output=(
        "ADGM Document Rewriting Report:\n\n"
        "DOCUMENTS CORRECTED:\n"
        "- List of documents processed with edit counts\n"
        "- Severity breakdown of fixes applied\n\n"
        
        "CRITICAL FIXES APPLIED:\n"
        "- Jurisdiction corrections (UAE Federal → ADGM Courts)\n"
        "- Registered office corrections\n"
        "- Missing signature additions\n\n"
        
        "HIGH PRIORITY FIXES:\n"
        "- Beneficial ownership disclosures added\n"
        "- Joint signatory requirements implemented\n"
        "- Director appointment procedures corrected\n\n"
        
        "COMPLIANCE SUMMARY:\n"
        "- Total edits made across all documents\n"
        "- JSON report location with detailed change log\n"
        "- Corrected documents directory path\n"
        "- Overall compliance improvement assessment\n\n"
        
        "OUTPUT FILES:\n"
        "- /corrected_documents/ folder with fixed DOCX files\n"
        "- compliance_edit_report.json with detailed change tracking"
    ),
    name="ADGM Document Compliance Rewriting",
    agent=DocumentRewriterAgent,
    context=[red_flag_analysis]  # Gets violations from Red Flag Analyzer
)
