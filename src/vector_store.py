"""
Chroma vector store setup and management.
Follows LangChain best practices for vector store initialization and persistence.
"""
import logging
from typing import List
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from .config import config
from .embeddings_setup import get_embeddings

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """
    Manages Chroma vector store for document retrieval.
    Implements LangChain best practices for persistence and retrieval.
    """
    
    def __init__(self, persist_directory: Path = config.CHROMA_DB_DIR):
        """
        Initialize Chroma vector store.
        
        Args:
            persist_directory: Path for vector store persistence
        """
        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.embeddings = get_embeddings()
        self._vector_store = None
        logger.info(f"ChromaVectorStore initialized with path: {persist_directory}")
    
    def _get_vector_store(self) -> Chroma:
        """
        Get or create vector store instance (lazy loading).
        
        Returns:
            Chroma vector store instance
        """
        if self._vector_store is None:
            logger.info(f"Loading Chroma from {self.persist_directory}")
            self._vector_store = Chroma(
                collection_name=config.CHROMA_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory),
            )
        return self._vector_store
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to vector store.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            List of document IDs
            
        Follows LangChain best practices:
        - Handles document batching efficiently
        - Preserves metadata
        - Manages persistence
        """
        if not documents:
            logger.warning("No documents to add")
            return []
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            vector_store = self._get_vector_store()
            ids = vector_store.add_documents(documents, batch_size=100)
            logger.info(f"Successfully added {len(ids)} document chunks")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query: str, k: int = config.RETRIEVAL_K) -> List[Document]:
        """
        Search for documents using semantic similarity.
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of relevant Document objects
            
        Implements LangChain best practices:
        - Uses semantic search via embeddings
        - Configurable retrieval count
        - Preserves document metadata
        """
        logger.info(f"Searching for: '{query}' (k={k})")
        
        try:
            vector_store = self._get_vector_store()
            documents = vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(documents)} relevant documents")
            return documents
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def search_with_scores(
        self, query: str, k: int = config.RETRIEVAL_K
    ) -> List[tuple]:
        """
        Search with relevance scores.
        
        Args:
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of (Document, score) tuples
        """
        logger.info(f"Searching with scores for: '{query}'")
        
        try:
            vector_store = self._get_vector_store()
            results = vector_store.similarity_search_with_scores(query, k=k)
            logger.info(f"Retrieved {len(results)} results with scores")
            return results
        except Exception as e:
            logger.error(f"Error searching with scores: {e}")
            return []
    
    def get_retriever(self):
        """
        Get LangChain retriever interface.
        
        Returns:
            Retriever object compatible with RAG chains
        """
        vector_store = self._get_vector_store()
        return vector_store.as_retriever(search_kwargs={"k": config.RETRIEVAL_K})
    
    def clear(self) -> None:
        """Clear all documents from vector store."""
        logger.warning("Clearing all documents from vector store")
        
        try:
            # Delete collection and reinitialize
            from chromadb.config import Settings
            
            # Remove the vector store instance to force reload
            self._vector_store = None
            
            # Delete the persistence directory
            import shutil
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
            
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            logger.info("Vector store cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise
    
    def document_count(self) -> int:
        """
        Get number of documents in vector store.
        
        Returns:
            Number of document chunks
        """
        try:
            vector_store = self._get_vector_store()
            collection = vector_store._collection
            return collection.count()
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0


def get_vector_store() -> ChromaVectorStore:
    """Get vector store instance."""
    return ChromaVectorStore()
