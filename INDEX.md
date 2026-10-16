# 📑 Project Index & File Reference

## 🎯 Project Overview

**Multi-Document RAG Agent** - A production-ready Retrieval-Augmented Generation system built with LangChain, following official best practices.

---

## 📁 Complete File Structure

```
d:\multimodel_rag\
│
├── 📄 Core Documentation
│   ├── README.md                    # Project overview & features
│   ├── PROJECT_COMPLETION.md        # This project summary
│   ├── QUICKSTART.md                # 5-minute quick start
│   ├── SETUP_GUIDE.md              # Detailed installation guide
│   ├── ARCHITECTURE.md              # Design decisions & patterns
│   ├── BEST_PRACTICES.md           # LangChain best practices
│   └── TROUBLESHOOTING.md          # Common issues & solutions
│
├── 🐍 Core Source Code (src/)
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration management
│   ├── document_loader.py           # Multi-format document loading
│   ├── embeddings_setup.py          # HuggingFace embeddings
│   ├── vector_store.py              # Chroma vector database
│   ├── rag_pipeline.py              # RAG chain (LCEL)
│   └── cli.py                       # Command-line interface
│
├── 📚 Examples & Tests
│   ├── main.py                      # Entry point
│   ├── example_usage.py             # Programmatic API usage
│   ├── advanced_examples.py         # Advanced patterns
│   └── test_rag.py                  # Unit & integration tests
│
├── 📦 Configuration
│   └── requirements.txt              # Python dependencies
│   └── .gitignore                   # Git ignore rules
│
├── 📁 Data Directories
│   ├── documents/                   # User document storage
│   │   └── sample.txt               # Sample document
│   └── chroma_db/                   # Vector database (created after index)
│
└── ⚙️ Project Configuration
    └── .env                         # Environment variables (optional)
```

---

## 📖 Documentation Guide

### For First-Time Users
1. Start: [README.md](README.md) - Overview & features
2. Quick: [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes
3. Setup: [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed installation

### For Developers
1. Architecture: [ARCHITECTURE.md](ARCHITECTURE.md) - Design & patterns
2. Practices: [BEST_PRACTICES.md](BEST_PRACTICES.md) - LangChain patterns
3. Issues: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common problems

### For Production
- [ARCHITECTURE.md](ARCHITECTURE.md) - Scaling considerations
- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Production patterns
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Deployment options

---

## 🔧 Core Modules Reference

### 1. **src/config.py**
**Purpose**: Centralized configuration management

**Key Classes**:
- `RAGConfig` - Configuration holder
- `config` - Singleton instance

**Key Settings**:
- Model choices (embeddings, LLM)
- Device settings (CPU/GPU)
- Chunk sizes and retrieval counts
- Document paths

**Usage**:
```python
from src.config import config
print(config.EMBEDDINGS_MODEL)  # "all-MiniLM-L6-v2"
```

---

### 2. **src/document_loader.py**
**Purpose**: Load and process documents (PDF, DOCX, PPTX)

**Key Classes**:
- `MultiFormatDocumentLoader` - Main loader

**Key Methods**:
- `load_document()` - Load single document
- `load_all_documents()` - Load all in directory
- `load_pdf()`, `load_docx()`, `load_pptx()` - Format-specific

**Usage**:
```python
from src.document_loader import get_document_loader
loader = get_document_loader()
docs = loader.load_all_documents()
```

---

### 3. **src/embeddings_setup.py**
**Purpose**: Initialize and manage embeddings model

**Key Functions**:
- `initialize_embeddings()` - Create embeddings instance
- `get_embeddings()` - Get or create (lazy loading)

**Technology**: HuggingFaceEmbeddings (sentence-transformers)

**Usage**:
```python
from src.embeddings_setup import get_embeddings
embeddings = get_embeddings()
vector = embeddings.embed_query("test")
```

---

### 4. **src/vector_store.py**
**Purpose**: Manage Chroma vector database

**Key Classes**:
- `ChromaVectorStore` - Vector store manager

**Key Methods**:
- `add_documents()` - Add documents to store
- `search()` - Semantic search
- `search_with_scores()` - Search with relevance scores
- `get_retriever()` - Get LangChain retriever
- `clear()` - Clear all documents

**Usage**:
```python
from src.vector_store import get_vector_store
store = get_vector_store()
docs = store.search("query", k=4)
```

---

### 5. **src/rag_pipeline.py**
**Purpose**: RAG chain construction and inference

**Key Classes**:
- `RAGPipeline` - RAG system manager

**Key Methods**:
- `build_chain()` - Build LCEL chain
- `query()` - Single query
- `query_with_sources()` - Query with source docs

**Technology**: LCEL (LangChain Expression Language)

**Usage**:
```python
from src.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
result = rag.query_with_sources("Question?")
```

---

### 6. **src/cli.py**
**Purpose**: Command-line interface

**Key Classes**:
- `RAGCLI` - CLI manager

**Key Methods**:
- `index_documents()` - Index documents
- `query()` - Single question
- `list_documents()` - Show indexed docs
- `interactive_mode()` - Continuous Q&A
- `reset_database()` - Clear database

**Usage**:
```bash
python main.py --index
python main.py --query "Question?"
python main.py --interactive
```

---

## 🎯 CLI Commands Reference

```bash
# Index all documents
python main.py --index

# Ask a single question
python main.py --query "Your question here"

# Show indexed documents
python main.py --list-documents

# Interactive mode (continuous questions)
python main.py --interactive

# Clear vector database
python main.py --reset-db

# Show help
python main.py --help
```

---

## 🧪 Running Examples

### Example 1: Basic Usage
```bash
# Index sample document
python main.py --index

# Ask a question
python main.py --query "What is RAG?"
```

### Example 2: Interactive Mode
```bash
python main.py --interactive
# Then type questions continuously
```

### Example 3: Programmatic API
```bash
python example_usage.py
```

### Example 4: Advanced Patterns
```bash
python advanced_examples.py
```

### Example 5: Tests
```bash
pip install pytest
python -m pytest test_rag.py -v
```

---

## 🔑 Key Concepts

### RAG (Retrieval-Augmented Generation)
1. **Retrieval**: Find relevant documents for query
2. **Augmentation**: Combine query with retrieved context
3. **Generation**: Use LLM to generate answer

### LCEL (LangChain Expression Language)
Modern syntax for building chains:
```python
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)
```

### Vector Embeddings
Convert text to dense vectors for semantic search:
- Model: all-MiniLM-L6-v2 (384-dimensional)
- Usage: Similarity-based document retrieval

### Chunking Strategy
Split large documents into overlapping chunks:
- Size: 1000 characters (configurable)
- Overlap: 200 characters (for context)
- Strategy: Recursive splitting by separators

---

## ⚙️ Configuration Quick Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| `EMBEDDINGS_MODEL` | `all-MiniLM-L6-v2` | Fast, lightweight embeddings |
| `EMBEDDINGS_DEVICE` | `cpu` | CPU or `cuda` or `mps` |
| `LLM_MODEL_ID` | `google/flan-t5-base` | Instruction-tuned LLM |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Documents to retrieve |
| `LLM_TEMPERATURE` | `0.7` | Creativity vs consistency |

---

## 🚀 Getting Started Checklist

- [ ] Read [README.md](README.md)
- [ ] Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python main.py --index`
- [ ] Run `python main.py --interactive`
- [ ] Add your documents to `documents/` folder
- [ ] Re-index with your documents
- [ ] Customize in [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Deploy using patterns in [BEST_PRACTICES.md](BEST_PRACTICES.md)

---

## 🔗 File Dependencies

```
main.py
  └── src/cli.py
      ├── src/config.py
      ├── src/document_loader.py
      │   └── src/config.py
      ├── src/vector_store.py
      │   ├── src/config.py
      │   └── src/embeddings_setup.py
      └── src/rag_pipeline.py
          ├── src/config.py
          ├── src/vector_store.py
          └── src/embeddings_setup.py
```

**Key Principle**: All modules import from `config.py` for settings

---

## 📊 Data Flow Summary

```
Documents → Loader → Split → Embed → Vector Store → Retriever
                                           ↓
                                      Index (Store)
                                           ↓
                                    Persist to Disk

Query → Embeddings → Vector Search → Retrieved Docs
                                           ↓
                                      Format Context
                                           ↓
                                      Build Prompt
                                           ↓
                                      LLM Inference
                                           ↓
                                        Answer
```

---

## 💾 Resource Requirements

| Component | Size | Memory | Time |
|-----------|------|--------|------|
| all-MiniLM-L6-v2 | 80MB | 150MB | 5s |
| flan-t5-base | 990MB | 2GB | 3-5s per query |
| Chroma overhead | minimal | <100MB | - |
| Sample documents | varies | 10-50MB | 20-30s for 10 docs |
| **Total** | ~1.1GB | ~2.5GB | - |

---

## 🎓 Learning Path

**Level 1: User** (30 minutes)
→ Read README → Setup → Ask questions

**Level 2: Developer** (2 hours)
→ Read ARCHITECTURE → Study source code → Customize config

**Level 3: Advanced** (1 day)
→ Read BEST_PRACTICES → Implement extensions → Deploy

**Level 4: Expert** (1 week)
→ Fine-tune models → Optimize performance → Production deployment

---

## 📞 Quick Reference

### Installation
```bash
pip install -r requirements.txt
```

### Verify Setup
```bash
python -c "from src import *; print('OK')"
```

### Index Documents
```bash
python main.py --index
```

### Query
```bash
python main.py --query "Your question?"
```

### Debug
```python
# In src/config.py
LOG_LEVEL = "DEBUG"
```

---

## 🎉 You're All Set!

This complete implementation includes:
- ✅ Core RAG system (LangChain)
- ✅ Multiple document formats
- ✅ Vector database (Chroma)
- ✅ CLI interface
- ✅ Comprehensive documentation
- ✅ Examples and tests
- ✅ Best practices throughout

**Start with**: `python main.py --help`

**Questions?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Ready to deploy?** See [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Last Updated**: January 26, 2026
**Status**: Production Ready ✅
