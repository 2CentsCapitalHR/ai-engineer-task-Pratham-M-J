from crewai import Crew
from Agents import DocumentClassifier, RedFlagAnalyzer, DocumentRewriterAgent
from Tasks import document_classification, red_flag_analysis, document_rewriting
from dotenv import load_dotenv
import os

load_dotenv()

crew = Crew(
    agents = [DocumentClassifier, RedFlagAnalyzer, DocumentRewriterAgent],
    tasks = [document_classification, red_flag_analysis, document_rewriting],
    verbose = True
)

crew.kickoff()