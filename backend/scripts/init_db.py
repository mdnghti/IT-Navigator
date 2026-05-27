"""
Database initialization script with hardcoded IT tests.
This script is self-contained and doesn't require external files.

Creates:
- Admin user
- IT Specialties (F1-F7)
- General test with 13 questions (multi-dimensional weights)
- Specialized tests for each specialty with 10 questions each
"""

import asyncio

from app.core.security import get_password_hash
from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.specialty import Specialty
from app.db.models.test import Test, TestType
from app.db.models.user import User
from app.db.session import AsyncSessionLocal


# Define related specialties for weight distribution
RELATED_SPECIALTIES = {
    "F1": ["F3", "F4"],  # Математика → Комп. науки, Data Science
    "F2": ["F3", "F6"],  # Інженерія ПЗ → Комп. науки, Інф. системи
    "F3": ["F1", "F2", "F4"],  # Комп. науки → Математика, Інженерія, Data Science
    "F4": ["F1", "F3", "F6"],  # Data Science → Математика, Комп. науки, Інф. системи
    "F5": ["F2", "F6", "F7"],  # Кібербезпека → Інженерія, Інф. системи, Комп. інженерія
    "F6": ["F2", "F4", "F5"],  # Інф. системи → Інженерія, Data Science, Кібербезпека
    "F7": ["F2", "F5"],  # Комп. інженерія → Інженерія, Кібербезпека
}

ALL_SPECIALTIES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]


def generate_weights(primary_specialty: str, single_weight: int) -> dict[str, int]:
    """Generate multi-dimensional weights from single weight."""
    weights = {}
    related = RELATED_SPECIALTIES.get(primary_specialty, [])

    for specialty in ALL_SPECIALTIES:
        if specialty == primary_specialty:
            weights[specialty] = single_weight
        elif specialty in related:
            if single_weight >= 10:
                weights[specialty] = 5
            elif single_weight >= 5:
                weights[specialty] = 3
            elif single_weight >= 2:
                weights[specialty] = 1
            else:
                weights[specialty] = 0
        else:
            if single_weight >= 10:
                weights[specialty] = 1
            else:
                weights[specialty] = 0

    return weights


# IT Specialties data
SPECIALTIES = [
    {
        "code": "F1",
        "name": "Прикладна математика",
        "description": "Математичне моделювання, аналіз даних, статистика",
    },
    {
        "code": "F2",
        "name": "Інженерія програмного забезпечення",
        "description": "Розробка, тестування та підтримка програмного забезпечення",
    },
    {
        "code": "F3",
        "name": "Комп'ютерні науки",
        "description": "Алгоритми, структури даних, штучний інтелект",
    },
    {
        "code": "F4",
        "name": "Системний аналіз та Data Science",
        "description": "Аналіз даних, бізнес-аналітика, прогнозування",
    },
    {
        "code": "F5",
        "name": "Кібербезпека",
        "description": "Захист інформації, мережева безпека, криптографія",
    },
    {
        "code": "F6",
        "name": "Інформаційні системи та технології",
        "description": "Проектування та управління ІТ-системами, DevOps",
    },
    {
        "code": "F7",
        "name": "Комп'ютерна інженерія",
        "description": "Апаратне забезпечення, embedded-системи, мікроконтролери",
    },
]

# General test questions (13 questions covering all specialties)
GENERAL_TEST_QUESTIONS = [
    {
        "text": "Яке число має бути наступним у ряду: 2, 4, 8, 16, ?",
        "specialty": "F1",
        "answers": [
            {"text": "18", "weight": 0},
            {"text": "24", "weight": 5},
            {"text": "32", "weight": 10},
            {"text": "36", "weight": 0},
        ],
    },
    {
        "text": "Вам прийшов лист із проханням терміново ввести пароль. Що зробите?",
        "specialty": "F5",
        "answers": [
            {"text": "Введу пароль", "weight": 0},
            {"text": "Перевірю адресу відправника", "weight": 10},
            {"text": "Перешлю друзям", "weight": 0},
            {"text": "Видалю браузер", "weight": 3},
        ],
    },
    {
        "text": "Що важливіше при створенні великої програми?",
        "specialty": "F2",
        "answers": [
            {"text": "Кольори", "weight": 0},
            {"text": "Кількість кнопок", "weight": 2},
            {"text": "Структура коду", "weight": 10},
            {"text": "Анімації", "weight": 0},
        ],
    },
    {
        "text": "Що найбільше впливає на швидкість ПК?",
        "specialty": "F7",
        "answers": [
            {"text": "Колір корпусу", "weight": 0},
            {"text": "Процесор і RAM", "weight": 10},
            {"text": "Шпалери", "weight": 0},
            {"text": "Браузер", "weight": 2},
        ],
    },
    {
        "text": "Що допоможе передбачити продажі?",
        "specialty": "F4",
        "answers": [
            {"text": "Аналіз даних", "weight": 10},
            {"text": "Випадковий вибір", "weight": 0},
            {"text": "Новий логотип", "weight": 2},
            {"text": "Перезапуск ПК", "weight": 0},
        ],
    },
    {
        "text": "Що таке алгоритм?",
        "specialty": "F3",
        "answers": [
            {"text": "Гра", "weight": 2},
            {"text": "Послідовність дій", "weight": 10},
            {"text": "Монітор", "weight": 0},
            {"text": "Вірус", "weight": 0},
        ],
    },
    {
        "text": "Для чого потрібна база даних?",
        "specialty": "F6",
        "answers": [
            {"text": "Зберігання інформації", "weight": 10},
            {"text": "Ігри", "weight": 0},
            {"text": "Охолодження ПК", "weight": 0},
            {"text": "Малювання", "weight": 1},
        ],
    },
    {
        "text": "Яке число зайве: 5, 10, 15, 22, 25?",
        "specialty": "F1",
        "answers": [
            {"text": "5", "weight": 0},
            {"text": "15", "weight": 3},
            {"text": "22", "weight": 10},
            {"text": "25", "weight": 0},
        ],
    },
    {
        "text": "Який пароль безпечніший?",
        "specialty": "F5",
        "answers": [
            {"text": "123456", "weight": 0},
            {"text": "qwerty", "weight": 0},
            {"text": "MyDog2026!", "weight": 10},
            {"text": "admin", "weight": 2},
        ],
    },
    {
        "text": "Для чого програму ділять на модулі?",
        "specialty": "F2",
        "answers": [
            {"text": "Для зручності підтримки", "weight": 10},
            {"text": "Для реклами", "weight": 0},
            {"text": "Щоб код був довший", "weight": 1},
            {"text": "Для кольорів", "weight": 0},
        ],
    },
    {
        "text": "Що буде швидше для пошуку слова?",
        "specialty": "F3",
        "answers": [
            {"text": "Перегляд усіх сторінок", "weight": 4},
            {"text": "Пошук за алфавітом", "weight": 10},
            {"text": "Випадковий вибір", "weight": 0},
            {"text": "Закриття словника", "weight": 0},
        ],
    },
    {
        "text": "Що допоможе уникнути плутанини у компанії?",
        "specialty": "F6",
        "answers": [
            {"text": "Інформаційна система", "weight": 10},
            {"text": "Випадкові записи", "weight": 1},
            {"text": "Відсутність правил", "weight": 0},
            {"text": "Видалення файлів", "weight": 0},
        ],
    },
    {
        "text": "Чому ПК може перегріватися?",
        "specialty": "F7",
        "answers": [
            {"text": "Погане охолодження", "weight": 10},
            {"text": "Назва браузера", "weight": 0},
            {"text": "Шпалери", "weight": 0},
            {"text": "Колір корпусу", "weight": 1},
        ],
    },
]

# Specialized tests data (10 questions each)
# Format: specialty_code -> list of questions
SPECIALIZED_TESTS = {
    "F1": [
        {"text": "Наступне число: 3, 6, 12, 24, ?", "answers": [("30", 0), ("36", 0), ("48", 10), ("54", 0)]},
        {"text": "Яке число зайве: 2, 4, 6, 7, 8", "answers": [("2", 0), ("4", 0), ("7", 10), ("8", 0)]},
        {"text": "Що таке математичне моделювання?", "answers": [("Аналіз процесів через формули", 10), ("Ремонт ПК", 0), ("Монтаж відео", 0), ("Ігри", 0)]},
        {"text": "Якщо графік функції росте, він:", "answers": [("Спадає", 0), ("Підіймається", 10), ("Стоїть", 0), ("Зникає", 0)]},
        {"text": "Що таке відсоток?", "answers": [("Частина від цілого", 10), ("Тип пам'яті", 0), ("Кабель", 0), ("Браузер", 0)]},
        {"text": "25% від 200 =", "answers": [("25", 0), ("40", 0), ("50", 10), ("75", 0)]},
        {"text": "Яка фігура має 3 сторони?", "answers": [("Квадрат", 0), ("Коло", 0), ("Трикутник", 10), ("Куб", 0)]},
        {"text": "Що таке статистика?", "answers": [("Аналіз даних", 10), ("Тип монітора", 0), ("Процесор", 0), ("Мова програмування", 0)]},
        {"text": "Якщо x + 5 = 12, x =", "answers": [("5", 0), ("6", 0), ("7", 10), ("8", 0)]},
        {"text": "Для чого потрібні графіки?", "answers": [("Візуалізація даних", 10), ("Ігри", 0), ("Охолодження ПК", 0), ("Друк", 0)]},
    ],
    "F2": [
        {"text": "Що таке Git?", "answers": [("Контроль версій", 10), ("Антивірус", 0), ("Редактор фото", 0), ("Гра", 0)]},
        {"text": "Що таке баг?", "answers": [("Помилка в коді", 10), ("Дизайн", 0), ("Сервер", 0), ("Кабель", 0)]},
        {"text": "Для чого тестують програми?", "answers": [("Пошук помилок", 10), ("Зміна кольору", 0), ("Ігри", 0), ("Реклама", 0)]},
        {"text": "Що таке IDE?", "answers": [("Середовище розробки", 10), ("Тип процесора", 0), ("Монітор", 0), ("Кабель", 0)]},
        {"text": "Для чого код ділять на модулі?", "answers": [("Підтримка та масштабування", 10), ("Для реклами", 0), ("Для кольорів", 0), ("Для музики", 0)]},
        {"text": "Що таке frontend?", "answers": [("Частина, яку бачить користувач", 10), ("Сервер", 0), ("База даних", 0), ("BIOS", 0)]},
        {"text": "Що таке backend?", "answers": [("Логіка та серверна частина", 10), ("Колір сайту", 0), ("Відеокарта", 0), ("Клавіатура", 0)]},
        {"text": "Що таке Agile?", "answers": [("Методологія розробки", 10), ("Процесор", 0), ("Антивірус", 0), ("Кабель", 0)]},
        {"text": "Для чого потрібна документація?", "answers": [("Розуміння проєкту", 10), ("Ігри", 0), ("Відео", 0), ("Реклама", 0)]},
        {"text": "Що робить програміст?", "answers": [("Створює та підтримує ПЗ", 10), ("Лише ремонтує ПК", 0), ("Друкує документи", 0), ("Монтує відео", 0)]},
    ],
    "F3": [
        {"text": "Що таке алгоритм?", "answers": [("Послідовність дій", 10), ("Гра", 0), ("Кабель", 0), ("Монітор", 0)]},
        {"text": "Що таке структура даних?", "answers": [("Організація даних", 10), ("Антивірус", 0), ("Відеокарта", 0), ("Браузер", 0)]},
        {"text": "Для чого використовують AI?", "answers": [("Аналіз та автоматизація", 10), ("Друк", 0), ("Охолодження", 0), ("Фарбування", 0)]},
        {"text": "Що таке цикл у програмуванні?", "answers": [("Повторення дій", 10), ("Помилка", 0), ("Тип монітора", 0), ("Кабель", 0)]},
        {"text": "Що таке змінна?", "answers": [("Комірка для даних", 10), ("Процесор", 0), ("Сервер", 0), ("Браузер", 0)]},
        {"text": "Що таке база даних?", "answers": [("Сховище інформації", 10), ("Гра", 0), ("RAM", 0), ("BIOS", 0)]},
        {"text": "Що таке компілятор?", "answers": [("Перекладає код", 10), ("Охолоджує ПК", 0), ("Малює графіку", 0), ("Зберігає фото", 0)]},
        {"text": "Що таке оптимізація?", "answers": [("Покращення ефективності", 10), ("Видалення файлів", 0), ("Зміна кольору", 0), ("Друк", 0)]},
        {"text": "Що швидше для пошуку?", "answers": [("Алфавітний порядок", 10), ("Випадковий пошук", 0), ("Повний перегляд", 0), ("Закриття програми", 0)]},
        {"text": "Що таке нейромережа?", "answers": [("Модель для AI", 10), ("Кабель", 0), ("Монітор", 0), ("Серверна кімната", 0)]},
    ],
    "F4": [
        {"text": "Що таке dataset?", "answers": [("Набір даних", 10), ("Кабель", 0), ("Монітор", 0), ("Процесор", 0)]},
        {"text": "Для чого потрібна візуалізація?", "answers": [("Аналіз даних", 10), ("Ігри", 0), ("Реклама", 0), ("Охолодження", 0)]},
        {"text": "Що допомагає знайти закономірності?", "answers": [("Статистика", 10), ("Випадковість", 0), ("Видалення файлів", 0), ("Перезапуск ПК", 0)]},
        {"text": "Що таке аналітика?", "answers": [("Аналіз інформації", 10), ("Гра", 0), ("Кабель", 0), ("RAM", 0)]},
        {"text": "Для чого потрібні графіки?", "answers": [("Показ даних", 10), ("Ігри", 0), ("Ремонт ПК", 0), ("BIOS", 0)]},
        {"text": "Що таке прогнозування?", "answers": [("Передбачення на основі даних", 10), ("Монтаж відео", 0), ("Друк", 0), ("Малювання", 0)]},
        {"text": "Що таке BI-система?", "answers": [("Система бізнес-аналітики", 10), ("Тип відеокарти", 0), ("Браузер", 0), ("Антивірус", 0)]},
        {"text": "Що таке SQL?", "answers": [("Мова роботи з БД", 10), ("Кабель", 0), ("Монітор", 0), ("Процесор", 0)]},
        {"text": "Що робить аналітик даних?", "answers": [("Аналізує інформацію", 10), ("Лише ремонтує ПК", 0), ("Малює логотипи", 0), ("Збирає столи", 0)]},
        {"text": "Для чого використовують Data Science?", "answers": [("Аналіз і прогнозування", 10), ("Ігри", 0), ("Фарбування корпусів", 0), ("Друк", 0)]},
    ],
    "F5": [
        {"text": "Що таке фішинг?", "answers": [("Шахрайство через підроблені повідомлення", 10), ("Тип процесора", 0), ("Гра", 0), ("Кабель", 0)]},
        {"text": "Який пароль безпечніший?", "answers": [("123456", 0), ("qwerty", 0), ("MyDog2026!", 10), ("admin", 0)]},
        {"text": "Що таке 2FA?", "answers": [("Додатковий захист", 10), ("Відеокарта", 0), ("Монітор", 0), ("Браузер", 0)]},
        {"text": "Для чого потрібне шифрування?", "answers": [("Захист інформації", 10), ("Ігри", 0), ("Реклама", 0), ("Монтаж відео", 0)]},
        {"text": "Що таке вірус?", "answers": [("Шкідлива програма", 10), ("Кабель", 0), ("Монітор", 0), ("RAM", 0)]},
        {"text": "Що таке VPN?", "answers": [("Захищене з'єднання", 10), ("Тип мишки", 0), ("Принтер", 0), ("BIOS", 0)]},
        {"text": "Чому не можна відкривати підозрілі файли?", "answers": [("Можуть містити вірус", 10), ("Зламається монітор", 0), ("Зникне браузер", 0), ("Зламається стіл", 0)]},
        {"text": "Що таке firewall?", "answers": [("Захист мережі", 10), ("Кабель", 0), ("Відеокарта", 0), ("Динамік", 0)]},
        {"text": "Для чого оновлюють ПЗ?", "answers": [("Закриття вразливостей", 10), ("Для шпалер", 0), ("Для реклами", 0), ("Для музики", 0)]},
        {"text": "Що таке кібербезпека?", "answers": [("Захист систем та даних", 10), ("Монтаж відео", 0), ("Ремонт столів", 0), ("Друк", 0)]},
    ],
    "F6": [
        {"text": "Для чого потрібна БД?", "answers": [("Зберігання інформації", 10), ("Ігри", 0), ("Охолодження", 0), ("Малювання", 0)]},
        {"text": "Що таке CRM?", "answers": [("Система роботи з клієнтами", 10), ("Процесор", 0), ("Відеокарта", 0), ("Кабель", 0)]},
        {"text": "Що таке ERP?", "answers": [("Система управління ресурсами", 10), ("Браузер", 0), ("Монітор", 0), ("RAM", 0)]},
        {"text": "Для чого автоматизують процеси?", "answers": [("Підвищення ефективності", 10), ("Ігри", 0), ("Шпалери", 0), ("Реклама", 0)]},
        {"text": "Що таке DevOps?", "answers": [("Автоматизація інфраструктури", 10), ("Дизайн", 0), ("Друк", 0), ("Фото", 0)]},
        {"text": "Що робить системний адміністратор?", "answers": [("Підтримує системи", 10), ("Малює логотипи", 0), ("Збирає меблі", 0), ("Друкує фото", 0)]},
        {"text": "Для чого потрібен сервер?", "answers": [("Обробка та зберігання даних", 10), ("Ігри", 0), ("Музика", 0), ("Монтаж", 0)]},
        {"text": "Що таке хмарні технології?", "answers": [("Робота через інтернет-сервери", 10), ("Погода", 0), ("Тип мишки", 0), ("Монітор", 0)]},
        {"text": "Що допомагає уникнути плутанини?", "answers": [("Інформаційна система", 10), ("Випадкові записи", 0), ("Видалення файлів", 0), ("Відсутність правил", 0)]},
        {"text": "Для чого потрібні ІТ-системи у бізнесі?", "answers": [("Автоматизація та аналіз", 10), ("Лише ігри", 0), ("Малювання", 0), ("Друк", 0)]},
    ],
    "F7": [
        {"text": "Для чого потрібна RAM?", "answers": [("Тимчасове зберігання даних", 10), ("Охолодження", 0), ("Друк", 0), ("Малювання", 0)]},
        {"text": "Що таке процесор?", "answers": [("Основний обчислювальний компонент", 10), ("Кабель", 0), ("Монітор", 0), ("Браузер", 0)]},
        {"text": "Що таке мікроконтролер?", "answers": [("Маленький керуючий комп'ютер", 10), ("Клавіатура", 0), ("Мишка", 0), ("Динамік", 0)]},
        {"text": "Чому ПК перегрівається?", "answers": [("Погане охолодження", 10), ("Назва браузера", 0), ("Шпалери", 0), ("Колір корпусу", 0)]},
        {"text": "Для чого потрібна відеокарта?", "answers": [("Обробка графіки", 10), ("Зберігання файлів", 0), ("Охолодження", 0), ("Друк", 0)]},
        {"text": "Що таке SSD?", "answers": [("Швидкий накопичувач", 10), ("Кабель", 0), ("Монітор", 0), ("Процесор", 0)]},
        {"text": "Для чого потрібен блок живлення?", "answers": [("Подача електроенергії", 10), ("Ігри", 0), ("Шпалери", 0), ("Фото", 0)]},
        {"text": "Що таке BIOS?", "answers": [("Система запуску ПК", 10), ("Гра", 0), ("Браузер", 0), ("RAM", 0)]},
        {"text": "Що робить мережевий адаптер?", "answers": [("Підключає до мережі", 10), ("Друкує фото", 0), ("Малює графіку", 0), ("Охолоджує ПК", 0)]},
        {"text": "Що таке embedded-система?", "answers": [("Вбудований комп'ютер", 10), ("Монітор", 0), ("Клавіатура", 0), ("Кабель", 0)]},
    ],
}


async def init_db() -> None:
    """Initialize database with all data."""
    async with AsyncSessionLocal() as db:
        print("Creating admin user...")
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_admin=True,
            is_active=True,
        )
        db.add(admin)

        print("Creating IT specialties...")
        specialties = {}
        for spec_data in SPECIALTIES:
            specialty = Specialty(**spec_data)
            db.add(specialty)
            await db.flush()
            specialties[spec_data["code"]] = specialty
            print(f"  Created {spec_data['code']}: {spec_data['name']}")

        print("\nCreating general test...")
        general_test = Test(
            title="Загальний профорієнтаційний тест",
            description="Визначення схильностей до різних ІТ-спеціальностей",
            test_type=TestType.GENERAL,
            is_active=True,
        )
        db.add(general_test)
        await db.flush()

        print(f"Adding {len(GENERAL_TEST_QUESTIONS)} general test questions...")
        for idx, q_data in enumerate(GENERAL_TEST_QUESTIONS, 1):
            question = Question(
                test_id=general_test.id,
                specialty_id=specialties[q_data["specialty"]].id,
                text=q_data["text"],
                order=idx,
            )
            db.add(question)
            await db.flush()

            # Create answers with multi-dimensional weights
            for answer_data in q_data["answers"]:
                # Generate weights for all specialties based on primary specialty
                weights = generate_weights(
                    q_data["specialty"],
                    answer_data["weight"]
                )

                answer = Answer(
                    question_id=question.id,
                    text=answer_data["text"],
                    weight=answer_data["weight"],  # Keep legacy field
                    weights=weights,  # New multi-dimensional weights
                )
                db.add(answer)
                await db.flush()

        print("\nCreating specialized tests...")
        for code, questions_data in SPECIALIZED_TESTS.items():
            specialty = specialties[code]
            print(f"\n  {code} - {specialty.name}:")
            
            spec_test = Test(
                title=f"Спеціалізований тест: {specialty.name}",
                description=f"Поглиблене тестування для спеціальності {specialty.name}",
                test_type=TestType.SPECIALIZED,
                specialty_id=specialty.id,
                is_active=True,
            )
            db.add(spec_test)
            await db.flush()

            for idx, q_data in enumerate(questions_data, 1):
                question = Question(
                    test_id=spec_test.id,
                    specialty_id=specialty.id,
                    text=q_data["text"],
                    order=idx,
                )
                db.add(question)
                await db.flush()

                # Add all answers for this question one by one
                answer_count = 0
                for answer_text, weight in q_data["answers"]:
                    try:
                        # Generate multi-dimensional weights
                        weights = generate_weights(code, weight)

                        answer = Answer(
                            question_id=question.id,
                            text=answer_text,
                            weight=weight,  # Keep legacy field
                            weights=weights,  # New multi-dimensional weights
                        )
                        db.add(answer)
                        await db.flush()  # Flush each answer individually
                        answer_count += 1
                    except Exception as e:
                        print(f"    ERROR adding answer '{answer_text}' to question '{q_data['text'][:50]}': {e}")

                if answer_count != 4:
                    print(f"    WARNING: Question '{q_data['text'][:50]}' has {answer_count} answers instead of 4!")

            print(f"    Added {len(questions_data)} questions")

        await db.commit()
        print("\n✅ Database initialized successfully!")
        print("\nAdmin credentials:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nAccess admin panel at: http://localhost:8000/admin")
        print("\nTests created:")
        print("  - 1 general test with 13 questions")
        print("  - 7 specialized tests with 10 questions each")


if __name__ == "__main__":
    asyncio.run(init_db())
