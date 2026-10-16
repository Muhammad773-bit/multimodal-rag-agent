"""
Advanced example showing custom configurations and patterns.
"""
import logging
from pathlib import Path

from src.config import RAGConfig
from src.document_loader import MultiFormatDocumentLoader
from src.vector_store import ChromaVectorStore
from src.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomRAGSetup:
    """
    Example of customizing RAG system for specific use cases.
    """
    
    @staticmethod
    def custom_chunk_configuration():
        """
        Example 1: Using custom chunk sizes for different document types.
        """
        logger.info("Example 1: Custom Chunk Configuration")
        
        # Larger chunks for better context (financial documents)
        loader_financial = MultiFormatDocumentLoader(
            chunk_size=2000,  # Larger chunks
            chunk_overlap=300,
        )
        
        # Smaller chunks for detailed information (technical docs)
        loader_technical = MultiFormatDocumentLoader(
            chunk_size=500,  # Smaller chunks
            chunk_overlap=100,
        )
        
        logger.info("Created custom loaders for different document types")
        return loader_financial, loader_technical
    
    @staticmethod
    def batch_index_specific_documents():
        """
        Example 2: Index specific document types separately.
        """
        logger.info("Example 2: Batch Indexing Specific Documents")
        
        from src.config import config
        
        loader = MultiFormatDocumentLoader()
        vector_store = ChromaVectorStore()
        
        # Index PDFs first
        pdf_files = list(config.DOCUMENTS_DIR.glob("*.pdf"))
        if pdf_files:
            logger.info(f"Found {len(pdf_files)} PDF files")
            for pdf_file in pdf_files:
                docs = loader.load_document(pdf_file)
                if docs:
                    vector_store.add_documents(docs)
                    logger.info(f"Indexed {len(docs)} chunks from {pdf_file.name}")
        
        # Index DOCX files
        docx_files = list(config.DOCUMENTS_DIR.glob("*.docx"))
        if docx_files:
            logger.info(f"Found {len(docx_files)} DOCX files")
            for docx_file in docx_files:
                docs = loader.load_document(docx_file)
                if docs:
                    vector_store.add_documents(docs)
                    logger.info(f"Indexed {len(docs)} chunks from {docx_file.name}")
    
    @staticmethod
    def semantic_search_with_scoring():
        """
        Example 3: Semantic search with relevance scoring.
        """
        logger.info("Example 3: Semantic Search with Scoring")
        
        from src.vector_store import ChromaVectorStore
        
        vector_store = ChromaVectorStore()
        
        queries = [
            "machine learning algorithms",
            "data science techniques",
            "artificial intelligence",
        ]
        
        for query in queries:
            logger.info(f"\nSearching for: {query}")
            results = vector_store.search_with_scores(query, k=3)
            
            for doc, score in results:
                logger.info(f"Score: {score:.4f} - {doc.page_content[:100]}...")
    
    @staticmethod
    def hybrid_query_approach():
        """
        Example 4: Combining semantic search with keyword filtering.
        """
        logger.info("Example 4: Hybrid Query Approach")
        
        from src.vector_store import ChromaVectorStore
        
        vector_store = ChromaVectorStore()
        
        # Get all documents with scores
        query = "data analysis"
        results = vector_store.search_with_scores(query, k=10)
        
        # Filter by score threshold
        min_score = 0.6
        filtered_results = [
            (doc, score) for doc, score in results
            if score >= min_score
        ]
        
        logger.info(
            f"Found {len(filtered_results)} results with score >= {min_score}"
        )
        
        for doc, score in filtered_results:
            file_type = doc.metadata.get("file_type", "unknown")
            logger.info(f"{file_type}: {score:.4f}")
    
    @staticmethod
    def custom_rag_prompt():
        """
        Example 5: Using custom prompts for specific domains.
        """
        logger.info("Example 5: Custom RAG Prompt")
        
        from src.rag_pipeline import RAGPipeline
        
        rag = RAGPipeline()
        
        # Override system prompt for domain-specific use
        rag.SYSTEM_PROMPT = """You are a domain expert assistant.

Your role is to:
1. Answer questions accurately based on provided documents
2. Cite specific sections when answering
3. Acknowledge if information is not in documents
4. Provide structured answers when possible

Context documents:
{context}

User Question: {question}

Expert Answer:"""
        
        logger.info("Custom prompt configured for domain-specific answers")


def run_advanced_examples():
    """Run all advanced examples."""
    print("\n" + "=" * 60)
    print("ADVANCED EXAMPLES")
    print("=" * 60 + "\n")
    
    setup = CustomRAGSetup()
    
    # Example 1
    print("\n--- Example 1: Custom Chunk Configuration ---")
    setup.custom_chunk_configuration()
    
    # Example 2
    print("\n--- Example 2: Batch Indexing ---")
    setup.batch_index_specific_documents()
    
    # Example 3
    print("\n--- Example 3: Semantic Search with Scoring ---")
    setup.semantic_search_with_scoring()
    
    # Example 4
    print("\n--- Example 4: Hybrid Query ---")
    setup.hybrid_query_approach()
    
    # Example 5
    print("\n--- Example 5: Custom Prompts ---")
    setup.custom_rag_prompt()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_advanced_examples()
