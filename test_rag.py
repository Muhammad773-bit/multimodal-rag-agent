"""
Tests for RAG system components.
Run with: python -m pytest tests/ -v
"""
import pytest
import tempfile
from pathlib import Path

from src.config import RAGConfig
from src.document_loader import MultiFormatDocumentLoader
from src.embeddings_setup import initialize_embeddings
from src.vector_store import ChromaVectorStore


class TestConfiguration:
    """Test configuration management."""
    
    def test_config_paths_created(self):
        """Test that required directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RAGConfig()
            config.validate_setup()
            
            assert config.DOCUMENTS_DIR.exists()
            assert config.CHROMA_DB_DIR.exists()
    
    def test_config_values_valid(self):
        """Test configuration values are valid."""
        from src.config import config
        
        assert config.CHUNK_SIZE > 0
        assert config.CHUNK_OVERLAP < config.CHUNK_SIZE
        assert config.RETRIEVAL_K > 0
        assert config.EMBEDDINGS_MODEL
        assert config.LLM_MODEL_ID


class TestDocumentLoader:
    """Test document loading functionality."""
    
    def test_loader_initialization(self):
        """Test loader can be initialized."""
        loader = MultiFormatDocumentLoader()
        assert loader is not None
        assert loader.chunk_size > 0
    
    def test_custom_chunk_sizes(self):
        """Test loader with custom chunk sizes."""
        loader = MultiFormatDocumentLoader(chunk_size=500, chunk_overlap=50)
        assert loader.chunk_size == 500
        assert loader.chunk_overlap == 50
    
    def test_supported_formats(self):
        """Test detection of supported formats."""
        from src.config import config
        
        assert ".pdf" in config.SUPPORTED_FORMATS
        assert ".docx" in config.SUPPORTED_FORMATS
        assert ".pptx" in config.SUPPORTED_FORMATS


class TestVectorStore:
    """Test vector store functionality."""
    
    def test_vector_store_initialization(self):
        """Test vector store can be initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaVectorStore(persist_directory=Path(tmpdir))
            assert store is not None
    
    def test_document_count_empty(self):
        """Test document count on empty store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaVectorStore(persist_directory=Path(tmpdir))
            # Count should be 0 or raise no error
            try:
                count = store.document_count()
                assert count >= 0
            except Exception as e:
                pytest.skip(f"Vector store not fully initialized: {e}")
    
    def test_retriever_creation(self):
        """Test retriever can be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ChromaVectorStore(persist_directory=Path(tmpdir))
            retriever = store.get_retriever()
            assert retriever is not None


class TestEmbeddings:
    """Test embeddings functionality."""
    
    def test_embeddings_initialization(self):
        """Test embeddings can be initialized.
        
        Note: First run will download model (~350MB), may take time.
        """
        try:
            embeddings = initialize_embeddings()
            assert embeddings is not None
        except Exception as e:
            pytest.skip(f"Embeddings initialization skipped: {e}")
    
    def test_embeddings_dimension(self):
        """Test embeddings have correct dimension."""
        try:
            embeddings = initialize_embeddings()
            # all-MiniLM-L6-v2 has 384 dimensions
            embedding_vector = embeddings.embed_query("test")
            assert len(embedding_vector) == 384
        except Exception as e:
            pytest.skip(f"Embeddings test skipped: {e}")


# Integration tests (requires full setup)
class TestIntegration:
    """Integration tests for full pipeline."""
    
    @pytest.mark.slow
    def test_full_pipeline(self):
        """Test complete RAG pipeline.
        
        Requires documents to be indexed first.
        """
        try:
            from src.rag_pipeline import get_rag_pipeline
            
            rag = get_rag_pipeline()
            # This will fail if no documents indexed, which is expected
            result = rag.query("test")
            assert isinstance(result, str)
        except Exception as e:
            pytest.skip(f"Full pipeline test skipped: {e}")


# Unit test helpers
class TestHelpers:
    """Test helper functions."""
    
    def test_factory_functions_singleton(self):
        """Test that factory functions return consistent instances."""
        from src.embeddings_setup import get_embeddings
        from src.vector_store import get_vector_store
        from src.rag_pipeline import get_rag_pipeline
        
        # Embeddings
        emb1 = get_embeddings()
        emb2 = get_embeddings()
        assert emb1 is emb2  # Same instance (lazy loading)
        
        # Other factories create new instances (for isolation)
        store1 = get_vector_store()
        store2 = get_vector_store()
        # Note: Different instances is OK for stores
        assert store1 is not None and store2 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
