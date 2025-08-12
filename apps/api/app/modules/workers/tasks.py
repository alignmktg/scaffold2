"""Celery tasks for background processing."""

import time
from typing import Dict, Any, List

from celery import current_task

from app.core.logging import get_logger
from app.modules.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True)
def long_running_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Example long-running task."""
    try:
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting task..."}
        )

        # Simulate work
        for i in range(10):
            time.sleep(1)  # Simulate work
            progress = (i + 1) * 10

            self.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": f"Processing step {i + 1}/10..."
                }
            )

        logger.info("Long running task completed", task_id=self.request.id)

        return {
            "status": "completed",
            "result": f"Processed data: {data}",
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error("Long running task failed", error=str(e), task_id=self.request.id)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True)
def ai_processing_task(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
    """Background AI processing task."""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Initializing AI processing..."}
        )

        # Import here to avoid circular imports
        from app.services.ai_service import AIService

        ai_service = AIService()

        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing with AI model..."}
        )

        # Get AI response
        response = await ai_service.chat_completion(
            messages=messages,
            model=model,
            provider="openai",
        )

        logger.info("AI processing task completed", task_id=self.request.id)

        return {
            "status": "completed",
            "response": response,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error("AI processing task failed", error=str(e), task_id=self.request.id)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True)
def document_processing_task(self, document_url: str) -> Dict[str, Any]:
    """Background document processing task."""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Downloading document..."}
        )

        # Simulate document processing
        time.sleep(2)

        self.update_state(
            state="PROGRESS",
            meta={"status": "Extracting text..."}
        )

        time.sleep(2)

        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing complete"}
        )

        logger.info("Document processing task completed", task_id=self.request.id)

        return {
            "status": "completed",
            "document_url": document_url,
            "processed": True,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error("Document processing task failed", error=str(e), task_id=self.request.id)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(bind=True)
def email_notification_task(self, user_id: str, message: str) -> Dict[str, Any]:
    """Background email notification task."""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Preparing email..."}
        )

        # Simulate email sending
        time.sleep(1)

        logger.info("Email notification sent", user_id=user_id, task_id=self.request.id)

        return {
            "status": "completed",
            "user_id": user_id,
            "email_sent": True,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error("Email notification task failed", error=str(e), task_id=self.request.id)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
