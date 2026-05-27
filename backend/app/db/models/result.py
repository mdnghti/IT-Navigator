from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.test import Test
    from app.db.models.user import User


class TestResult(Base):
    """Test result storing user answers and calculated scores."""

    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="results")
    test: Mapped["Test"] = relationship()
