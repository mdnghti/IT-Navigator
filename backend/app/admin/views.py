from sqladmin import ModelView
from markupsafe import Markup

from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.specialty import Specialty
from app.db.models.test import Test
from app.db.models.user import User


class UserAdmin(ModelView, model=User):
    """Admin view for User model."""

    column_list = [User.id, User.email, User.full_name, User.is_active, User.is_admin]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.id, User.email, User.created_at]
    form_excluded_columns = [User.hashed_password, User.results, User.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class SpecialtyAdmin(ModelView, model=Specialty):
    """Admin view for Specialty model."""

    column_list = [Specialty.id, Specialty.code, Specialty.name]
    column_searchable_list = [Specialty.code, Specialty.name]
    column_sortable_list = [Specialty.id, Specialty.code]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Specialty"
    name_plural = "Specialties"
    icon = "fa-solid fa-graduation-cap"


class AnswerInline(ModelView):
    """Inline view for answers within questions."""
    column_list = [Answer.text, Answer.weight]
    form_columns = [Answer.text, Answer.weight]


class QuestionInline(ModelView):
    """Inline view for questions within tests."""
    column_list = [Question.text, Question.specialty, Question.order]
    form_columns = [Question.text, Question.specialty_id, Question.order]


class TestAdmin(ModelView, model=Test):
    """Admin view for Test model."""

    column_list = [Test.id, Test.title, Test.test_type, Test.specialty, Test.is_active]
    column_searchable_list = [Test.title]
    column_sortable_list = [Test.id, Test.title, Test.created_at]
    form_excluded_columns = [Test.created_at]
    can_create = False  # Disable default create, use custom editor
    can_edit = False  # Disable default edit, use custom editor
    can_delete = True
    name = "Test"
    name_plural = "Tests"
    icon = "fa-solid fa-clipboard-list"

    # Add custom action column with link to editor
    column_formatters = {
        Test.id: lambda m, a: Markup(f'<a href="/admin/test-editor/{m.id}" class="btn btn-sm btn-primary"><i class="fa fa-edit"></i> Редагувати</a>')
    }

    # Override the create button to point to custom editor
    create_template = "sqladmin/create.html"

    @property
    def can_create(self):
        return True

    @property
    def create_url(self):
        return "/admin/test-create"


class QuestionAdmin(ModelView, model=Question):
    """Admin view for Question model."""

    column_list = [Question.id, Question.text, Question.test, Question.specialty, Question.order]
    column_searchable_list = [Question.text]
    column_sortable_list = [Question.id, Question.order]
    form_excluded_columns = [Question.created_at]
    form_ajax_refs = {
        "answers": {
            "fields": ("text", "weight"),
            "order_by": "id",
        }
    }
    can_create = True
    can_edit = True
    can_delete = True
    name = "Question"
    name_plural = "Questions"
    icon = "fa-solid fa-question-circle"


class AnswerAdmin(ModelView, model=Answer):
    """Admin view for Answer model."""

    column_list = [Answer.id, Answer.text, Answer.weight, Answer.question]
    column_searchable_list = [Answer.text]
    column_sortable_list = [Answer.id, Answer.weight]
    form_excluded_columns = [Answer.created_at]
    can_create = True
    can_edit = True
    can_delete = True
    name = "Answer"
    name_plural = "Answers"
    icon = "fa-solid fa-check-circle"
