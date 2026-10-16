# Architecture & Design Decisions

## Overview

This Multi-Document RAG Agent follows LangChain best practices and implements a clean, modular architecture for production-ready RAG systems.

## Design Principles

### 1. **Separation of Concerns**
Each component has a single responsibility:
- **config.py**: Configuration management
- **document_loader.py**: Document loading and splitting
- **embeddings_setup.py**: Embedding model initialization
- **vector_store.py**: Vector database operations
- **rag_pipeline.py**: Chain construction and inference
- **cli.py**: User interface

### 2. **Lazy Loading Pattern**
Expensive resources are loaded only when needed:
```python
def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = initialize_embeddings()
    return _embeddings
```

This reduces startup time and memory usage.

### 3. **Factory Functions**
Use factory functions instead of instantiation throughout:
```python
rag = get_rag_pipeline()  # Gets or creates instance
```

This enables:
- Easy singleton management
- Centralized initialization
- Testing with mocks

### 4. **Configuration Management**
All settings in one place (`src/config.py`):
```python
class RAGConfig:
    EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL_ID = "google/flan-t5-base"
    CHUNK_SIZE = 1000
    # ... more settings
```

Benefits:
- Easy customization
- Environment-specific overrides possible
- No hardcoding scattered across code

## Component Architecture

### Document Loader
```
Raw Documents (PDF/DOCX/PPTX)
    ↓
PyPDFLoader / Docx2txtLoader / UnstructuredPowerPointLoader
    ↓
Document objects with metadata
    ↓
RecursiveCharacterTextSplitter
    ↓
Chunked documents ready for embedding
```

**Key Features:**
- Handles 3 document formats
- Preserves source metadata
- Smart text splitting with overlap
- Error handling per document

### Vector Store (Chroma)
```
Chunked Documents
    ↓
HuggingFace Embeddings
    ↓
Chroma Vector Store (Persistent)
    ↓
Semantic similarity search capability
```

**Key Features:**
- Persistent storage (survives restarts)
- Fast semantic search
- Batch document addition
- Collection management

### RAG Pipeline
```
User Question
    ↓
Vector Store Retrieval (k=4 by default)
    ↓
Retrieved Docs → Format as Context
    ↓
[Context + Question] → Prompt Template
    ↓
LLM (flan-t5-base) generates answer
    ↓
Response to user
```

**Key Features:**
- LCEL chain composition
- Proper context formatting
- Source tracking
- Error resilience

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
│  (CLI: --index, --query, --interactive, --list-documents)   │
└──────────┬──────────────────────────────────────────────────┘
           │
           ├─► INDEX FLOW                    QUERY FLOW
           │    ├─ Load documents            ├─ User question
           │    ├─ Split into chunks         ├─ Semantic search
           │    ├─ Generate embeddings       ├─ Retrieve docs
           │    ├─ Store in Chroma           ├─ Build context
           │    └─ Persist to disk           ├─ Generate prompt
           │                                 ├─ LLM inference
           │                                 └─ Format response
           │
           └─► VECTOR STORE
                 ├─ In-memory index
                 ├─ Persistent disk storage
                 └─ Semantic search engine
```

## Technology Stack Choices

### Embeddings: sentence-transformers/all-MiniLM-L6-v2
- ✓ Small (~80MB), fast inference
- ✓ Good quality for general tasks
- ✓ Open source, no API keys
- ✓ Works on CPU and GPU

**Alternatives:**
- `all-mpnet-base-v2`: Larger, better quality (~450MB)
- `distiluse-base-multilingual-cased-v2`: Multilingual support

### LLM: google/flan-t5-base
- ✓ Open source, local inference
- ✓ Instruction-tuned (good for QA)
- ✓ Moderate size, reasonable speed
- ✓ No rate limits, no cost

**Alternatives:**
- `google/flan-t5-large`: Better quality, slower
- `facebook/opt-350m`: Different architecture
- `mistralai/Mistral-7B-v0.1`: Larger, better quality

### Vector Store: Chroma
- ✓ Easy to use
- ✓ Local, open source
- ✓ Persistent storage
- ✓ Good for development/practice

**Alternatives:**
- Pinecone: Cloud, scalable, paid
- Weaviate: Self-hosted, feature-rich
- Milvus: Distributed, high performance

## Configuration Strategy

### Environment-Based Configuration

```python
# In production, override via environment
import os

class RAGConfig:
    EMBEDDINGS_DEVICE = os.getenv("EMBEDDINGS_DEVICE", "cpu")
    LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "google/flan-t5-base")
```

### Performance Tuning Parameters

```python
# For better quality (slower)
CHUNK_SIZE = 2000  # Larger chunks = more context
RETRIEVAL_K = 8    # More documents = better coverage
LLM_TEMPERATURE = 0.5  # Lower = more consistent

# For speed (potentially lower quality)
CHUNK_SIZE = 500   # Smaller chunks = faster processing
RETRIEVAL_K = 2    # Fewer documents = faster
EMBEDDINGS_DEVICE = "cuda"  # GPU acceleration
```

## Error Handling Strategy

Each module implements defensive programming:

```python
def load_document(self, file_path):
    try:
        documents = self.loader.load(file_path)
        return documents
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return []  # Graceful failure, continue processing
```

Benefits:
- Single document failure doesn't stop entire pipeline
- Detailed error logging for debugging
- User sees helpful error messages

## Logging Strategy

Comprehensive logging at multiple levels:

```python
logger.info("Starting indexing")      # User-relevant events
logger.debug("Processing chunk 5")    # Detailed debugging
logger.warning("File format unknown") # Recoverable issues
logger.error("Failed to load model")  # Serious issues
```

## Testing Approach

### Unit Testing Pattern
```python
def test_document_loader():
    loader = MultiFormatDocumentLoader()
    docs = loader.load_pdf(test_pdf_path)
    assert len(docs) > 0
    assert "source_file" in docs[0].metadata
```

### Integration Testing Pattern
```python
def test_full_rag_pipeline():
    # Setup
    loader.load_all_documents()
    vector_store.add_documents(docs)
    
    # Execute
    answer = rag.query("test question")
    
    # Assert
    assert len(answer) > 0
```

## Performance Considerations

### Memory Usage
- LLM loaded lazily only when querying
- Embeddings model loaded once, reused
- Documents streamed, not all in memory

### Speed Optimization
- First run: ~30s (models downloaded)
- Indexing: ~10-30s for 10 documents
- Queries: ~2-5s (depends on model)

### Scaling Limitations
- Single process (no parallelization)
- Local storage (limited by disk)
- Suitable for <10,000 documents

## LangChain Best Practices Implemented

| Practice | Implementation |
|----------|-----------------|
| Modular design | Separate modules per concern |
| LCEL chains | Modern chain composition in RAG |
| Lazy loading | Resources loaded on-demand |
| Error handling | Try-catch with logging |
| Configuration | Centralized `config.py` |
| Metadata | Preserved through pipeline |
| Retriever pattern | Standard LangChain interface |
| Logging | Comprehensive logging |
| Batch processing | Efficient document batching |
| Documentation | Docstrings on all public APIs |

## Future Enhancement Possibilities

1. **Multi-Index Support**: Separate indices for different document types
2. **Semantic Caching**: Cache embeddings of common queries
3. **Conversation Memory**: Multi-turn conversations with context
4. **Streaming Output**: Real-time token streaming for faster responses
5. **Hybrid Search**: Combine BM25 + semantic search
6. **Query Optimization**: Rephrase queries for better retrieval
7. **Evaluation Metrics**: RAGAS-based quality assessment
8. **API Server**: FastAPI wrapper for web integration
9. **Docker Support**: Containerized deployment
10. **Monitoring**: Prometheus metrics for production
