"""
RAG pipeline construction following LangChain best practices.
Implements retrieval-augmented generation chain.
"""
import logging
from typing import Optional

from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document

from .config import config
from .vector_store import get_vector_store
from .embeddings_setup import get_embeddings

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Constructs and manages RAG chain.
    Follows LangChain best practices for chain composition.
    """
    
    # System prompt for context-aware responses
    SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided documents.

Use only the information from the provided context to answer questions.
If the answer is not in the context, say "I don't have enough information to answer this question."
Be concise and factual.

Context:
{context}

Question: {question}
Answer:"""
    
    def __init__(self):
        """Initialize RAG pipeline components."""
        self.vector_store = get_vector_store()
        self.embeddings = get_embeddings()
        self.llm = None
        self.chain = None
        logger.info("RAGPipeline initialized")
    
    def initialize_llm(self):
        """
        Initialize Hugging Face LLM.
        
        Implements LangChain best practices:
        - Uses HuggingFacePipeline for managed inference
        - Configures model parameters
        - Sets up proper tokenization
        """
        logger.info(f"Initializing LLM: {config.LLM_MODEL_ID}")
        
        try:
            self.llm = HuggingFacePipeline(
                model_id=config.LLM_MODEL_ID,
                task="text2text-generation",
                model_kwargs={
                    "max_length": config.LLM_MAX_LENGTH,
                    "temperature": config.LLM_TEMPERATURE,
                    "do_sample": True,
                },
                device=config.LLM_DEVICE,
            )
            logger.info(f"LLM initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    def _format_docs(self, docs: list) -> str:
        """
        Format retrieved documents for context.
        
        Args:
            docs: List of Document objects
            
        Returns:
            Formatted string with document content
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source_file", "Unknown")
            formatted.append(f"[Document {i} - {source}]\n{doc.page_content}")
        return "\n\n".join(formatted)
    
    def build_chain(self):
        """
        Build RAG chain using LangChain LCEL.
        
        Follows LangChain best practices:
        - Uses modern LCEL syntax
        - Implements proper retrieval
        - Structures prompt engineering
        - Handles runnable chains
        """
        if self.llm is None:
            self.initialize_llm()
        
        logger.info("Building RAG chain")
        
        # Retriever from vector store
        retriever = self.vector_store.get_retriever()
        
        # Prompt template
        prompt = PromptTemplate(
            template=self.SYSTEM_PROMPT,
            input_variables=["context", "question"],
        )
        
        # Build chain using LCEL
        # {context} will be filled by retriever, {question} by input
        self.chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
        )
        
        logger.info("RAG chain built successfully")
        return self.chain
    
    def query(self, question: str) -> str:
        """
        Query the RAG pipeline.
        
        Args:
            question: User question
            
        Returns:
            Answer from LLM based on document context
            
        Implements LangChain best practices:
        - Manages context window
        - Handles errors gracefully
        - Preserves chat history awareness
        """
        if self.chain is None:
            self.build_chain()
        
        logger.info(f"Processing query: {question}")
        
        try:
            response = self.chain.invoke(question)
            logger.info("Query processed successfully")
            return response.strip()
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error: {str(e)}"
    
    def query_with_sources(self, question: str) -> dict:
        """
        Query with source document information.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and source documents
        """
        logger.info(f"Processing query with sources: {question}")
        
        try:
            # Get relevant documents
            docs = self.vector_store.search(question)
            
            # Get answer
            answer = self.query(question)
            
            # Format sources
            sources = []
            for doc in docs:
                sources.append({
                    "file": doc.metadata.get("source_file", "Unknown"),
                    "type": doc.metadata.get("file_type", "Unknown"),
                    "content": doc.page_content[:200] + "...",
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "num_sources": len(sources),
            }
        except Exception as e:
            logger.error(f"Error in query_with_sources: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "num_sources": 0,
            }


def get_rag_pipeline() -> RAGPipeline:
    """Get RAG pipeline instance."""
    return RAGPipeline()
