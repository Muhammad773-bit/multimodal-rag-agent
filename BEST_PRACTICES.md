# LangChain Best Practices Reference

This document explains how this RAG system implements LangChain best practices.

## 1. Modular Architecture

**Best Practice**: Separate concerns into distinct modules

**Implementation**:
```
src/
├── config.py          # Configuration
├── document_loader.py # Document I/O
├── embeddings_setup.py # Embeddings
├── vector_store.py    # Vector database
├── rag_pipeline.py    # Chain logic
└── cli.py            # User interface
```

**Benefits**:
- Easy testing of each component
- Reusable in different contexts
- Clear dependencies
- Easy to maintain and debug

## 2. Configuration Management

**Best Practice**: Centralize all settings

**Implementation** (`src/config.py`):
```python
class RAGConfig:
    EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL_ID = "google/flan-t5-base"
    CHUNK_SIZE = 1000
    RETRIEVAL_K = 4
    # ... more settings
```

**Benefits**:
- Single source of truth for settings
- Easy environment-specific overrides
- No magic numbers scattered in code
- Simple testing with different configs

## 3. Lazy Loading

**Best Practice**: Load expensive resources only when needed

**Implementation** (`embeddings_setup.py`):
```python
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = initialize_embeddings()
    return _embeddings
```

**Benefits**:
- Faster startup time
- Lower initial memory usage
- Only pay cost for what you use
- Easy to switch implementations

## 4. Factory Functions

**Best Practice**: Use factory functions for object creation

**Implementation**:
```python
# Instead of: rag = RAGPipeline()
# Use:
rag = get_rag_pipeline()
```

**Benefits**:
- Centralized initialization logic
- Easy singleton management
- Simplified testing and mocking
- Consistent error handling

## 5. Proper Error Handling

**Best Practice**: Handle errors gracefully with informative messages

**Implementation** (`document_loader.py`):
```python
def load_pdf(self, file_path):
    try:
        loader = PyPDFLoader(str(file_path))
        return loader.load()
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {e}")
        return []  # Graceful failure
```

**Benefits**:
- System continues despite individual document failures
- Clear error messages for debugging
- Users understand what went wrong
- Logging for troubleshooting

## 6. Comprehensive Logging

**Best Practice**: Log at appropriate levels for debugging and monitoring

**Implementation**:
```python
logger.info(f"Loading PDF: {file_path}")    # User-relevant
logger.debug(f"Processing page {i}")        # Detailed debugging
logger.warning(f"Empty document: {path}")   # Potential issues
logger.error(f"Failed to load: {error}")    # Serious problems
```

**Benefits**:
- Easy debugging in production
- Performance monitoring
- Error tracking
- User feedback

## 7. LCEL Chain Composition

**Best Practice**: Use LangChain Expression Language for chains

**Implementation** (`rag_pipeline.py`):
```python
self.chain = (
    {
        "context": retriever | self._format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | self.llm
)
```

**Benefits**:
- Declarative chain definition
- Easy to modify and extend
- Built-in error handling
- Streaming support

## 8. Metadata Preservation

**Best Practice**: Keep document metadata through processing pipeline

**Implementation** (`document_loader.py`):
```python
for doc in documents:
    doc.metadata["source_file"] = file_path.name
    doc.metadata["file_type"] = suffix
```

**Benefits**:
- Know which document each answer comes from
- Track document source for citations
- Enable filtering by document type
- Better debugging and auditing

## 9. Batch Processing

**Best Practice**: Process documents efficiently in batches

**Implementation** (`vector_store.py`):
```python
ids = vector_store.add_documents(documents, batch_size=100)
```

**Benefits**:
- More efficient than one-at-a-time
- Better performance for large document sets
- Reduced memory spikes
- Built-in transaction management

## 10. Standard Retriever Interface

**Best Practice**: Use LangChain's standard retriever interface

**Implementation** (`vector_store.py`):
```python
def get_retriever(self):
    vector_store = self._get_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})
```

**Benefits**:
- Compatible with all LangChain tools
- Easy to swap implementations
- Works with other LangChain components
- Standard patterns across projects

## 11. Environment-Based Configuration

**Best Practice**: Support environment variable overrides

**Implementation** (`config.py`):
```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
EMBEDDINGS_DEVICE = os.getenv("EMBEDDINGS_DEVICE", "cpu")
```

**Benefits**:
- Different configs per environment
- No code changes for deployment
- Secure credential handling
- CI/CD friendly

## 12. Separation of Concerns - API vs CLI

**Best Practice**: Core logic independent of interface

**Implementation**:
- `core modules` (loader, store, pipeline): Pure logic
- `cli.py`: User interface layer
- `example_usage.py`: Programmatic API usage

**Benefits**:
- Can use in web apps, APIs, scripts
- CLI not required for core functionality
- Easy to test core logic
- Multiple interfaces possible

## Anti-Patterns Avoided

### ❌ DON'T: Hardcode models
```python
# Bad
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

### ✅ DO: Use configuration
```python
# Good
embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDINGS_MODEL)
```

### ❌ DON'T: Ignore errors
```python
# Bad
documents = loader.load_all_documents()  # Might crash
```

### ✅ DO: Handle gracefully
```python
# Good
try:
    documents = loader.load_all_documents()
except Exception as e:
    logger.error(f"Error: {e}")
    # Continue gracefully
```

### ❌ DON'T: Create instances globally
```python
# Bad
llm = HuggingFacePipeline(...)  # Created on import
```

### ✅ DO: Lazy load
```python
# Good
def get_llm():
    global _llm
    if _llm is None:
        _llm = HuggingFacePipeline(...)
    return _llm
```

### ❌ DON'T: Mix business logic with I/O
```python
# Bad
def query(question):
    # Business logic mixed with print statements
    print("Searching...")
    # ... logic ...
    print("Found results")
```

### ✅ DO: Separate concerns
```python
# Good - just logic
def query(question):
    logger.info("Searching...")
    # ... logic ...
    return results

# CLI handles printing
print(answer)
```

## Configuration Examples

### For Development
```python
# In config.py
EMBEDDINGS_DEVICE = "cpu"
LLM_MAX_LENGTH = 256  # Quick responses
CHUNK_SIZE = 500
```

### For Production Quality
```python
EMBEDDINGS_MODEL = "all-mpnet-base-v2"  # Better quality
LLM_MODEL_ID = "google/flan-t5-large"    # Larger model
CHUNK_SIZE = 2000  # Better context
RETRIEVAL_K = 8    # More sources
```

### For Performance
```python
EMBEDDINGS_DEVICE = "cuda"  # GPU
LLM_MAX_LENGTH = 128  # Quick
CHUNK_SIZE = 500  # Small chunks
RETRIEVAL_K = 2  # Few sources
```

## Testing Your Implementation

### Test Configuration
```python
from src.config import config
assert config.EMBEDDINGS_MODEL == "all-MiniLM-L6-v2"
assert config.CHUNK_SIZE == 1000
```

### Test Document Loading
```python
from src.document_loader import get_document_loader
loader = get_document_loader()
docs = loader.load_all_documents()
assert len(docs) > 0
assert all("source_file" in doc.metadata for doc in docs)
```

### Test Vector Store
```python
from src.vector_store import get_vector_store
store = get_vector_store()
assert store.document_count() >= 0  # Works even if empty
```

### Test RAG Pipeline
```python
from src.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
answer = rag.query("test question")
assert isinstance(answer, str)
```

## Documentation Best Practices

This project includes:
- ✓ Docstrings on all public functions
- ✓ Type hints for clarity
- ✓ README.md for overview
- ✓ QUICKSTART.md for getting started
- ✓ ARCHITECTURE.md for design
- ✓ This file for best practices
- ✓ Inline comments for complex logic
- ✓ CLI help text (--help)

## When to Refactor

Consider refactoring if:
- [ ] A module exceeds 500 lines (split concerns)
- [ ] More than 3 levels of nesting (extract functions)
- [ ] Same code appears in multiple places (DRY principle)
- [ ] Configuration scattered across files (centralize)
- [ ] Error handling inconsistent (standardize)
- [ ] Magic numbers in code (use constants)
- [ ] Complex logic hard to test (modularize)
