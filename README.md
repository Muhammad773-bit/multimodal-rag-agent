# Multimodal Rag Agent

Retrieval-augmented generation over PDF, DOCX and PPTX files, built following LangChain best practices: config management, multi-format loaders, sentence-transformer embeddings, a persisted Chroma store and a CLI.

**Tech:** Python, LangChain, ChromaDB, sentence-transformers, Hugging Face

## Run it

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py --index
python main.py --query "Your question"
```

API keys are read from environment variables. Copy `.env.example` to `.env` and fill in your own keys.

---
By [Muhammad Ali](https://muhammad773-bit.github.io), BS Artificial Intelligence, SMIU Karachi.

## Original notes

# Multi-Document RAG Agent

A production-ready Retrieval-Augmented Generation system built with LangChain, following official best practices.

## Features

- **Multi-format Document Support**: PDF, DOCX, PPTX
- **Vector Database**: Chroma for semantic search
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: Hugging Face (google/flan-t5-base)
- **CLI Interface**: No UI, practice-focused

## Project Structure

```
multimodel_rag/
├── src/
│   ├── config.py           # Configuration management
│   ├── document_loader.py   # Multi-format document loading
│   ├── embeddings_setup.py  # Embeddings initialization
│   ├── vector_store.py      # Chroma vector database setup
│   ├── rag_pipeline.py      # RAG chain construction
│   └── cli.py               # Command-line interface
├── documents/               # Document storage
├── chroma_db/               # Vector database persistence
└── main.py                  # Entry point
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your documents in the `documents/` folder (PDF, DOCX, PPTX).

3. Run the RAG agent:
```bash
python main.py
```

## CLI Commands

```bash
# Index all documents
python main.py --index

# Ask a question
python main.py --query "Your question here"

# Show indexed documents
python main.py --list-documents

# Clear vector database
python main.py --reset-db
```

## LangChain Best Practices Applied

✓ Separated concerns (loaders, embeddings, stores, chains)
✓ Configuration management
✓ Proper memory/context management
✓ Error handling
✓ Logging
✓ Modular architecture
