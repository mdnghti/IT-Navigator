from pydantic import BaseModel, ConfigDict


class AnswerRead(BaseModel):
    """Answer schema for client (without weight)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class QuestionRead(BaseModel):
    """Question schema with answers."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    answers: list[AnswerRead]


class AnswerSubmit(BaseModel):
    """Answer submission from client."""

    question_id: int
    answer_id: int


class TestSubmitRequest(BaseModel):
    """Test submission request."""

    answers: list[AnswerSubmit]


class SpecialtyResult(BaseModel):
    """Result for a single specialty."""

    specialty_code: str
    specialty_name: str
    score: int
    max_score: int
    percentage: float


class TestResultResponse(BaseModel):
    """Test result response with all specialty scores."""

    results: list[SpecialtyResult]
    recommended_specialty: SpecialtyResult | None
    result_id: int


class TestResultRead(BaseModel):
    """Test result for history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    test_id: int
    scores: dict[str, float]
    completed_at: str
    specialty_names: dict[str, str] | None = None


# Admin schemas for test editor

class AnswerAdmin(BaseModel):
    """Answer schema for admin with weights."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    text: str
    weights: dict[str, int]  # {"F1": 10, "F2": 5, ...}
    weight: int = 0  # Legacy field


class AnswerCreate(BaseModel):
    """Create answer schema."""

    text: str
    weights: dict[str, int]
    weight: int = 0


class AnswerUpdate(BaseModel):
    """Update answer schema."""

    text: str | None = None
    weights: dict[str, int] | None = None
    weight: int | None = None


class QuestionAdmin(BaseModel):
    """Question schema for admin with all data."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    text: str
    specialty_id: int
    order: int
    answers: list[AnswerAdmin]


class QuestionCreate(BaseModel):
    """Create question schema."""

    text: str
    specialty_id: int
    order: int
    answers: list[AnswerCreate]


class QuestionUpdate(BaseModel):
    """Update question schema."""

    text: str | None = None
    specialty_id: int | None = None
    order: int | None = None


class TestAdmin(BaseModel):
    """Test schema for admin with all questions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    test_type: str
    specialty_id: int | None
    is_active: bool
    questions: list[QuestionAdmin]


class TestCreate(BaseModel):
    """Create test schema."""

    title: str
    description: str | None = None
    test_type: str
    specialty_id: int | None = None
    is_active: bool = True


class TestUpdate(BaseModel):
    """Update test schema."""

    title: str | None = None
    description: str | None = None
    test_type: str | None = None
    specialty_id: int | None = None
    is_active: bool | None = None

