"""Vector store service for RAG functionality."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Vector store service for document storage and retrieval."""

    def __init__(self) -> None:
        """Initialize vector store."""
        self.client = None
        self.collection = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize ChromaDB client."""
        try:
            if settings.USE_RAG:
                self.client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                )
                logger.info("ChromaDB client initialized")
            else:
                logger.warning("RAG module not enabled")
        except Exception as e:
            logger.error("Failed to initialize ChromaDB client", error=str(e))
            raise

    def create_collection(self, collection_name: str = "documents") -> None:
        """Create a new collection."""
        try:
            if not self.client:
                raise ValueError("ChromaDB client not initialized")

            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
            logger.info(f"Collection '{collection_name}' created/retrieved")

        except Exception as e:
            logger.error("Failed to create collection", error=str(e))
            raise

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add documents to the vector store."""
        try:
            if not self.collection:
                self.create_collection()

            # Generate IDs if not provided
            if not ids:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]

            # Add documents
            self.collection.add(
                documents=documents,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids,
            )

            logger.info(f"Added {len(documents)} documents to vector store")
            return ids

        except Exception as e:
            logger.error("Failed to add documents", error=str(e))
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            if not self.collection:
                self.create_collection()

            # Perform search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata,
            )

            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                })

            logger.info(f"Search completed, found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error("Failed to search documents", error=str(e))
            raise

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents from the vector store."""
        try:
            if not self.collection:
                raise ValueError("No collection initialized")

            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from vector store")

        except Exception as e:
            logger.error("Failed to delete documents", error=str(e))
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        try:
            if not self.collection:
                return {"error": "No collection initialized"}

            count = self.collection.count()
            return {
                "name": self.collection.name,
                "count": count,
                "metadata": self.collection.metadata,
            }

        except Exception as e:
            logger.error("Failed to get collection info", error=str(e))
            return {"error": str(e)}

    def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            if not self.client:
                return []

            collections = self.client.list_collections()
            return [col.name for col in collections]

        except Exception as e:
            logger.error("Failed to list collections", error=str(e))
            return []
