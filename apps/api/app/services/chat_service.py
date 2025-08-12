"""Chat service for managing conversations and messages."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.chat import Chat, Message
from app.models.user import User

logger = get_logger(__name__)


class ChatService:
    """Service for managing chat conversations and messages."""

    async def save_chat(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        response: Dict[str, Any],
        model: str,
        provider: str,
        db: Optional[AsyncSession] = None,
    ) -> Chat:
        """Save a chat conversation to the database."""
        try:
            # Generate chat title from first user message
            title = self._generate_chat_title(messages)

            # Create chat record
            chat = Chat(
                user_id=int(user_id),
                title=title,
                model=model,
                provider=provider,
            )

            if db:
                db.add(chat)
                await db.flush()  # Get the chat ID

                # Save messages
                await self._save_messages(chat.id, messages, response, db)

                await db.commit()
                logger.info("Chat saved successfully", chat_id=chat.id, user_id=user_id)

            return chat

        except Exception as e:
            logger.error("Failed to save chat", error=str(e), user_id=user_id)
            if db:
                await db.rollback()
            raise

    async def _save_messages(
        self,
        chat_id: int,
        messages: List[Dict[str, str]],
        response: Dict[str, Any],
        db: AsyncSession,
    ) -> None:
        """Save messages for a chat."""
        try:
            # Save user messages
            for message in messages:
                if message["role"] != "assistant":  # Skip assistant messages from input
                    db_message = Message(
                        chat_id=chat_id,
                        role=message["role"],
                        content=message["content"],
                    )
                    db.add(db_message)

            # Save assistant response
            assistant_content = response.get("content", "")
            if assistant_content:
                assistant_message = Message(
                    chat_id=chat_id,
                    role="assistant",
                    content=assistant_content,
                    tokens_used=response.get("usage", {}).get("completion_tokens"),
                    model=response.get("model"),
                )
                db.add(assistant_message)

        except Exception as e:
            logger.error("Failed to save messages", error=str(e), chat_id=chat_id)
            raise

    def _generate_chat_title(self, messages: List[Dict[str, str]]) -> str:
        """Generate a title for the chat from the first user message."""
        for message in messages:
            if message["role"] == "user":
                content = message["content"]
                # Truncate to 50 characters for title
                return content[:50] + "..." if len(content) > 50 else content
        return "New Chat"

    async def get_user_chats(
        self,
        user_id: str,
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get chat history for a user."""
        try:
            query = (
                select(Chat)
                .where(Chat.user_id == int(user_id))
                .order_by(Chat.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await db.execute(query)
            chats = result.scalars().all()

            return [
                {
                    "id": chat.id,
                    "title": chat.title,
                    "model": chat.model,
                    "provider": chat.provider,
                    "created_at": chat.created_at.isoformat(),
                    "updated_at": chat.updated_at.isoformat(),
                }
                for chat in chats
            ]

        except Exception as e:
            logger.error("Failed to get user chats", error=str(e), user_id=user_id)
            raise

    async def get_chat_messages(
        self,
        chat_id: int,
        user_id: str,
        db: AsyncSession,
    ) -> List[Dict[str, Any]]:
        """Get messages for a specific chat."""
        try:
            # Verify chat belongs to user
            chat_query = select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == int(user_id)
            )
            chat_result = await db.execute(chat_query)
            chat = chat_result.scalar_one_or_none()

            if not chat:
                raise ValueError("Chat not found or access denied")

            # Get messages
            messages_query = (
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.asc())
            )

            messages_result = await db.execute(messages_query)
            messages = messages_result.scalars().all()

            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ]

        except Exception as e:
            logger.error("Failed to get chat messages", error=str(e), chat_id=chat_id)
            raise

    async def delete_chat(
        self,
        chat_id: int,
        user_id: str,
        db: AsyncSession,
    ) -> bool:
        """Delete a chat and all its messages."""
        try:
            # Verify chat belongs to user
            chat_query = select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == int(user_id)
            )
            chat_result = await db.execute(chat_query)
            chat = chat_result.scalar_one_or_none()

            if not chat:
                return False

            # Delete chat (messages will be deleted via cascade)
            await db.delete(chat)
            await db.commit()

            logger.info("Chat deleted successfully", chat_id=chat_id, user_id=user_id)
            return True

        except Exception as e:
            logger.error("Failed to delete chat", error=str(e), chat_id=chat_id)
            await db.rollback()
            raise

    async def get_chat_stats(
        self,
        user_id: str,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """Get chat statistics for a user."""
        try:
            # Count total chats
            chats_query = select(Chat).where(Chat.user_id == int(user_id))
            chats_result = await db.execute(chats_query)
            total_chats = len(chats_result.scalars().all())

            # Count total messages
            messages_query = (
                select(Message)
                .join(Chat)
                .where(Chat.user_id == int(user_id))
            )
            messages_result = await db.execute(messages_query)
            total_messages = len(messages_result.scalars().all())

            # Get most used models
            models_query = (
                select(Chat.model, Chat.provider)
                .where(Chat.user_id == int(user_id))
                .group_by(Chat.model, Chat.provider)
            )
            models_result = await db.execute(models_query)
            models = models_result.all()

            return {
                "total_chats": total_chats,
                "total_messages": total_messages,
                "models_used": [{"model": m[0], "provider": m[1]} for m in models],
            }

        except Exception as e:
            logger.error("Failed to get chat stats", error=str(e), user_id=user_id)
            raise
