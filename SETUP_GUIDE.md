# Complete Setup Guide

## System Requirements

### Minimum
- Python 3.8 or higher
- 4GB RAM
- 2GB disk space (for models cache)
- Internet connection (for model downloads)

### Recommended
- Python 3.10+
- 8GB+ RAM
- 10GB disk space
- GPU (NVIDIA with CUDA, or Mac with Metal)

### Operating Systems
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

## Step-by-Step Installation

### Step 1: Check Python Version

```bash
python --version
```

Should output Python 3.8 or higher. If not, install from python.org.

### Step 2: Create Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
cd d:\multimodel_rag
pip install -r requirements.txt
```

This will download and install:
- LangChain core and community packages (~50MB)
- Document processors (PyPDF, python-docx, python-pptx) (~10MB)
- Chroma vector database (~20MB)
- sentence-transformers (~80MB on first use)
- PyTorch (~500MB - may take time)
- Transformers (~200MB)

**Total download**: ~800MB to 1.5GB (depends on PyTorch version)

⏱️ **Estimated time**: 10-30 minutes (varies by internet speed)

### Step 5: Verify Installation

```bash
python -c "import langchain; print(f'LangChain version: {langchain.__version__}')"
python -c "import chromadb; print('Chroma: OK')"
python -c "import sentence_transformers; print('Sentence Transformers: OK')"
python -c "import transformers; print('Transformers: OK')"
```

All should print without errors.

## First Run

### 1. Download and Cache Models

The first time you run the system, it will download embeddings and LLM models:

```bash
python main.py --list-documents
```

This will trigger:
- Download embeddings model (~80MB)
- Download LLM model (~990MB for flan-t5-base)

**First run takes 5-10 minutes** as models download to cache.

### 2. Prepare Sample Documents

Add some test documents to the `documents/` folder:

```
documents/
├── sample.txt (already included)
├── report.pdf
├── guide.docx
└── presentation.pptx
```

### 3. Index Documents

```bash
python main.py --index
```

Output:
```
2024-01-26 10:00:00 - __main__ - INFO - ============================================================
2024-01-26 10:00:00 - __main__ - INFO - INDEXING DOCUMENTS
2024-01-26 10:00:00 - __main__ - INFO - ============================================================
2024-01-26 10:00:05 - document_loader - INFO - Loading PDF: ...
...
2024-01-26 10:00:15 - vector_store - INFO - Added 50 document chunks
```

### 4. Ask a Question

```bash
python main.py --query "What is RAG?"
```

Output:
```
============================================================
QUERY: What is RAG?
============================================================

📄 ANSWER:
RAG stands for Retrieval-Augmented Generation. It's a system that...

📚 SOURCES (2):
  1. sample.txt (Unknown)
     RAG combines retrieval and generation...
  2. report.pdf (.pdf)
     The RAG system architecture includes...
```

## Environment Variables (Optional)

Create a `.env` file in the project root:

```
# Logging
LOG_LEVEL=INFO

# Device
EMBEDDINGS_DEVICE=cpu
LLM_DEVICE=-1

# Model cache location (optional)
HF_HOME=/path/to/huggingface/cache
```

Load with:
```bash
# On Windows PowerShell
$env:LOG_LEVEL="DEBUG"
python main.py --index

# On macOS/Linux
export LOG_LEVEL="DEBUG"
python main.py --index
```

## Performance Tuning

### For CPU (Default)

**config.py settings:**
```python
EMBEDDINGS_DEVICE = "cpu"
LLM_DEVICE = -1
CHUNK_SIZE = 500  # Smaller chunks
RETRIEVAL_K = 2   # Fewer documents
```

Expected performance:
- Indexing: 20-30s per 10 documents
- Querying: 3-5s per query

### For GPU (NVIDIA with CUDA)

**Install GPU support:**
```bash
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**config.py settings:**
```python
EMBEDDINGS_DEVICE = "cuda"
LLM_DEVICE = 0  # GPU 0
```

Expected performance:
- Indexing: 5-10s per 10 documents
- Querying: 1-2s per query

### For Apple Silicon (M1/M2/M3)

**PyTorch already optimized**, just set:
```python
EMBEDDINGS_DEVICE = "mps"  # Metal Performance Shaders
```

## Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--interactive"]
```

Build and run:
```bash
docker build -t rag-agent .
docker run -it -v $(pwd)/documents:/app/documents rag-agent
```

## Troubleshooting Installation

### Issue: "ModuleNotFoundError: No module named 'torch'"

**Solution**:
```bash
pip install torch
# Or for GPU:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "ERROR: Could not install packages due to EnvironmentError"

**Solution**: Use a fresh virtual environment:
```bash
deactivate
rm -rf venv
python -m venv venv
# Reactivate and install
```

### Issue: "Collecting langchain_huggingface==0.0.5 ... ERROR"

**Solution**: Version mismatch, use latest:
```bash
pip install langchain langchain_community langchain_huggingface --upgrade
```

### Issue: Slow download speed

**Solution**: Use different mirror:
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

### Issue: "Download timed out"

**Solution**: Increase timeout and retry:
```bash
pip install --default-timeout=1000 -r requirements.txt
```

## Post-Installation Checks

Verify everything works:

```bash
# 1. Test imports
python -c "from src import *; print('Imports: OK')"

# 2. Test CLI help
python main.py --help

# 3. List documents
python main.py --list-documents

# 4. Index documents (with sample.txt)
python main.py --index

# 5. Ask a question
python main.py --query "What is this project about?"

# 6. Interactive mode
echo "What is RAG?" | python main.py --interactive
```

All should complete without errors.

## Project Structure After Setup

```
d:\multimodel_rag\
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── document_loader.py
│   ├── embeddings_setup.py
│   ├── vector_store.py
│   ├── rag_pipeline.py
│   └── cli.py
├── documents/
│   └── sample.txt
├── chroma_db/               # Created after first index
│   └── ... (vector database files)
├── main.py
├── example_usage.py
├── advanced_examples.py
├── test_rag.py
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── SETUP_GUIDE.md
├── ARCHITECTURE.md
├── BEST_PRACTICES.md
└── TROUBLESHOOTING.md
```

## Next Steps

1. **Read documentation**:
   - [README.md](README.md) - Overview
   - [QUICKSTART.md](QUICKSTART.md) - Quick start
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Design details

2. **Add your documents**:
   - Place PDFs, DOCX, PPTX in `documents/` folder
   - Run `python main.py --index`

3. **Test the system**:
   - `python main.py --interactive`
   - Ask questions about your documents

4. **Customize**:
   - Edit `src/config.py` for your needs
   - Modify prompts in `src/rag_pipeline.py`
   - Extend with your own features

5. **Deploy**:
   - Use as CLI (current)
   - Wrap in FastAPI for web service
   - Containerize with Docker
   - Deploy to cloud (AWS, GCP, Azure)

## Support

For issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Enable DEBUG logging:
   ```python
   # In src/config.py
   LOG_LEVEL = "DEBUG"
   ```
3. Review logs for error messages
4. Test individual components (see TROUBLESHOOTING.md)

## Summary Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` completed
- [ ] Models downloaded (first run)
- [ ] Sample documents indexed
- [ ] Sample query working
- [ ] Documentation read
- [ ] Ready to add custom documents

You're ready to use the RAG system! 🚀
