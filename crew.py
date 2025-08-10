from crewai import Crew
from Agents import DocumentClassifier, RedFlagAnalyzer
from Tasks import document_classification, red_flag_analysis
from dotenv import load_dotenv
import os

load_dotenv()

crew = Crew(
    agents = [DocumentClassifier, RedFlagAnalyzer],
    tasks = [document_classification, red_flag_analysis],
    verbose = True
)

crew.kickoff()