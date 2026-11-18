from pathlib import Path
import os

from dotenv import load_dotenv

#Project root: D:\DataAssistant_AI-Agent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

#Frozen knowledge base
KNOWLEDGE_DIR = PROJECT_ROOT / "src" / "knowledge"

#Persistent local Chroma database
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

#Load environment variables from project-level .env
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

#Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")