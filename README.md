
# ADGM Corporate Agent – AI-Powered Document Compliance System

An AI-driven platform for **Abu Dhabi Global Market (ADGM)** corporate filings that automates **document classification** and prepares for full **compliance analysis** using advanced AI agents.

---

## 1. Overview
The **ADGM Corporate Agent** processes corporate documents for **classification** and **completeness validation**, with planned expansion into **regulation-backed compliance checks** via Retrieval-Augmented Generation (RAG).

---

## 2. Tech Stack
- **CrewAI** – Multi-agent orchestration & workflow management
- **LangChain** – Planned RAG pipeline & LLM integration
- **python-docx** – DOCX parsing & content extraction
- **Groq/OpenAI** – Large Language Models (llama-3.1-8b-instant) for document analysis
- **Python** – Core backend development

---

## 3. Current Implementation – Document Classifier Agent ✅

**Tool:** `ADGMDocumentClassifierTool`

**Capabilities:**
- Scans `/documents` directory for DOCX files
- Extracts content & headers for AI classification
- Validates against required ADGM documents:
  - Articles of Association
  - Memorandum of Association
  - Board Resolution
  - Register of Members
  - Register of Directors
  - Incorporation Application
- Completeness scoring (percentage)
- Error handling for corrupt or unsupported files

**Example Output:**
