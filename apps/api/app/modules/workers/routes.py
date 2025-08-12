"""Workers module routes for task management."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.security import extract_user_from_token
from app.modules.workers.celery_app import celery_app
from app.modules.workers.tasks import long_running_task, document_processing_task

logger = get_logger(__name__)
router = APIRouter()


class TaskRequest(BaseModel):
    """Task request model."""
    data: Dict[str, Any]


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    status: str
    message: str


@router.post("/tasks", response_model=TaskResponse)
async def submit_task(
    request: TaskRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> TaskResponse:
    """Submit a background task."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Submit task
        task = long_running_task.delay(request.data)

        logger.info("Task submitted", task_id=task.id, user_id=user.get("user_id"))

        return TaskResponse(
            task_id=task.id,
            status="submitted",
            message="Task submitted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task",
        )


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Get task status and result."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Get task result
        task_result = celery_app.AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "status": task_result.status,
        }

        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.info)
        else:
            response["info"] = task_result.info

        logger.info("Task status retrieved", task_id=task_id, status=task_result.status)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get task status", error=str(e), task_id=task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status",
        )


@router.post("/tasks/document", response_model=TaskResponse)
async def submit_document_task(
    document_url: str,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> TaskResponse:
    """Submit a document processing task."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Submit document processing task
        task = document_processing_task.delay(document_url)

        logger.info("Document task submitted", task_id=task.id, user_id=user.get("user_id"))

        return TaskResponse(
            task_id=task.id,
            status="submitted",
            message="Document processing task submitted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit document task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit document task",
        )


@router.get("/health")
async def workers_health() -> Dict[str, Any]:
    """Check workers health status."""
    try:
        # Check Celery worker status
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active_tasks = inspect.active()

        return {
            "status": "healthy" if stats else "unhealthy",
            "workers": len(stats) if stats else 0,
            "active_tasks": len(active_tasks) if active_tasks else 0,
        }

    except Exception as e:
        logger.error("Workers health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
        }
