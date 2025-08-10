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
        "1. Read all original documents using read_files_tool\n"
        "2. Extract violations from previous red flag analysis\n"
        "3. For each document with violations:\n"
        "   - Create corrected version of ENTIRE document\n"
        "   - Highlight all corrections with severity colors\n"
        "   - Add detailed compliance comments\n"
        "4. Use DocumentRewriterTool to generate:\n"
        "   - Corrected DOCX files in /corrected_documents/\n"
        "   - Individual JSON reports for each file\n"
        "   - Master compliance_corrections_report.json\n"
        "5. Ensure ALL documents are completely rewritten, not just edited"
    ),
    expected_output=(
        "Document Rewriting Results:\n\n"
        "FILES GENERATED:\n"
        "- CORRECTED_[filename].docx for each processed document\n"
        "- [filename]_corrections.json for each file\n"
        "- compliance_corrections_report.json (master report)\n\n"
        
        "CORRECTIONS SUMMARY:\n"
        "- Total documents rewritten: [X]\n"
        "- Total corrections applied: [X]\n"
        "- Critical fixes: [X]\n"
        "- High priority fixes: [X]\n\n"
        
        "OUTPUT LOCATIONS:\n"
        "- Corrected documents: /corrected_documents/\n"
        "- JSON reports: /corrected_documents/\n"
        "- All files saved successfully with full content rewrite"
    ),
    name="Complete Document Rewriting with JSON Reports",
    agent=DocumentRewriterAgent,
    context=[red_flag_analysis]
)
