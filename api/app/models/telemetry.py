from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, bigint_pk, created_at_col
from app.models.catalog import EMBEDDING_DIM
from app.models.enums import EventType, SearchType, pg_enum


class UserEvent(Base):
    """Behaviour telemetry (M5). user_id is nulled on account deletion (RODO anonymisation)."""

    __tablename__ = "user_events"

    id: Mapped[bigint_pk]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    session_token: Mapped[Optional[str]] = mapped_column(String(128))
    event_type: Mapped[EventType] = mapped_column(pg_enum(EventType, "event_type"))
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL")
    )
    variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    # "metadata" is reserved by SQLAlchemy's declarative API, hence the attribute alias.
    event_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)
    source: Mapped[Optional[str]] = mapped_column(String(50))  # algorithm that showed the item
    created_at: Mapped[created_at_col]

    __table_args__ = (
        Index("ix_user_events_user_created", "user_id", "created_at"),
        Index("ix_user_events_session_created", "session_token", "created_at"),
        Index("ix_user_events_product_type", "product_id", "event_type"),
    )


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[bigint_pk]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    session_token: Mapped[Optional[str]] = mapped_column(String(128))
    query_text: Mapped[str] = mapped_column(String(500))
    locale: Mapped[Optional[str]] = mapped_column(String(10))
    results_count: Mapped[Optional[int]]
    clicked_product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL")
    )
    search_type: Mapped[SearchType] = mapped_column(pg_enum(SearchType, "search_type"))
    query_embedding = mapped_column(Vector(EMBEDDING_DIM), nullable=True)  # cache for frequent queries
    created_at: Mapped[created_at_col]

    __table_args__ = (Index("ix_search_queries_query_text", "query_text"),)
