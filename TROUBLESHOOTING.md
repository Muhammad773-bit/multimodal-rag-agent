# Troubleshooting & FAQ

## Common Issues and Solutions

### 1. "ModuleNotFoundError: No module named 'langchain'"

**Solution**:
```bash
pip install -r requirements.txt
```

Make sure you're in the project directory and using the correct Python version (3.8+).

### 2. "No documents found in documents/"

**Issue**: The system can't find your files.

**Solution**:
- Ensure files are in `documents/` folder
- Check file extensions (.pdf, .docx, .pptx) - case sensitive
- Verify files are valid (not corrupted)

Example:
```bash
documents/
├── report.pdf      ✓ Correct
├── guide.DOCX      ✗ Wrong case
├── data.txt        ✗ Unsupported format
└── image.png       ✗ Not a document
```

### 3. "CUDA out of memory"

**Issue**: GPU doesn't have enough memory for models.

**Solution**:
```python
# In src/config.py
EMBEDDINGS_DEVICE = "cpu"  # Use CPU instead
LLM_DEVICE = -1            # -1 for CPU

# Or reduce model size
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # Already small
LLM_MODEL_ID = "google/flan-t5-small"  # Even smaller
```

### 4. "Model download too slow / not working"

**Issue**: First run downloads large models (500MB+).

**Solution**:
- Check internet connection
- Models are cached in `~/.cache/huggingface/`
- Wait for download to complete (appears to hang)
- Can manually set cache location:

```python
import os
os.environ['HF_HOME'] = '/path/to/cache'
```

### 5. "Vector store seems empty after indexing"

**Issue**: `chroma_db/` directory exists but no data.

**Solution**:
```bash
# Check what was indexed
python main.py --list-documents

# Manually verify
import os
size = os.path.getsize("chroma_db")  # Should be > 0
```

If still empty, re-index:
```bash
python main.py --reset-db
python main.py --index
```

### 6. "Poor quality answers"

**Issue**: Answers are vague or incorrect.

**Solutions**:

1. **Add more documents** - Better coverage improves answers
2. **Adjust chunk size**:
   ```python
   CHUNK_SIZE = 1500  # Larger chunks = more context
   ```

3. **Increase retrieval count**:
   ```python
   RETRIEVAL_K = 8  # More sources
   ```

4. **Use better models**:
   ```python
   # Better embeddings
   EMBEDDINGS_MODEL = "all-mpnet-base-v2"
   
   # Better LLM
   LLM_MODEL_ID = "google/flan-t5-large"
   ```

5. **Optimize prompt** in `src/rag_pipeline.py`:
   - Be more specific in system prompt
   - Add domain context
   - Specify response format

### 7. "Slow performance / timeouts"

**Issue**: Queries take too long.

**Solutions**:

1. **Use GPU**:
   ```python
   EMBEDDINGS_DEVICE = "cuda"
   LLM_DEVICE = 0  # GPU index
   ```

2. **Smaller models**:
   ```python
   EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # Already small
   LLM_MODEL_ID = "google/flan-t5-base"
   ```

3. **Reduce retrieval count**:
   ```python
   RETRIEVAL_K = 2  # Fewer documents
   ```

4. **Smaller chunks**:
   ```python
   CHUNK_SIZE = 500  # Faster processing
   ```

### 8. "EOFError: EOF when reading a line" in interactive mode

**Issue**: Terminal input handling issue on Windows.

**Solution**:
```bash
# Try with explicit encoding
python -u main.py --interactive

# Or use regular query mode
python main.py --query "your question"
```

### 9. "PDF not loading properly"

**Issue**: Text extraction from PDF fails.

**Possible causes**:
- Scanned PDF (image-based, not text-based)
- Encrypted/password-protected PDF
- Corrupted file

**Solutions**:
1. Verify PDF is text-based (can copy text manually)
2. Remove password protection
3. Convert scanned PDFs to text using OCR first

### 10. "Memory grows over time"

**Issue**: Application uses more memory after several queries.

**Solution**:
This is normal with LLMs. If critical:
- Use smaller models
- Implement periodic restarts
- Use GPU (offloads memory from CPU)

## FAQ

### Q: Can I use this in a web application?

**A**: Yes, but needs adaptation:
1. Wrap in FastAPI/Flask app
2. Move LLM init outside request handler
3. Implement connection pooling
4. Add error handling for crashes
5. See `example_usage.py` for programmatic API

### Q: How do I update/re-index documents?

**A**: Two approaches:

**Option 1**: Clean rebuild
```bash
python main.py --reset-db
# Add new documents to documents/ folder
python main.py --index
```

**Option 2**: Incremental (keeps old docs)
```bash
# Just re-run indexing (adds duplicates)
python main.py --index
```

Note: Option 2 adds duplicates. For production, implement tracking.

### Q: Can I use different models?

**A**: Yes, edit `src/config.py`:

```python
# Embeddings options
EMBEDDINGS_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDINGS_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# LLM options (Hugging Face)
LLM_MODEL_ID = "google/flan-t5-large"
LLM_MODEL_ID = "facebook/opt-6.7b"
LLM_MODEL_ID = "mistralai/Mistral-7B-v0.1"
```

### Q: How to use OpenAI instead of open-source models?

**A**: Not supported in current setup, but possible:

```python
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Replace embeddings
embeddings = OpenAIEmbeddings(openai_api_key="...")

# Replace LLM
llm = ChatOpenAI(model="gpt-4", openai_api_key="...")
```

Requires `langchain-openai` package and API key.

### Q: How do I handle large documents?

**A**: For 1000+ page documents:
1. Split before adding to system
2. Use smaller chunks:
   ```python
   CHUNK_SIZE = 500
   CHUNK_OVERLAP = 100
   ```
3. Increase retrieval count
4. Consider preprocessing (remove boilerplate, etc)

### Q: Can I use multiple vector stores?

**A**: Currently no, but possible to add:
1. Create separate `ChromaVectorStore` instances with different paths
2. Route queries to appropriate store
3. Aggregate results

### Q: How do I export/backup the vector database?

**A**: Simple copy:
```bash
# Copy the entire directory
cp -r chroma_db chroma_db_backup
```

Chromadb stores everything as files, so regular file backup works.

### Q: Production deployment recommendations?

**A**: Consider:
1. **API Server**: Wrap with FastAPI
2. **Containerization**: Docker for consistency
3. **Persistence**: Use managed vector DB (Pinecone, Weaviate)
4. **Monitoring**: Add logging, metrics, alerts
5. **Security**: API authentication, input validation
6. **Scaling**: Batch processing for large document sets
7. **Testing**: Unit + integration tests

See advanced_examples.py for code patterns.

### Q: How to add conversation memory?

**A**: Extend RAGPipeline:
```python
from langchain.memory import ConversationBufferMemory

class ConversationalRAG(RAGPipeline):
    def __init__(self):
        super().__init__()
        self.memory = ConversationBufferMemory()
    
    def query_with_history(self, question):
        # Use memory in prompt
        context = self.memory.buffer
        # ... generate answer ...
        self.memory.save_context({"input": question}, {"output": answer})
```

### Q: How to evaluate quality?

**A**: Use RAGAS framework:
```bash
pip install ragas
```

Then evaluate your questions/answers/contexts.

### Q: Performance tuning tips?

**A**: Priority order for optimization:
1. GPU acceleration (biggest impact)
2. Smaller models
3. Caching/memoization
4. Batch processing
5. Async operations

Benchmark with `time` before/after changes.

## Getting Help

1. **Check logs**: Enable DEBUG logging
   ```python
   LOG_LEVEL = "DEBUG"
   ```

2. **Reproduce issue**: Test with `documents/sample.txt`

3. **Examine stack traces**: Full error context in logs

4. **Check document format**: Verify PDFs, DOCX, PPTX are valid

5. **Test components separately**:
   ```python
   # Test each module independently
   from src.embeddings_setup import initialize_embeddings
   embeddings = initialize_embeddings()  # Works?
   ```

## Performance Benchmarks

Typical times (on CPU, M1 Mac):

| Operation | Time |
|-----------|------|
| Model download (first time) | ~30s |
| Initialize embeddings | ~5s |
| Index 10 documents | ~20s |
| Single query | ~3-5s |
| Interactive mode startup | ~10s |

Times improve significantly with GPU.

## Resource Requirements

| Component | Size | Memory |
|-----------|------|--------|
| all-MiniLM-L6-v2 | ~80MB | ~150MB |
| flan-t5-base | ~990MB | ~2GB |
| Chroma overhead | minimal | <100MB |
| **Total** | **~1GB** | **~2.5GB** |

GPU: 4GB+ recommended for fast inference
