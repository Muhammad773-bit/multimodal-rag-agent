# LangChain Multi-Document RAG Agent - Quick Start

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Step 1: Install Dependencies

```bash
cd d:\multimodel_rag
pip install -r requirements.txt
```

**Note**: This will download:
- LangChain ecosystem packages
- sentence-transformers model (~350MB)
- Hugging Face transformers & torch
- Document processing libraries

### Step 2: Prepare Documents

Place your documents in the `documents/` folder:
```
documents/
├── report.pdf
├── guide.docx
└── presentation.pptx
```

Supported formats:
- **.pdf** - PDF documents
- **.docx** - Microsoft Word documents  
- **.pptx** - PowerPoint presentations

### Step 3: Index Documents

```bash
python main.py --index
```

This will:
1. Load all documents from `documents/`
2. Split into semantic chunks
3. Generate embeddings
4. Store in Chroma database

## 📖 Usage

### Command-Line Interface

```bash
# Index all documents
python main.py --index

# Ask a question
python main.py --query "What is machine learning?"

# List indexed documents
python main.py --list-documents

# Interactive mode (continuous questioning)
python main.py --interactive

# Clear vector database
python main.py --reset-db
```

### Programmatic Usage

```python
from src.document_loader import get_document_loader
from src.vector_store import get_vector_store
from src.rag_pipeline import get_rag_pipeline

# Load and index documents
loader = get_document_loader()
documents = loader.load_all_documents()

vector_store = get_vector_store()
vector_store.add_documents(documents)

# Ask a question
rag = get_rag_pipeline()
answer = rag.query("What is in these documents?")
print(answer)

# Get answer with sources
result = rag.query_with_sources("What is in these documents?")
print(result["answer"])
print(result["sources"])
```

## 🏗️ Architecture

### Core Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized configuration management |
| `document_loader.py` | Multi-format document loading & chunking |
| `embeddings_setup.py` | HuggingFace embeddings initialization |
| `vector_store.py` | Chroma database operations |
| `rag_pipeline.py` | RAG chain construction & querying |
| `cli.py` | Command-line interface |

### Data Flow

```
User Documents (PDF/DOCX/PPTX)
        ↓
  Document Loader
        ↓
  Text Splitting (Chunks)
        ↓
  Embeddings (all-MiniLM-L6-v2)
        ↓
  Chroma Vector Store
        ↓
  User Query → Semantic Search → LLM (flan-t5-base)
        ↓
     Answer
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Embeddings
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
EMBEDDINGS_DEVICE = "cpu"  # or "cuda"

# LLM
LLM_MODEL_ID = "google/flan-t5-base"
LLM_TEMPERATURE = 0.7

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval
RETRIEVAL_K = 4  # Number of documents to retrieve
```

## 🔍 LangChain Best Practices Implemented

✓ **Modular Architecture**: Each concern separated into dedicated modules
✓ **Configuration Management**: Centralized settings via `config.py`
✓ **Lazy Loading**: Expensive resources (LLM, embeddings) loaded on demand
✓ **Error Handling**: Comprehensive try-catch with logging
✓ **Logging**: Detailed logging at all levels
✓ **LCEL**: Modern LangChain Expression Language for chain composition
✓ **Metadata Preservation**: Document source tracking
✓ **Batch Processing**: Efficient document addition to vector store
✓ **Retriever Pattern**: Standard LangChain retriever interface
✓ **Prompt Engineering**: Structured system prompts for better answers

## 🧪 Testing

### Test with Sample Document

The system includes `documents/sample.txt` for testing.

1. Index it:
   ```bash
   python main.py --index
   ```

2. Ask questions:
   ```bash
   python main.py --query "What formats does this system support?"
   python main.py --query "What is the architecture of the RAG system?"
   ```

### Test Programmatic API

```bash
python example_usage.py
```

## 🔧 Troubleshooting

### Issue: "No documents found"
- Ensure documents are in `documents/` folder
- Check file extensions (.pdf, .docx, .pptx)

### Issue: Out of memory
- Reduce CHUNK_SIZE in config.py
- Use CPU instead of GPU (EMBEDDINGS_DEVICE = "cpu")

### Issue: Slow embeddings
- First run downloads models (~350MB)
- Subsequent runs are faster (loaded from cache)

### Issue: Poor answers
- Add more documents to corpus
- Adjust CHUNK_SIZE and CHUNK_OVERLAP
- Try different LLM models

## 📚 Further Customization

### Change Embeddings Model

In `src/config.py`:
```python
EMBEDDINGS_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Larger model
# or
EMBEDDINGS_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v2"  # Multilingual
```

### Change LLM Model

In `src/config.py`:
```python
LLM_MODEL_ID = "google/flan-t5-large"  # Larger model
# or
LLM_MODEL_ID = "facebook/opt-350m"  # Different model
```

### Modify System Prompt

In `src/rag_pipeline.py`, edit `SYSTEM_PROMPT` to customize response style.

## 📝 License

This project is for practice and learning purposes.

## 🤝 Contributing

To improve the system:
1. Add support for more document formats
2. Implement semantic caching
3. Add conversation memory
4. Support for multiple vector stores
5. Performance optimization
