"""
Example usage and testing module for the RAG system.
Demonstrates programmatic API usage without CLI.
"""
import logging
from pathlib import Path

from src.config import config
from src.document_loader import get_document_loader
from src.vector_store import get_vector_store
from src.rag_pipeline import get_rag_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_programmatic_usage():
    """
    Example: Using RAG system programmatically (without CLI).
    """
    
    # 1. Load documents
    logger.info("Step 1: Loading documents...")
    loader = get_document_loader()
    documents = loader.load_all_documents()
    
    if not documents:
        logger.warning("No documents found. Please add files to documents/ directory.")
        return
    
    logger.info(f"Loaded {len(documents)} document chunks")
    
    # 2. Index documents
    logger.info("\nStep 2: Indexing documents...")
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    logger.info(f"Indexed {vector_store.document_count()} chunks total")
    
    # 3. Initialize RAG pipeline
    logger.info("\nStep 3: Initializing RAG pipeline...")
    rag = get_rag_pipeline()
    
    # 4. Ask questions
    logger.info("\nStep 4: Asking questions...")
    
    questions = [
        "What is this document about?",
        "Summarize the main points",
        "What are the key findings?",
    ]
    
    for question in questions:
        logger.info(f"\nQuestion: {question}")
        result = rag.query_with_sources(question)
        logger.info(f"Answer: {result['answer'][:200]}...")
        logger.info(f"Sources used: {result['num_sources']}")


if __name__ == "__main__":
    example_programmatic_usage()
