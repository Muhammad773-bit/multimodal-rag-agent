"""
CLI interface for RAG Agent.
Provides command-line interface for indexing, querying, and managing documents.
"""
import logging
import argparse
import sys
from pathlib import Path

from .config import config
from .document_loader import get_document_loader
from .vector_store import get_vector_store
from .rag_pipeline import get_rag_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RAGCLI:
    """Command-line interface for RAG Agent."""
    
    def __init__(self):
        """Initialize CLI."""
        config.ensure_directories()
        self.document_loader = get_document_loader()
        self.vector_store = get_vector_store()
        self.rag_pipeline = get_rag_pipeline()
    
    def index_documents(self) -> None:
        """Index all documents in documents/ directory."""
        logger.info("=" * 60)
        logger.info("INDEXING DOCUMENTS")
        logger.info("=" * 60)
        
        # Load documents
        documents = self.document_loader.load_all_documents()
        
        if not documents:
            logger.warning(
                f"No documents found in {config.DOCUMENTS_DIR}. "
                "Please add PDF, DOCX, or PPTX files."
            )
            return
        
        # Add to vector store
        doc_ids = self.vector_store.add_documents(documents)
        
        logger.info(f"✓ Indexed {len(doc_ids)} document chunks")
        logger.info(f"Total documents in store: {self.vector_store.document_count()}")
        logger.info("=" * 60)
    
    def query(self, question: str, show_sources: bool = True) -> None:
        """
        Query the RAG pipeline.
        
        Args:
            question: Question to ask
            show_sources: Whether to display source documents
        """
        logger.info("=" * 60)
        logger.info(f"QUERY: {question}")
        logger.info("=" * 60)
        
        # Check if documents are indexed
        if self.vector_store.document_count() == 0:
            logger.warning("No documents indexed. Please run indexing first.")
            print("\n❌ No documents indexed. Run: python main.py --index\n")
            return
        
        if show_sources:
            result = self.rag_pipeline.query_with_sources(question)
            print(f"\n📄 ANSWER:\n{result['answer']}\n")
            
            if result["sources"]:
                print(f"📚 SOURCES ({result['num_sources']}):")
                for i, source in enumerate(result["sources"], 1):
                    print(f"\n  {i}. {source['file']} ({source['type']})")
                    print(f"     {source['content']}")
        else:
            answer = self.rag_pipeline.query(question)
            print(f"\n📄 ANSWER:\n{answer}\n")
        
        logger.info("=" * 60)
    
    def list_documents(self) -> None:
        """List all indexed documents."""
        logger.info("=" * 60)
        logger.info("INDEXED DOCUMENTS")
        logger.info("=" * 60)
        
        count = self.vector_store.document_count()
        
        if count == 0:
            print("\n❌ No documents indexed.\n")
            return
        
        print(f"\n✓ Total chunks indexed: {count}\n")
        
        # List files in documents directory
        doc_files = list(config.DOCUMENTS_DIR.glob("*"))
        supported_files = [
            f for f in doc_files
            if f.suffix.lower() in config.SUPPORTED_FORMATS
        ]
        
        if supported_files:
            print("📄 Supported files in documents/:")
            for i, file in enumerate(supported_files, 1):
                print(f"  {i}. {file.name}")
        
        print()
        logger.info("=" * 60)
    
    def reset_database(self) -> None:
        """Clear the vector database."""
        logger.info("=" * 60)
        logger.info("RESETTING DATABASE")
        logger.info("=" * 60)
        
        confirm = input("⚠️  This will delete all indexed documents. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("✗ Operation cancelled.\n")
            return
        
        self.vector_store.clear()
        print("✓ Vector database cleared.\n")
        logger.info("=" * 60)
    
    def interactive_mode(self) -> None:
        """Run interactive query mode."""
        logger.info("=" * 60)
        logger.info("INTERACTIVE MODE")
        logger.info("=" * 60)
        
        if self.vector_store.document_count() == 0:
            logger.warning("No documents indexed.")
            print("\n❌ No documents indexed. Run: python main.py --index\n")
            return
        
        print("\n💬 Interactive Mode (type 'exit' to quit)\n")
        
        while True:
            try:
                question = input("Your question: ").strip()
                
                if question.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!\n")
                    break
                
                if not question:
                    continue
                
                # Query without logging overhead
                result = self.rag_pipeline.query_with_sources(question)
                print(f"\n📄 Answer:\n{result['answer']}\n")
                
                if result["sources"]:
                    print(f"📚 Sources ({result['num_sources']}):")
                    for source in result["sources"]:
                        print(f"  • {source['file']}")
                
                print()
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!\n")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Multi-Document RAG Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --index                    # Index all documents
  python main.py --query "Your question"    # Ask a question
  python main.py --list-documents           # Show indexed documents
  python main.py --interactive              # Interactive mode
  python main.py --reset-db                 # Clear vector database
        """,
    )
    
    parser.add_argument(
        "--index",
        action="store_true",
        help="Index all documents from documents/ directory",
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Ask a question to the RAG agent",
    )
    parser.add_argument(
        "--list-documents",
        action="store_true",
        help="Show indexed documents",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive mode",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Clear vector database",
    )
    
    args = parser.parse_args()
    cli = RAGCLI()
    
    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Execute commands
    if args.index:
        cli.index_documents()
    
    if args.query:
        cli.query(args.query)
    
    if args.list_documents:
        cli.list_documents()
    
    if args.interactive:
        cli.interactive_mode()
    
    if args.reset_db:
        cli.reset_database()


if __name__ == "__main__":
    main()
