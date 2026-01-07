"""PostgreSQL checkpointer for LangGraph state persistence."""

import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from sqlalchemy import Column, DateTime, String, Text

from app.db.base import Base


class CheckpointModel(Base):
    """SQLAlchemy model for storing checkpoints."""

    __tablename__ = "langgraph_checkpoints"

    thread_id = Column(String(255), primary_key=True)
    checkpoint_id = Column(String(255), primary_key=True)
    parent_id = Column(String(255), nullable=True)
    checkpoint_data = Column(Text, nullable=False)
    metadata_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PostgresCheckpointer(BaseCheckpointSaver):
    """Async PostgreSQL-backed checkpoint saver."""

    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory

    async def aget(self, config: dict[str, Any]) -> Checkpoint | None:
        """Get checkpoint for thread."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        async with self.session_factory() as session:
            result = await session.execute(
                CheckpointModel.__table__.select()
                .where(CheckpointModel.thread_id == thread_id)
                .order_by(CheckpointModel.created_at.desc())
                .limit(1)
            )
            row = result.fetchone()

            if row:
                return json.loads(row.checkpoint_data)
            return None

    async def aget_tuple(self, config: dict[str, Any]) -> CheckpointTuple | None:
        """Get checkpoint tuple with metadata."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        async with self.session_factory() as session:
            result = await session.execute(
                CheckpointModel.__table__.select()
                .where(CheckpointModel.thread_id == thread_id)
                .order_by(CheckpointModel.created_at.desc())
                .limit(1)
            )
            row = result.fetchone()

            if row:
                checkpoint = json.loads(row.checkpoint_data)
                metadata = (
                    json.loads(row.metadata_data) if row.metadata_data else {}
                )
                parent_config = None
                if row.parent_id:
                    parent_config = {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row.parent_id,
                        }
                    }
                return CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row.checkpoint_id,
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=CheckpointMetadata(**metadata),
                    parent_config=parent_config,
                )
            return None

    async def aput(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> dict[str, Any]:
        """Save checkpoint."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id required")

        checkpoint_id = checkpoint.get("id", str(datetime.utcnow().timestamp()))
        parent_id = config.get("configurable", {}).get("checkpoint_id")

        async with self.session_factory() as session:
            # Insert new checkpoint
            stmt = CheckpointModel.__table__.insert().values(
                thread_id=thread_id,
                checkpoint_id=checkpoint_id,
                parent_id=parent_id,
                checkpoint_data=json.dumps(checkpoint),
                metadata_data=json.dumps(metadata) if metadata else None,
            )
            await session.execute(stmt)
            await session.commit()

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def alist(
        self,
        config: dict[str, Any],
        *,
        filter: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints for thread."""
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return

        async with self.session_factory() as session:
            query = (
                CheckpointModel.__table__.select()
                .where(CheckpointModel.thread_id == thread_id)
                .order_by(CheckpointModel.created_at.desc())
            )

            if limit:
                query = query.limit(limit)

            result = await session.execute(query)

            for row in result.fetchall():
                checkpoint = json.loads(row.checkpoint_data)
                metadata = (
                    json.loads(row.metadata_data) if row.metadata_data else {}
                )
                parent_config = None
                if row.parent_id:
                    parent_config = {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row.parent_id,
                        }
                    }
                yield CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_id": row.checkpoint_id,
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=CheckpointMetadata(**metadata),
                    parent_config=parent_config,
                )

    # Sync methods required by base class (delegate to async)
    def get(self, config: dict[str, Any]) -> Checkpoint | None:
        raise NotImplementedError("Use async methods")

    def get_tuple(self, config: dict[str, Any]) -> CheckpointTuple | None:
        raise NotImplementedError("Use async methods")

    def put(
        self,
        config: dict[str, Any],
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> dict[str, Any]:
        raise NotImplementedError("Use async methods")

    def list(
        self,
        config: dict[str, Any],
        *,
        filter: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ):
        raise NotImplementedError("Use async methods")
