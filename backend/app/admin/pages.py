"""Custom admin pages."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.question import Question
from app.db.models.specialty import Specialty
from app.db.models.test import Test
from app.db.session import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")


async def check_admin_session(request: Request):
    """Check if user is authenticated in admin session."""
    # SQLAdmin stores user info in session
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True


@router.get("/test/create")
async def test_create_redirect():
    """Redirect from SQLAdmin create URL to custom editor."""
    return RedirectResponse(url="/admin/test-create")


@router.get("/test-editor/{test_id}", response_class=HTMLResponse)
async def test_editor(
    request: Request,
    test_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Custom test editor page."""
    # TODO: Add proper admin authentication check

    # Get test with all questions and answers
    stmt = (
        select(Test)
        .where(Test.id == test_id)
        .options(
            selectinload(Test.questions).selectinload(Question.answers),
            selectinload(Test.questions).selectinload(Question.specialty),
        )
    )
    result = await db.execute(stmt)
    test = result.scalar_one_or_none()

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Get all specialties for dropdown
    spec_stmt = select(Specialty).order_by(Specialty.code)
    spec_result = await db.execute(spec_stmt)
    specialties = spec_result.scalars().all()

    # Convert everything to simple dicts
    test_data = {
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "test_type": test.test_type,
        "specialty_id": test.specialty_id,
        "is_active": test.is_active,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "specialty_id": q.specialty_id,
                "order": q.order,
                "answers": [
                    {
                        "id": a.id,
                        "text": a.text,
                        "weights": a.weights,
                    }
                    for a in q.answers
                ]
            }
            for q in test.questions
        ]
    }

    specialties_data = [
        {"id": s.id, "code": s.code, "name": s.name}
        for s in specialties
    ]

    return _render_test_editor(test_data, specialties_data, is_new=False)


@router.get("/test-create", response_class=HTMLResponse)
async def test_create(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create new test page."""
    # TODO: Add proper admin authentication check

    # Get all specialties for dropdown
    spec_stmt = select(Specialty).order_by(Specialty.code)
    spec_result = await db.execute(spec_stmt)
    specialties = spec_result.scalars().all()

    specialties_data = [
        {"id": s.id, "code": s.code, "name": s.name}
        for s in specialties
    ]

    # Empty test data
    test_data = {
        "id": None,
        "title": "Новий тест",
        "description": "",
        "test_type": "general",
        "is_active": True,
        "questions": []
    }

    return _render_test_editor(test_data, specialties_data, is_new=True)


def _render_test_editor(test_data: dict, specialties_data: list, is_new: bool = False):
    """Render test editor with Tailwind CSS."""
    questions_html = ""
    for idx, q in enumerate(test_data['questions'], 1):
        answers_html = ""
        for a in q['answers']:
            weights_html = ""
            for spec_code in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']:
                weight_val = a['weights'].get(spec_code, 0)
                weights_html += f"""
                <div class="text-center">
                    <label class="block text-xs text-gray-600 mb-1 font-medium">{spec_code}</label>
                    <input type="number" class="w-full px-2 py-1 text-center text-sm font-semibold text-accent-primary border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary weight-input"
                           min="0" max="10" step="1"
                           value="{weight_val}"
                           data-answer-id="{a['id']}"
                           data-specialty="{spec_code}">
                </div>
                """

            answers_html += f"""
            <div class="bg-gray-50 rounded-xl p-4 mb-3 border border-gray-100" data-answer-id="{a['id']}">
                <div class="flex gap-3 mb-3">
                    <input type="text" class="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary answer-text"
                           value="{a['text']}" data-answer-id="{a['id']}">
                    <button class="px-3 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors" onclick="deleteAnswer({a['id']})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="grid grid-cols-7 gap-2">
                    {weights_html}
                </div>
            </div>
            """

        specialty_options = ""
        for s in specialties_data:
            selected = "selected" if s['id'] == q['specialty_id'] else ""
            specialty_options += f'<option value="{s["id"]}" {selected}>{s["code"]} - {s["name"]}</option>'

        questions_html += f"""
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6" data-question-id="{q['id']}">
            <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Питання {idx}</h3>
                <button class="px-3 py-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors" onclick="deleteQuestion({q['id']})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Текст питання</label>
                    <textarea class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary question-text"
                              rows="2" data-question-id="{q['id']}">{q['text']}</textarea>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Спеціальність</label>
                    <select class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary question-specialty"
                            data-question-id="{q['id']}" style="display: {'block' if test_data['test_type'] == 'general' else 'none'};">
                        {specialty_options}
                    </select>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Варіанти відповідей</label>
                    <div class="answers-container space-y-3" data-question-id="{q['id']}">
                        {answers_html}
                    </div>
                    <button class="mt-3 px-4 py-2 text-sm text-accent-primary border border-accent-primary rounded-xl hover:bg-orange-50 transition-colors" onclick="addAnswer({q['id']})">
                        <i class="fas fa-plus mr-2"></i>Додати відповідь
                    </button>
                </div>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Редактор тесту - {test_data['title']}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script>
            tailwind.config = {{
                theme: {{
                    extend: {{
                        colors: {{
                            'accent-primary': '#f97316',
                            'accent-secondary': '#fb923c',
                        }}
                    }}
                }}
            }}
        </script>
    </head>
    <body class="bg-gray-50">
        <div class="max-w-4xl mx-auto py-8 px-4">
            <!-- Header -->
            <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 md:p-8 mb-6">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold text-gray-900">
                        <i class="fas fa-clipboard-list mr-2 text-accent-primary"></i>
                        <span id="test-title">{test_data['title']}</span>
                    </h1>
                    <a href="/admin/test/list" class="px-4 py-2 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors">
                        <i class="fas fa-arrow-left mr-2"></i>Назад
                    </a>
                </div>

                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Назва тесту</label>
                        <input type="text" id="title-input" value="{test_data['title']}"
                               class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Опис</label>
                        <textarea id="description-input" rows="2"
                                  class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all">{test_data.get('description', '')}</textarea>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Тип тесту</label>
                            <select id="test-type-input" onchange="toggleTestSpecialty()"
                                    class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all">
                                <option value="general" {'selected' if test_data['test_type'] == 'general' else ''}>Загальний</option>
                                <option value="specialized" {'selected' if test_data['test_type'] == 'specialized' else ''}>Спеціалізований</option>
                            </select>
                        </div>

                        <div id="test-specialty-container" style="display: {'block' if test_data['test_type'] == 'specialized' else 'none'};">
                            <label class="block text-sm font-medium text-gray-700 mb-2">Спеціальність тесту</label>
                            <select id="test-specialty-input"
                                    class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all">
                                {''.join([f'<option value="{s["id"]}" {"selected" if test_data.get("specialty_id") == s["id"] else ""}>{s["code"]} - {s["name"]}</option>' for s in specialties_data])}
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Статус</label>
                            <label class="flex items-center space-x-3 cursor-pointer">
                                <input type="checkbox" id="is-active-input" {'checked' if test_data['is_active'] else ''}
                                       class="w-5 h-5 text-accent-primary border-gray-300 rounded focus:ring-accent-primary">
                                <span class="text-sm text-gray-700">Тест активний</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Questions -->
            <div id="questions-container" class="space-y-6">
                {questions_html}
            </div>

            <!-- Add Question Button -->
            <div class="text-center mb-24">
                <button onclick="addQuestion()"
                        class="px-6 py-3 bg-gradient-to-r from-accent-primary to-accent-secondary text-white font-semibold rounded-xl hover:shadow-lg transition-all">
                    <i class="fas fa-plus mr-2"></i>Додати питання
                </button>
            </div>

            <!-- Save Bar -->
            <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
                <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
                    <span id="save-status" class="text-sm text-gray-600">Є незбережені зміни</span>
                    <button onclick="saveTest()"
                            class="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all">
                        <i class="fas fa-save mr-2"></i>Зберегти тест
                    </button>
                </div>
            </div>
        </div>

        <!-- Modal for adding question -->
        <div id="questionModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
            <div class="bg-white rounded-2xl p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-gray-900">Додати питання</h3>
                    <button onclick="closeModal('questionModal')" class="text-gray-400 hover:text-gray-600 text-2xl w-8 h-8 flex items-center justify-center">
                        &times;
                    </button>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Текст питання</label>
                        <textarea id="newQuestionText" rows="3" placeholder="Введіть текст питання..."
                                  class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Спеціальність</label>
                        <select id="newQuestionSpecialty"
                                class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary">
                            {''.join([f'<option value="{s["id"]}">{s["code"]} - {s["name"]}</option>' for s in specialties_data])}
                        </select>
                    </div>
                </div>
                <div class="flex gap-3 justify-end mt-6">
                    <button onclick="closeModal('questionModal')"
                            class="px-4 py-2 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors">
                        Скасувати
                    </button>
                    <button onclick="confirmAddQuestion()"
                            class="px-4 py-2 bg-gradient-to-r from-accent-primary to-accent-secondary text-white rounded-xl hover:shadow-lg transition-all">
                        Додати
                    </button>
                </div>
            </div>
        </div>

        <!-- Modal for adding answer -->
        <div id="answerModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
            <div class="bg-white rounded-2xl p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold text-gray-900">Додати відповідь</h3>
                    <button onclick="closeModal('answerModal')" class="text-gray-400 hover:text-gray-600 text-2xl w-8 h-8 flex items-center justify-center">
                        &times;
                    </button>
                </div>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Текст відповіді</label>
                        <input type="text" id="newAnswerText" placeholder="Введіть текст відповіді..."
                               class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Ваги по спеціальностях (0-10)</label>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {''.join([f'''
                            <div>
                                <label class="block text-xs text-gray-600 mb-1">{code}</label>
                                <input type="number" id="newAnswerWeight{code}" min="0" max="10" value="0"
                                       class="w-full px-3 py-2 text-center border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary">
                            </div>
                            ''' for code in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7']])}
                        </div>
                    </div>
                </div>
                <div class="flex gap-3 justify-end mt-6">
                    <button onclick="closeModal('answerModal')"
                            class="px-4 py-2 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors">
                        Скасувати
                    </button>
                    <button onclick="confirmAddAnswer()"
                            class="px-4 py-2 bg-gradient-to-r from-accent-primary to-accent-secondary text-white rounded-xl hover:shadow-lg transition-all">
                        Додати
                    </button>
                </div>
            </div>
        </div>

        <script>
            let testId = {test_data['id'] if test_data['id'] else 'null'};
            const apiBase = '/api/v1/admin/tests';
            const isNew = {'true' if is_new else 'false'};
            let currentQuestionIdForAnswer = null;

            function toggleTestSpecialty() {{
                const testType = document.getElementById('test-type-input').value;
                const isSpecialized = testType === 'specialized';
                const isGeneral = testType === 'general';

                // Show/hide test-level specialty for specialized tests
                document.getElementById('test-specialty-container').style.display = isSpecialized ? 'block' : 'none';

                // Show/hide question-level specialty for general tests
                document.querySelectorAll('.question-specialty').forEach(el => {{
                    el.style.display = isGeneral ? 'block' : 'none';
                }});
            }}

            function openModal(modalId) {{
                document.getElementById(modalId).classList.remove('hidden');
            }}

            function closeModal(modalId) {{
                document.getElementById(modalId).classList.add('hidden');
            }}

            function addQuestion() {{
                openModal('questionModal');
            }}

            function confirmAddQuestion() {{
                const questionText = document.getElementById('newQuestionText').value.trim();
                const specialtyId = document.getElementById('newQuestionSpecialty').value;

                if (!questionText) {{
                    alert('Введіть текст питання');
                    return;
                }}

                closeModal('questionModal');

                if (isNew || testId === null) {{
                    addQuestionLocally(questionText, parseInt(specialtyId));
                }} else {{
                    fetch(`${{apiBase}}/${{testId}}/questions`, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            text: questionText,
                            specialty_id: parseInt(specialtyId),
                            order: document.querySelectorAll('.question-card').length + 1,
                            answers: []
                        }}),
                        credentials: 'include'
                    }})
                    .then(() => {{
                        window.location.reload();
                    }})
                    .catch(error => {{
                        console.error('Error adding question:', error);
                        alert('Помилка при додаванні питання');
                    }});
                }}

                // Clear form
                document.getElementById('newQuestionText').value = '';
            }}

            function addAnswer(questionId) {{
                currentQuestionIdForAnswer = questionId;
                openModal('answerModal');
            }}

            function addAnswerLocally(questionId) {{
                currentQuestionIdForAnswer = questionId;
                openModal('answerModal');
            }}

            function confirmAddAnswer() {{
                const answerText = document.getElementById('newAnswerText').value.trim();
                if (!answerText) {{
                    alert('Введіть текст відповіді');
                    return;
                }}

                const weights = {{}};
                ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'].forEach(code => {{
                    weights[code] = parseInt(document.getElementById('newAnswerWeight' + code).value) || 0;
                }});

                closeModal('answerModal');

                const questionCard = document.querySelector(`[data-question-id="${{currentQuestionIdForAnswer}}"]`);
                const isNewQuestion = questionCard && questionCard.dataset.isNew === 'true';

                if (isNewQuestion || isNew || testId === null) {{
                    addAnswerLocallyToQuestion(currentQuestionIdForAnswer, answerText, weights);
                }} else {{
                    fetch(`${{apiBase}}/questions/${{currentQuestionIdForAnswer}}/answers`, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            text: answerText,
                            weights: weights,
                            weight: 0
                        }}),
                        credentials: 'include'
                    }})
                    .then(() => {{
                        window.location.reload();
                    }})
                    .catch(error => {{
                        console.error('Error adding answer:', error);
                        alert('Помилка при додаванні відповіді');
                    }});
                }}

                // Clear form
                document.getElementById('newAnswerText').value = '';
                ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'].forEach(code => {{
                    document.getElementById('newAnswerWeight' + code).value = '0';
                }});
            }}

            function addAnswerLocallyToQuestion(questionId, answerText, weights) {{
                const container = document.querySelector(`[data-question-id="${{questionId}}"] .answers-container`);
                const tempId = 'new_' + Date.now();

                let weightsHtml = '';
                ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'].forEach(code => {{
                    weightsHtml += `
                        <div class="text-center">
                            <label class="block text-xs text-gray-600 mb-1 font-medium">${{code}}</label>
                            <input type="number" class="w-full px-2 py-1 text-center text-sm font-semibold text-accent-primary border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary weight-input"
                                   min="0" max="10" step="1" value="${{weights[code]}}"
                                   data-answer-id="${{tempId}}"
                                   data-specialty="${{code}}">
                        </div>
                    `;
                }});

                const answerHtml = `
                    <div class="bg-gray-50 rounded-xl p-4 mb-3 border border-gray-100" data-answer-id="${{tempId}}" data-is-new="true">
                        <div class="flex gap-3 mb-3">
                            <input type="text" class="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary answer-text"
                                   value="${{answerText}}" data-answer-id="${{tempId}}">
                            <button class="px-3 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors" onclick="this.closest('.bg-gray-50').remove()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="grid grid-cols-7 gap-2">
                            ${{weightsHtml}}
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', answerHtml);
            }}

            async function saveTest() {{
                const saveBtn = event.target;
                saveBtn.disabled = true;
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Збереження...';

                try {{
                    const testData = {{
                        title: document.getElementById('title-input').value,
                        description: document.getElementById('description-input').value,
                        test_type: document.getElementById('test-type-input').value,
                        is_active: document.getElementById('is-active-input').checked
                    }};

                    // Add specialty_id for specialized tests
                    if (testData.test_type === 'specialized') {{
                        testData.specialty_id = parseInt(document.getElementById('test-specialty-input').value);
                    }}

                    if (isNew || testId === null) {{
                        // Create new test
                        const response = await fetch(`${{apiBase}}/`, {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify(testData),
                            credentials: 'include'
                        }});
                        const result = await response.json();
                        testId = result.id;

                        // Create questions and answers for new test
                        const questions = document.querySelectorAll('.question-card[data-is-new="true"]');
                        for (const qCard of questions) {{
                            const qText = qCard.querySelector('.question-text').value;
                            const qSpecialty = qCard.querySelector('.question-specialty').value;

                            // Create question
                            const qResponse = await fetch(`${{apiBase}}/${{testId}}/questions`, {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{
                                    text: qText,
                                    specialty_id: parseInt(qSpecialty),
                                    order: Array.from(questions).indexOf(qCard) + 1,
                                    answers: []
                                }}),
                                credentials: 'include'
                            }});
                            const qResult = await qResponse.json();
                            const newQuestionId = qResult.questions[qResult.questions.length - 1].id;

                            // Create answers for this question
                            const answers = qCard.querySelectorAll('.answer-item[data-is-new="true"]');
                            for (const aItem of answers) {{
                                const aText = aItem.querySelector('.answer-text').value;
                                const weights = {{}};
                                const weightInputs = aItem.querySelectorAll('.weight-input');
                                weightInputs.forEach(input => {{
                                    weights[input.dataset.specialty] = parseInt(input.value) || 0;
                                }});

                                await fetch(`${{apiBase}}/questions/${{newQuestionId}}/answers`, {{
                                    method: 'POST',
                                    headers: {{'Content-Type': 'application/json'}},
                                    body: JSON.stringify({{
                                        text: aText,
                                        weights: weights,
                                        weight: 0
                                    }}),
                                    credentials: 'include'
                                }});
                            }}
                        }}

                        alert('Тест створено! ID: ' + result.id);
                        window.location.href = '/admin/test-editor/' + result.id;
                        return;
                    }}

                    // Update existing test
                    await fetch(`${{apiBase}}/${{testId}}`, {{
                        method: 'PUT',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify(testData),
                        credentials: 'include'
                    }});

                    // Update questions and answers
                    const questions = document.querySelectorAll('.question-card');
                    const testType = document.getElementById('test-type-input').value;

                    for (const qCard of questions) {{
                        const qId = qCard.dataset.questionId;
                        const qText = qCard.querySelector('.question-text').value;

                        const questionData = {{ text: qText }};

                        // Only include specialty_id for general tests
                        if (testType === 'general') {{
                            const qSpecialty = qCard.querySelector('.question-specialty').value;
                            questionData.specialty_id = parseInt(qSpecialty);
                        }}

                        await fetch(`${{apiBase}}/questions/${{qId}}`, {{
                            method: 'PUT',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify(questionData),
                            credentials: 'include'
                        }});

                        // Update answers
                        const answers = qCard.querySelectorAll('.answer-item');
                        for (const aItem of answers) {{
                            const aId = aItem.dataset.answerId;
                            const aText = aItem.querySelector('.answer-text').value;

                            // Collect weights from inputs
                            const weights = {{}};
                            const weightInputs = aItem.querySelectorAll('.weight-input');
                            weightInputs.forEach(input => {{
                                weights[input.dataset.specialty] = parseInt(input.value) || 0;
                            }});

                            await fetch(`${{apiBase}}/answers/${{aId}}`, {{
                                method: 'PUT',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{
                                    text: aText,
                                    weights: weights
                                }}),
                                credentials: 'include'
                            }});
                        }}
                    }}

                    document.getElementById('save-status').textContent = 'Всі зміни збережено';
                    document.getElementById('save-status').classList.remove('text-warning');
                    document.getElementById('save-status').classList.add('text-success');
                    alert('Тест успішно збережено!');
                }} catch (error) {{
                    console.error('Error saving test:', error);
                    alert('Помилка при збереженні тесту: ' + error.message);
                }} finally {{
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Зберегти тест';
                }}
            }}

            async function deleteQuestion(questionId) {{
                if (!confirm('Видалити це питання?')) return;
                try {{
                    await fetch(`${{apiBase}}/questions/${{questionId}}`, {{
                        method: 'DELETE',
                        credentials: 'include'
                    }});
                    document.querySelector(`[data-question-id="${{questionId}}"]`).remove();
                }} catch (error) {{
                    console.error('Error deleting question:', error);
                    alert('Помилка при видаленні питання');
                }}
            }}

            async function deleteAnswer(answerId) {{
                if (!confirm('Видалити цю відповідь?')) return;
                try {{
                    await fetch(`${{apiBase}}/answers/${{answerId}}`, {{
                        method: 'DELETE',
                        credentials: 'include'
                    }});
                    document.querySelector(`[data-answer-id="${{answerId}}"]`).remove();
                }} catch (error) {{
                    console.error('Error deleting answer:', error);
                    alert('Помилка при видаленні відповіді');
                }}
            }}

            function addQuestionLocally(questionText, specialtyId) {{
                const container = document.getElementById('questions-container');
                const questionIndex = document.querySelectorAll('.question-card').length + 1;
                const tempId = 'new_' + Date.now();

                const questionHtml = `
                    <div class="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 question-card" data-question-id="${{tempId}}" data-is-new="true">
                        <div class="flex justify-between items-start mb-4">
                            <h3 class="text-lg font-semibold text-gray-900">Питання ${{questionIndex}}</h3>
                            <button class="px-3 py-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors" onclick="this.closest('.question-card').remove()">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Текст питання</label>
                                <textarea class="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary question-text"
                                          rows="2" data-question-id="${{tempId}}">${{questionText}}</textarea>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Спеціальність</label>
                                <input type="hidden" class="question-specialty" value="${{specialtyId}}" data-question-id="${{tempId}}">
                                <p class="text-sm text-gray-600">ID: ${{specialtyId}}</p>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">Варіанти відповідей</label>
                                <div class="answers-container space-y-3" data-question-id="${{tempId}}"></div>
                                <button class="mt-3 px-4 py-2 text-sm text-accent-primary border border-accent-primary rounded-xl hover:bg-orange-50 transition-colors" onclick="addAnswerLocally('${{tempId}}')">
                                    <i class="fas fa-plus mr-2"></i>Додати відповідь
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', questionHtml);
            }}

            function addAnswerLocally(questionId) {{
                currentQuestionIdForAnswer = questionId;
                openModal('answerModal');
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
