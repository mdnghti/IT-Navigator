from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.question import Question


class Specialty(Base):
    """Specialty model representing career directions (F1-F7)."""

    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Relationships
    questions: Mapped[list["Question"]] = relationship(back_populates="specialty")

    def __repr__(self) -> str:
        return f"{self.name} ({self.code})"
