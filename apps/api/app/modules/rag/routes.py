"""RAG module routes for document ingestion and search."""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.core.security import extract_user_from_token
from app.modules.rag.vector_store import VectorStore

logger = get_logger(__name__)
router = APIRouter()


class DocumentIngestRequest(BaseModel):
    """Document ingestion request model."""
    documents: List[str] = Field(..., description="List of document texts")
    metadatas: List[Dict[str, Any]] = Field(default=[], description="Document metadata")
    collection_name: str = Field(default="documents", description="Collection name")


class DocumentSearchRequest(BaseModel):
    """Document search request model."""
    query: str = Field(..., description="Search query")
    n_results: int = Field(default=5, ge=1, le=20, description="Number of results")
    filter_metadata: Dict[str, Any] = Field(default={}, description="Filter by metadata")


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float | None = None


@router.post("/ingest")
async def ingest_documents(
    request: DocumentIngestRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Ingest documents into the vector store."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize vector store
        vector_store = VectorStore()

        # Create collection if specified
        if request.collection_name != "documents":
            vector_store.create_collection(request.collection_name)

        # Add documents
        ids = vector_store.add_documents(
            documents=request.documents,
            metadatas=request.metadatas if request.metadatas else None,
        )

        logger.info(
            "Documents ingested",
            count=len(request.documents),
            user_id=user.get("user_id"),
        )

        return {
            "status": "success",
            "message": f"Ingested {len(request.documents)} documents",
            "document_ids": ids,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to ingest documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest documents",
        )


@router.post("/search", response_model=List[DocumentResponse])
async def search_documents(
    request: DocumentSearchRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> List[DocumentResponse]:
    """Search for documents in the vector store."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize vector store
        vector_store = VectorStore()

        # Search documents
        results = vector_store.search(
            query=request.query,
            n_results=request.n_results,
            filter_metadata=request.filter_metadata if request.filter_metadata else None,
        )

        logger.info(
            "Document search completed",
            query=request.query,
            results_count=len(results),
            user_id=user.get("user_id"),
        )

        return [
            DocumentResponse(
                id=result["id"],
                document=result["document"],
                metadata=result["metadata"],
                distance=result["distance"],
            )
            for result in results
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to search documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents",
        )


@router.get("/collections")
async def list_collections(
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """List all available collections."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize vector store
        vector_store = VectorStore()

        # List collections
        collections = vector_store.list_collections()

        return {
            "collections": collections,
            "count": len(collections),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list collections", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list collections",
        )


@router.get("/collections/{collection_name}")
async def get_collection_info(
    collection_name: str,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Get information about a specific collection."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize vector store
        vector_store = VectorStore()

        # Create/get collection
        vector_store.create_collection(collection_name)

        # Get collection info
        info = vector_store.get_collection_info()

        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get collection info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get collection info",
        )


@router.delete("/documents")
async def delete_documents(
    document_ids: List[str],
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Delete documents from the vector store."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize vector store
        vector_store = VectorStore()

        # Delete documents
        vector_store.delete_documents(document_ids)

        logger.info(
            "Documents deleted",
            count=len(document_ids),
            user_id=user.get("user_id"),
        )

        return {
            "status": "success",
            "message": f"Deleted {len(document_ids)} documents",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete documents",
        )


@router.get("/health")
async def rag_health() -> Dict[str, Any]:
    """Check RAG module health status."""
    try:
        vector_store = VectorStore()

        if not vector_store.client:
            return {
                "status": "unhealthy",
                "error": "ChromaDB client not initialized",
            }

        # Test connection
        collections = vector_store.list_collections()

        return {
            "status": "healthy",
            "collections_count": len(collections),
            "chroma_host": settings.CHROMA_HOST,
            "chroma_port": settings.CHROMA_PORT,
        }

    except Exception as e:
        logger.error("RAG health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
        }
