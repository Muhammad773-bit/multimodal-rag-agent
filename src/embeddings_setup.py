"""
Embeddings setup using HuggingFaceEmbeddings.
Follows LangChain best practices for embeddings initialization.
"""
from langchain_huggingface import HuggingFaceEmbeddings
import logging
from .config import config

logger = logging.getLogger(__name__)


def initialize_embeddings():
    """
    Initialize HuggingFace embeddings with all-MiniLM-L6-v2 model.
    
    Returns:
        HuggingFaceEmbeddings: Initialized embeddings object
        
    Follows LangChain best practices:
    - Uses HuggingFaceEmbeddings from langchain_huggingface
    - Configures model and device appropriately
    - Enables query instruction optimization
    """
    logger.info(f"Initializing embeddings model: {config.EMBEDDINGS_MODEL}")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDINGS_MODEL,
        model_kwargs={
            "device": config.EMBEDDINGS_DEVICE,
            "trust_remote_code": True,
        },
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 32,
        },
    )
    
    logger.info(f"Embeddings initialized on device: {config.EMBEDDINGS_DEVICE}")
    return embeddings


# Lazy load embeddings (instantiated on first use)
_embeddings = None


def get_embeddings():
    """
    Get or create embeddings instance (lazy loading).
    
    Returns:
        HuggingFaceEmbeddings: Embeddings instance
    """
    global _embeddings
    if _embeddings is None:
        _embeddings = initialize_embeddings()
    return _embeddings
