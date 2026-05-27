from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.question import Question


class Answer(Base):
    """Answer option for a question with weights for all specialties."""

    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Multi-dimensional weights: {"F1": 10, "F2": 5, "F3": 0, ...}
    weights: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Legacy single weight field (deprecated, kept for backward compatibility)
    weight: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    question: Mapped["Question"] = relationship(back_populates="answers")

    def __repr__(self) -> str:
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"{preview} (веси: {self.weights})"
