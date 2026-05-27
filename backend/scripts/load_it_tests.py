"""
Load IT career tests from it_tests.md file.

Parses the markdown file and creates:
- General test with 13 questions
- Specialized tests for F1-F7 with 10 questions each
"""

import asyncio
import re
from pathlib import Path

from sqlalchemy import select, delete

from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.result import TestResult
from app.db.models.specialty import Specialty
from app.db.models.test import Test, TestType
from app.db.session import AsyncSessionLocal


def parse_it_tests_md(file_path: str) -> dict:
    """Parse it_tests.md file and extract test data."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by test sections
    sections = re.split(r"^# (F\d — .+|Загальний тест.+)$", content, flags=re.MULTILINE)

    tests = {
        "general": {"questions": []},
        "F1": {"questions": []},
        "F2": {"questions": []},
        "F3": {"questions": []},
        "F4": {"questions": []},
        "F5": {"questions": []},
        "F6": {"questions": []},
        "F7": {"questions": []},
    }

    current_section = None

    for i in range(1, len(sections), 2):
        section_title = sections[i]
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        if "Загальний тест" in section_title:
            current_section = "general"
        else:
            # Extract specialty code (F1, F2, etc.)
            match = re.match(r"(F\d)", section_title)
            if match:
                current_section = match.group(1)

        if not current_section:
            continue

        # Parse questions in this section
        question_blocks = re.split(r"^## Питання \d+|^\d+\.", section_content, flags=re.MULTILINE)

        for block in question_blocks[1:]:  # Skip first empty block
            if not block.strip():
                continue

            # Extract question text
            lines = block.strip().split("\n")
            question_text = ""
            answers = []

            i = 0
            # Get question text (everything before answer options)
            while i < len(lines) and not re.match(r"^[A-D]\.", lines[i].strip()):
                line = lines[i].strip()
                if line and not line.startswith("|") and not line.startswith("---"):
                    # Remove specialty marker like (F1 — ...)
                    line = re.sub(r"\(F\d — [^)]+\)", "", line).strip()
                    if line:
                        question_text += line + " "
                i += 1

            question_text = question_text.strip()
            if not question_text:
                continue

            # Parse answers
            answer_weights = {}

            # First, collect answer options (A, B, C, D)
            while i < len(lines):
                line = lines[i].strip()
                match = re.match(r"^([A-D])\.\s*(.+)", line)
                if match:
                    letter = match.group(1)
                    text = match.group(2).strip()
                    answers.append({"letter": letter, "text": text, "weight": 0})
                i += 1
                if line.startswith("|") or line.startswith("Правильна"):
                    break

            # Parse weights from table or "Правильна" format
            for line in lines[i:]:
                line = line.strip()

                # Table format: | A | 10 |
                table_match = re.match(r"\|\s*([A-D])\s*\|\s*(\d+)\s*\|", line)
                if table_match:
                    letter = table_match.group(1)
                    weight = int(table_match.group(2))
                    answer_weights[letter] = weight

                # "Правильна: A (10)" format
                correct_match = re.match(r"Правильна:\s*([A-D])\s*\((\d+)\)", line)
                if correct_match:
                    letter = correct_match.group(1)
                    weight = int(correct_match.group(2))
                    answer_weights[letter] = weight

            # Apply weights to answers
            for answer in answers:
                if answer["letter"] in answer_weights:
                    answer["weight"] = answer_weights[answer["letter"]]

            if question_text and answers:
                tests[current_section]["questions"].append({
                    "text": question_text,
                    "answers": answers
                })

    return tests


async def load_it_tests() -> None:
    """Load IT tests into database."""
    # Find it_tests.md file (in project root, outside container)
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "it_tests.md",  # /app/../it_tests.md
        Path("/mnt/d/projects/IT-Navigator/it_tests.md"),  # Absolute path
        Path("/app/it_tests.md"),  # Inside container
    ]

    it_tests_file = None
    for path in possible_paths:
        if path.exists():
            it_tests_file = path
            break

    if not it_tests_file.exists():
        print(f"Error: {it_tests_file} not found!")
        return

    print(f"Parsing {it_tests_file}...")
    tests_data = parse_it_tests_md(str(it_tests_file))

    async with AsyncSessionLocal() as db:
        # Get specialties
        result = await db.execute(select(Specialty))
        specialties = {s.code: s for s in result.scalars().all()}

        if not specialties:
            print("Error: No specialties found in database. Run init_db.py first!")
            return

        print(f"Found {len(specialties)} specialties")

        # Delete existing tests (cascade: results -> answers -> questions -> tests)
        print("Deleting existing test results and tests...")
        await db.execute(delete(TestResult))
        await db.execute(delete(Answer))
        await db.execute(delete(Question))
        await db.execute(delete(Test))
        await db.commit()

        # Create general test
        print("Creating general test...")
        general_test = Test(
            title="Загальний профорієнтаційний тест",
            description="Визначення схильностей до різних ІТ-спеціальностей",
            test_type=TestType.GENERAL,
            is_active=True,
        )
        db.add(general_test)
        await db.flush()

        # Add general test questions
        general_questions = tests_data["general"]["questions"]
        print(f"Adding {len(general_questions)} general questions...")

        for idx, q_data in enumerate(general_questions, 1):
            question = Question(
                test_id=general_test.id,
                text=q_data["text"],
                order=idx,
            )
            db.add(question)
            await db.flush()

            for a_data in q_data["answers"]:
                answer = Answer(
                    question_id=question.id,
                    text=a_data["text"],
                    weight=a_data["weight"],
                )
                db.add(answer)

        # Create specialized tests
        for code in ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]:
            if code not in specialties:
                print(f"Warning: Specialty {code} not found, skipping...")
                continue

            specialty = specialties[code]
            questions = tests_data[code]["questions"]

            if not questions:
                print(f"Warning: No questions found for {code}, skipping...")
                continue

            print(f"Creating specialized test for {code} ({specialty.name})...")
            spec_test = Test(
                title=f"Спеціалізований тест: {specialty.name}",
                description=f"Поглиблене тестування для спеціальності {specialty.name}",
                test_type=TestType.SPECIALIZED,
                specialty_id=specialty.id,
                is_active=True,
            )
            db.add(spec_test)
            await db.flush()

            print(f"Adding {len(questions)} questions for {code}...")
            for idx, q_data in enumerate(questions, 1):
                question = Question(
                    test_id=spec_test.id,
                    specialty_id=specialty.id,
                    text=q_data["text"],
                    order=idx,
                )
                db.add(question)
                await db.flush()

                for a_data in q_data["answers"]:
                    answer = Answer(
                        question_id=question.id,
                        text=a_data["text"],
                        weight=a_data["weight"],
                    )
                    db.add(answer)

        await db.commit()
        print("✅ IT tests loaded successfully!")


if __name__ == "__main__":
    asyncio.run(load_it_tests())
