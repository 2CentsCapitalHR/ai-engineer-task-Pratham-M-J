from crewai import Crew
from Agents import DocumentClassifier
from Tasks import document_classification
from dotenv import load_dotenv
import os

load_dotenv()

crew = Crew(
    agents = [DocumentClassifier],
    tasks = [document_classification],
    verbose = True
)

crew.kickoff()