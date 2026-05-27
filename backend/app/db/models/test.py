import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.question import Question
    from app.db.models.specialty import Specialty


class TestType(str, enum.Enum):
    """Test type enumeration."""

    GENERAL = "general"
    SPECIALIZED = "specialized"


class Test(Base):
    """Test model representing a collection of questions."""

    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    test_type: Mapped[TestType] = mapped_column(Enum(TestType), nullable=False)
    specialty_id: Mapped[int | None] = mapped_column(ForeignKey("specialties.id"))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    specialty: Mapped["Specialty | None"] = relationship()
    questions: Mapped[list["Question"]] = relationship(
        back_populates="test", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"{self.title}"
