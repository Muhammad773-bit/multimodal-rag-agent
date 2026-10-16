"""
Configuration management for RAG Agent.
Follows LangChain best practices for environment and settings management.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RAGConfig:
    """Central configuration for RAG system."""
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DOCUMENTS_DIR = PROJECT_ROOT / "documents"
    CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
    
    # Embeddings Configuration
    EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers
    EMBEDDINGS_DEVICE = "cpu"  # or "cuda" for GPU
    
    # LLM Configuration
    LLM_MODEL_ID = "google/flan-t5-base"
    LLM_DEVICE = 0  # GPU device index, -1 for CPU
    LLM_MAX_LENGTH = 512
    LLM_TEMPERATURE = 0.7
    
    # Chroma Vector Store Configuration
    CHROMA_COLLECTION_NAME = "documents"
    CHROMA_PERSISTENCE = True
    
    # Document Processing
    SUPPORTED_FORMATS = [".pdf", ".docx", ".pptx"]
    CHUNK_SIZE = 1000  # Characters per chunk
    CHUNK_OVERLAP = 200  # Overlap between chunks
    
    # RAG Pipeline Configuration
    RETRIEVAL_K = 4  # Number of documents to retrieve
    RETRIEVAL_SCORE_THRESHOLD = 0.5
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_setup(cls) -> bool:
        """Validate that all required paths exist."""
        cls.ensure_directories()
        return True


# Initialize configuration
config = RAGConfig()
