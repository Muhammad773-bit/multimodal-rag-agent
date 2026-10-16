# System Architecture Diagrams

## 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-DOCUMENT RAG AGENT                     │
│                    (LangChain + Chroma + Hugging Face)          │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐           ┌──────────────────────┐
    │   User Input    │           │  Vector Database     │
    │                 │           │  (Chroma)            │
    │ - Documents     │           │                      │
    │ - Questions     │           │ - Embeddings         │
    └────────┬────────┘           │ - Documents          │
             │                    │ - Metadata           │
             │                    └──────────────────────┘
             │
    ┌────────▼────────────────────────────┐
    │    LANGCHAIN ORCHESTRATION          │
    ├────────────────────────────────────┤
    │ 1. Document Loading (PDF/DOCX/PPTX)│
    │ 2. Text Splitting (Chunking)       │
    │ 3. Embedding Generation (HF)       │
    │ 4. Vector Store Indexing (Chroma)  │
    │ 5. Semantic Retrieval              │
    │ 6. LLM Inference (flan-t5-base)    │
    │ 7. Answer Generation               │
    └────────┬────────────────────────────┘
             │
    ┌────────▼──────────────────┐
    │    User Output             │
    │                            │
    │ - Answer                   │
    │ - Source Documents         │
    │ - Relevance Scores         │
    └────────────────────────────┘
```

## 2. Indexing Pipeline

```
📄 INPUT: Raw Documents
│
├─ PDF Files
├─ Word Documents (.docx)
└─ PowerPoint Files (.pptx)
│
▼
┌──────────────────────────────────┐
│   MultiFormatDocumentLoader      │
│  - PyPDFLoader                   │
│  - Docx2txtLoader                │
│  - UnstructuredPowerPointLoader   │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  RecursiveCharacterTextSplitter  │
│  - Chunk Size: 1000 chars        │
│  - Overlap: 200 chars            │
│  - Preserve boundaries           │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ HuggingFaceEmbeddings            │
│ Model: all-MiniLM-L6-v2          │
│ Output: 384-dimensional vectors  │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│   ChromaVectorStore              │
│  - Store embeddings              │
│  - Add metadata                  │
│  - Persist to disk               │
└──────────┬───────────────────────┘
           │
           ▼
💾 OUTPUT: Vector Database (Persistent)
   - embeddings.parquet
   - metadata.parquet
   - index/
   - documents/
```

## 3. Query/Retrieval Pipeline

```
❓ INPUT: User Question
│
▼
┌──────────────────────────────┐
│ Question Embedding           │
│ (same model as documents)    │
│ Output: 384-dim vector       │
└──────────┬──────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Vector Similarity Search         │
│ (Chroma: k=4 documents)          │
│ Returns top-k most similar docs  │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Format Retrieved Documents       │
│ - Extract page content           │
│ - Add source attribution         │
│ - Combine into context string    │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Build Prompt                     │
│ Template:                        │
│ "Context: {documents}            │
│  Question: {user_question}       │
│  Answer:"                        │
└──────────┬──────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ LLM Inference                    │
│ Model: google/flan-t5-base       │
│ Process: text2text-generation    │
│ Max Length: 512 tokens           │
└──────────┬──────────────────────┘
           │
           ▼
✅ OUTPUT: Answer with Sources
   - Generated text
   - Source documents
   - Relevance scores
   - Processing metadata
```

## 4. Module Dependencies

```
                    ┌─────────┐
                    │ config  │◄────────────────┐
                    └────┬────┘                 │
                         │                      │
        ┌────────────────┼────────────────┐    │
        │                │                │    │
        ▼                ▼                ▼    │
    ┌─────────┐  ┌─────────────┐  ┌──────────┐│
    │document │  │  embeddings │  │ cli      ││
    │ loader  │  │  setup      │  │ (needs  ││
    └────┬────┘  └─────┬───────┘  │all mods)││
         │              │          └────┬─────┘
         │              │               │
         └──────┬───────┼───────┬───────┘
                │       │       │
                ▼       ▼       ▼
         ┌────────────────────────┐
         │   vector store         │
         │   (uses both above)    │
         └────────┬───────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │   rag pipeline         │
         │   (orchestrates all)   │
         └────────┬───────────────┘
                  │
                  ▼
           READY FOR QUERIES
```

## 5. LCEL Chain Structure

```
┌─────────────────────────────────────────────────────────┐
│              LCEL Chain Composition                      │
└─────────────────────────────────────────────────────────┘

    ╔═════════════════════════════════════════╗
    ║       Input: User Question              ║
    ╚════════════════╤═══════════════════════╝
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  RunnablePassthrough()               │
    │  (pass question unchanged)           │
    └─────────────────────────────────────┘
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║      Retriever: Vector Search          ║
    ║      k=4 documents                     ║
    ║      Returns: List[Document]           ║
    ╚════════════════╤═══════════════════════╝
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  format_docs()                       │
    │  (extract content, add metadata)     │
    └─────────────────────────────────────┘
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  Dict: {"context": str, ...}          ║
    ║        {"question": str}              ║
    ╚════════════════╤═══════════════════════╝
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  PromptTemplate                      │
    │  Fills: context + question           │
    └─────────────────────────────────────┘
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║   HuggingFacePipeline (LLM)            ║
    ║   Model: google/flan-t5-base           ║
    ║   Task: text2text-generation           ║
    ╚════════════════╤═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║       Output: Generated Answer         ║
    ╚════════════════════════════════════════╝
```

## 6. Configuration Hierarchy

```
┌──────────────────────────────────────────────┐
│  RAGConfig (src/config.py)                   │
├──────────────────────────────────────────────┤
│                                              │
│  PATHS:                                      │
│  ├─ PROJECT_ROOT                            │
│  ├─ DOCUMENTS_DIR                           │
│  └─ CHROMA_DB_DIR                           │
│                                              │
│  MODELS:                                     │
│  ├─ EMBEDDINGS_MODEL                        │
│  ├─ EMBEDDINGS_DEVICE                       │
│  ├─ LLM_MODEL_ID                            │
│  └─ LLM_DEVICE                              │
│                                              │
│  PROCESSING:                                 │
│  ├─ CHUNK_SIZE                              │
│  ├─ CHUNK_OVERLAP                           │
│  ├─ SUPPORTED_FORMATS                       │
│  └─ RETRIEVAL_K                             │
│                                              │
│  QUALITY:                                    │
│  ├─ LLM_TEMPERATURE                         │
│  ├─ LLM_MAX_LENGTH                          │
│  ├─ RETRIEVAL_SCORE_THRESHOLD               │
│  └─ LOG_LEVEL                               │
│                                              │
└──────────────────────────────────────────────┘
         │
         │ Used by all modules
         │
    ┌────┴───────────────────────┐
    │                             │
    ▼                             ▼
All Core Modules            CLI Interface
```

## 7. Data Types Flow

```
Input Document
│
└─ str (file path)
   │
   ▼
   Document (Pydantic)
   ├─ page_content: str
   └─ metadata: dict
      ├─ source_file: str
      └─ file_type: str
   │
   ▼
   Split Documents (List[Document])
   ├─ Each chunk:
   │  ├─ page_content: str (1000 chars)
   │  └─ metadata: dict (with source)
   │
   ▼
   Embeddings (List[float])
   ├─ Dimension: 384
   └─ Normalized vectors
   │
   ▼
   Chroma Collection
   ├─ IDs: str
   ├─ Embeddings: List[List[float]]
   ├─ Metadatas: List[dict]
   └─ Documents: List[str]
   │
   ▼
Output Answer
├─ text: str (generated answer)
├─ sources: List[dict] (retrieved docs)
└─ scores: List[float] (relevance scores)
```

## 8. Error Handling Flow

```
Operation Attempted
│
├─ Try
│  ├─ Execute operation
│  │  │
│  │  └─ On Success
│  │     └─ Return result
│  │
│  └─ Catch Exception
│     │
│     ├─ Log Error (logger.error)
│     │
│     ├─ Return Safe Default
│     │  ├─ Empty list []
│     │  ├─ Empty dict {}
│     │  ├─ Empty string ""
│     │  └─ Or safe fallback
│     │
│     └─ Continue Execution
│        (don't crash entire system)
│
└─ User Sees
   ├─ Helpful error message
   ├─ Log entry for debugging
   └─ System continues running
```

## 9. Performance Characteristics

```
Operation                Time (CPU)    Time (GPU)    Scaling
────────────────────────────────────────────────────────────
Model Download (1st)     5-10 min      5-10 min      One-time
Initialize Embeddings    5s            2s            Per session
Load Document (10)       10s           5s            Linear
Chunk Document (10)      5s            5s            Linear
Index Documents          20-30s        5-10s         Linear
Generate Embeddings      20s           2s            Linear
Vector Search            1-2s          <1s           Log(N)
LLM Inference (avg)      3-5s          1-2s          Constant

Legend:
CPU = 4-core CPU
GPU = NVIDIA GPU with CUDA
Linear = time ∝ documents
Log(N) = time ∝ log(N) documents
Constant = time independent of documents
```

## 10. Deployment Architecture Options

```
Option 1: CLI (Current)
┌─────────────────────────────────────────┐
│  Python Script                          │
│  ├─ main.py                             │
│  └─ CLI Interface (argparse)            │
│                                         │
│  ✓ Simple                               │
│  ✓ No dependencies                      │
│  ✗ Single user                          │
└─────────────────────────────────────────┘

Option 2: FastAPI Web Service
┌─────────────────────────────────────────┐
│  FastAPI Server                         │
│  ├─ HTTP API endpoints                  │
│  └─ JSON request/response               │
│                                         │
│  ✓ Multi-user                           │
│  ✓ REST API                             │
│  ✗ Requires deployment                  │
└─────────────────────────────────────────┘

Option 3: Docker Container
┌─────────────────────────────────────────┐
│  Docker Container                       │
│  ├─ Isolated environment                │
│  ├─ Reproducible deployment             │
│  └─ Easy scaling                        │
│                                         │
│  ✓ Reproducible                         │
│  ✓ Scalable                             │
│  ✗ Container overhead                   │
└─────────────────────────────────────────┘

Option 4: Kubernetes Cluster
┌─────────────────────────────────────────┐
│  Kubernetes (K8s)                       │
│  ├─ Multiple pods                       │
│  ├─ Load balancing                      │
│  ├─ Auto-scaling                        │
│  └─ Service mesh                        │
│                                         │
│  ✓ Enterprise-scale                     │
│  ✓ High availability                    │
│  ✗ Complex setup                        │
└─────────────────────────────────────────┘
```

---

These diagrams visualize the complete system architecture, data flow, and design patterns used in the Multi-Document RAG Agent implementation.
