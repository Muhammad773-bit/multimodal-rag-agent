"""
Multi-format document loader for PDF, DOCX, and PPTX.
Follows LangChain best practices for document loading and text splitting.
"""
from pathlib import Path
from typing import List, Optional
import logging

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from .config import config

logger = logging.getLogger(__name__)


class MultiFormatDocumentLoader:
    """
    Loads documents in multiple formats (PDF, DOCX, PPTX).
    Implements LangChain best practices for document loading.
    """
    
    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
    ):
        """
        Initialize document loader.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        logger.info(
            f"DocumentLoader initialized: chunk_size={chunk_size}, overlap={chunk_overlap}"
        )
    
    def load_pdf(self, file_path: Path) -> List[Document]:
        """Load PDF document."""
        logger.info(f"Loading PDF: {file_path}")
        try:
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from PDF")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            return []
    
    def load_docx(self, file_path: Path) -> List[Document]:
        """Load DOCX document."""
        logger.info(f"Loading DOCX: {file_path}")
        try:
            loader = Docx2txtLoader(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded DOCX document")
            return documents
        except Exception as e:
            logger.error(f"Error loading DOCX {file_path}: {e}")
            return []
    
    def load_pptx(self, file_path: Path) -> List[Document]:
        """Load PPTX document."""
        logger.info(f"Loading PPTX: {file_path}")
        try:
            loader = UnstructuredPowerPointLoader(str(file_path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} slides from PPTX")
            return documents
        except Exception as e:
            logger.error(f"Error loading PPTX {file_path}: {e}")
            return []
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load document based on file extension.
        
        Args:
            file_path: Path to document
            
        Returns:
            List of Document objects
        """
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            documents = self.load_pdf(file_path)
        elif suffix == ".docx":
            documents = self.load_docx(file_path)
        elif suffix == ".pptx":
            documents = self.load_pptx(file_path)
        else:
            logger.warning(f"Unsupported file format: {suffix}")
            return []
        
        # Add metadata
        for doc in documents:
            doc.metadata["source_file"] = file_path.name
            doc.metadata["file_type"] = suffix
        
        return documents
    
    def load_all_documents(
        self, documents_dir: Optional[Path] = None
    ) -> List[Document]:
        """
        Load all supported documents from directory.
        
        Args:
            documents_dir: Directory containing documents (default: config.DOCUMENTS_DIR)
            
        Returns:
            List of split Document objects
            
        Implements LangChain best practices:
        - Loads multiple formats
        - Splits documents into chunks
        - Preserves metadata
        """
        if documents_dir is None:
            documents_dir = config.DOCUMENTS_DIR
        
        all_documents = []
        
        if not documents_dir.exists():
            logger.warning(f"Documents directory not found: {documents_dir}")
            return []
        
        # Load documents by format
        for file_path in documents_dir.iterdir():
            if file_path.suffix.lower() in config.SUPPORTED_FORMATS:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
        
        logger.info(f"Loaded {len(all_documents)} total documents")
        
        # Split documents into chunks
        if all_documents:
            split_documents = self.text_splitter.split_documents(all_documents)
            logger.info(f"Split into {len(split_documents)} chunks")
            return split_documents
        
        return []


def get_document_loader() -> MultiFormatDocumentLoader:
    """Get document loader instance."""
    return MultiFormatDocumentLoader()
