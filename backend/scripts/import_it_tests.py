"""
Database import script for Ukrainian IT-Navigator proforientation tests.

Parses it_tests.md and seeds the database with:
- Updated specialties (F1-F7) on Ukrainian with professional descriptions.
- New General proforientation test (13 questions) with specialty weights.
- Seven new Specialized tests (10 questions each) with correct answers.
"""

import asyncio
import os
import re
import sys

# Add current and parent directory to python path to import app modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.security import get_password_hash
from app.db.models.answer import Answer
from app.db.models.question import Question
from app.db.models.result import TestResult
from app.db.models.specialty import Specialty
from app.db.models.test import Test, TestType
from app.db.models.user import User
from app.db.session import AsyncSessionLocal

# Specialty details on Ukrainian with premium descriptions
SPECIALTIES_DATA = [
    {
        "code": "F1",
        "name": "Прикладна математика",
        "description": "Аналіз та розв'язання складних задач за допомогою математичних методів, моделювання та алгоритмів.",
    },
    {
        "code": "F2",
        "name": "Інженерія програмного забезпечення",
        "description": "Проектування, розробка, тестування та підтримка складних програмних систем і додатків.",
    },
    {
        "code": "F3",
        "name": "Комп’ютерні науки",
        "description": "Теоретичні основи обчислень, розробка алгоритмів, штучний інтелект та вирішення наукоємних ІТ-задач.",
    },
    {
        "code": "F4",
        "name": "Системний аналіз та Data Science",
        "description": "Збір, обробка та аналіз великих масивів даних (Big Data), побудова прогностичних моделей та аналітика.",
    },
    {
        "code": "F5",
        "name": "Кібербезпека",
        "description": "Захист інформаційних систем, комп'ютерних мереж, програмного забезпечення та даних від кібератак і загроз.",
    },
    {
        "code": "F6",
        "name": "Інформаційні системи та технології",
        "description": "Впровадження, інтеграція та адміністрування ІТ-інфраструктур, баз даних, хмарних сервісів та бізнес-систем.",
    },
    {
        "code": "F7",
        "name": "Комп’ютерна інженерія",
        "description": "Розробка та проектування апаратного забезпечення комп'ютерів, мікроконтролерів, робототехніки та вбудованих систем.",
    },
]


def parse_general_test(content: str) -> list[dict]:
    # Find the general test section
    general_match = re.search(r'# Загальний тест \(13 питань\)(.*?)(?=# F1)', content, re.DOTALL)
    if not general_match:
        raise ValueError("General test section not found in it_tests.md")
    
    general_text = general_match.group(1)
    
    questions = []
    # Match headers of format "## Питання X (F_code — Specialty_name)"
    matches = list(re.finditer(r'## Питання (\d+)\s*\((F\d+)\s*—\s*(.*?)\)', general_text))
    
    for i, match in enumerate(matches):
        q_num = int(match.group(1))
        spec_code = match.group(2)
        
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(general_text)
        block = general_text[start_idx:end_idx].strip()
        
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        question_text = ""
        options = {}  # letter -> text
        weights = {}  # letter -> weight
        
        for line in lines:
            # Check for option line: "A. 18"
            opt_match = re.match(r'^([A-DА-Д])\.\s*(.*?)$', line)
            if opt_match:
                letter = opt_match.group(1).upper()
                letter_map = {'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D'}
                letter = letter_map.get(letter, letter)
                options[letter] = opt_match.group(2).strip()
                continue
            
            # Check for weight table line: "| C | 10 |"
            weight_match = re.match(r'^\|\s*([A-DА-Д])\s*\|\s*(\d+)\s*\|$', line)
            if weight_match:
                letter = weight_match.group(1).upper()
                letter_map = {'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D'}
                letter = letter_map.get(letter, letter)
                weights[letter] = int(weight_match.group(2))
                continue
            
            # If not option or table line or separator, it's part of question text
            if not line.startswith('|') and not line.startswith('---'):
                if question_text:
                    question_text += "\n" + line
                else:
                    question_text = line
                    
        questions.append({
            "number": q_num,
            "specialty": spec_code,
            "text": question_text,
            "answers": [
                {"text": options[let], "weight": weights.get(let, 0)}
                for let in sorted(options.keys())
            ]
        })
    return questions


def parse_specialized_tests(content: str) -> list[dict]:
    # Split by specialty headers e.g. "# F1 — Прикладна математика (10 питань)"
    sections = re.split(r'# (F\d+)\s*—\s*(.*?)\s*\(\d+\s*питань\)', content)
    specialized_data = []
    
    for i in range(1, len(sections), 3):
        spec_code = sections[i]
        section_content = sections[i+2]
        
        # Split by question numbers "1.", "2." etc. at the start of a line
        q_matches = list(re.finditer(r'(?:^|\n)\s*(\d+)\.\s*(.*?)(?=\n\s*\d+\.\s*|$)', section_content, re.DOTALL))
        
        for q_match in q_matches:
            q_num = int(q_match.group(1))
            q_block = q_match.group(2).strip()
            
            # Parse the correct answer line: "Правильна: C (10)" or "Правильна: 7 (10)"
            correct_match = re.search(r'Правильна:\s*(.*?)\s*\((\d+)\)', q_block)
            if not correct_match:
                correct_match = re.search(r'Правильна:\s*(.*?)$', q_block, re.MULTILINE)
                if correct_match:
                    correct_val = correct_match.group(1).strip()
                    correct_weight = 10
                else:
                    correct_val = ""
                    correct_weight = 10
            else:
                correct_val = correct_match.group(1).strip()
                correct_weight = int(correct_match.group(2))
            
            # Remove "Правильна: ..." line from q_block
            q_block_clean = re.sub(r'Правильна:.*$', '', q_block, flags=re.MULTILINE).strip()
            
            options = {}
            question_text = ""
            
            lines = [l.strip() for l in q_block_clean.split('\n') if l.strip()]
            for line in lines:
                # Check for single-line options: "A. 30 B. 36 C. 48 D. 54"
                if re.search(r'[A-DА-Д]\..*?[A-DА-Д]\.', line):
                    opt_matches = re.findall(r'([A-DА-Д])\.\s*(.*?)(?=\s+[A-DА-Д]\.|\s*|$)', line)
                    for opt_match in opt_matches:
                        letter = opt_match[0].upper()
                        letter_map = {'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D'}
                        letter = letter_map.get(letter, letter)
                        options[letter] = opt_match[1].strip()
                    continue
                
                # Check for multiline option: "A. Спадає"
                opt_match = re.match(r'^([A-DА-Д])\.\s*(.*?)$', line)
                if opt_match:
                    letter = opt_match.group(1).upper()
                    letter_map = {'А': 'A', 'В': 'B', 'С': 'C', 'Д': 'D'}
                    letter = letter_map.get(letter, letter)
                    options[letter] = opt_match.group(2).strip()
                    continue
                
                # Otherwise it's question text
                if question_text:
                    question_text += "\n" + line
                else:
                    question_text = line
            
            # Special case for no options like "Яке число зайве: 2, 4, 6, 7, 8"
            if not options and ',' in question_text:
                # Match numbers/words separated by commas
                nums = [n.strip() for n in question_text.split(':')[-1].split(',')]
                if nums and len(nums) > 1:
                    options = {str(n): str(n) for n in nums}
            
            # Map options to answers with weight
            answers = []
            if options:
                for opt_key, opt_text in options.items():
                    # Check if this option is the correct one (compares key or text)
                    is_correct = (opt_key == correct_val) or (opt_text == correct_val)
                    answers.append({
                        "text": opt_text,
                        "weight": correct_weight if is_correct else 0
                    })
            
            specialized_data.append({
                "specialty": spec_code,
                "number": q_num,
                "text": question_text,
                "answers": answers
            })
            
    return specialized_data


async def main() -> None:
    # Locate it_tests.md
    content = ""
    for file_path in ["./it_tests.md", "../it_tests.md", "it_tests.md"]:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"✓ Found it_tests.md at '{file_path}'")
            break
            
    if not content:
        print("✗ Error: Could not find it_tests.md in project directories.")
        sys.exit(1)
        
    print("Parsing general test questions...")
    general_questions = parse_general_test(content)
    print(f"✓ Parsed {len(general_questions)} general questions.")
    
    print("Parsing specialized test questions...")
    specialized_questions = parse_specialized_tests(content)
    print(f"✓ Parsed {len(specialized_questions)} specialized questions.")

    async with AsyncSessionLocal() as db:
        # Clear existing data in correct dependency order
        print("\nClearing old test-related data from the database...")

        # 1. Clear test results
        await db.execute(text("DELETE FROM test_results"))

        # 2. Clear answers
        await db.execute(text("DELETE FROM answers"))

        # 3. Clear questions
        await db.execute(text("DELETE FROM questions"))

        # 4. Clear tests
        await db.execute(text("DELETE FROM tests"))

        # 5. Clear specialties
        await db.execute(text("DELETE FROM specialties"))

        await db.commit()
        print("✓ Database cleaned successfully!")
        
        # Seed Specialties
        print("\nCreating new IT specialties...")
        specialties = {}
        for spec_data in SPECIALTIES_DATA:
            specialty = Specialty(
                code=spec_data["code"],
                name=spec_data["name"],
                description=spec_data["description"]
            )
            db.add(specialty)
            await db.flush()
            specialties[spec_data["code"]] = specialty
            print(f"  + Created specialty: {spec_data['name']} ({spec_data['code']})")
            
        # Seed General Test
        print("\nCreating General proforientation test...")
        general_test = Test(
            title="Загальний профорієнтаційний тест",
            description="Визначення схильності до різних IT-спеціальностей на основі ваших інтересів та логічного мислення.",
            test_type=TestType.GENERAL,
            is_active=True
        )
        db.add(general_test)
        await db.flush()
        
        for q_data in general_questions:
            question = Question(
                test_id=general_test.id,
                specialty_id=specialties[q_data["specialty"]].id,
                text=q_data["text"],
                order=q_data["number"]
            )
            db.add(question)
            await db.flush()
            
            for ans_data in q_data["answers"]:
                answer = Answer(
                    question_id=question.id,
                    text=ans_data["text"],
                    weight=ans_data["weight"]
                )
                db.add(answer)
        print("✓ General test created successfully with 13 questions!")
        
        # Seed Specialized Tests
        print("\nCreating Specialized tests...")
        
        # Create a test for each specialty
        spec_tests = {}
        for code, spec in specialties.items():
            test = Test(
                title=f"Спеціалізований тест: {spec.name}",
                description=f"Детальна перевірка знань та навичок у напрямку {spec.name}.",
                test_type=TestType.SPECIALIZED,
                specialty_id=spec.id,
                is_active=True
            )
            db.add(test)
            await db.flush()
            spec_tests[code] = test
            print(f"  + Created test: Спеціалізований тест: {spec.name}")
            
        # Add questions to specialized tests
        for q_data in specialized_questions:
            code = q_data["specialty"]
            question = Question(
                test_id=spec_tests[code].id,
                specialty_id=specialties[code].id,
                text=q_data["text"],
                order=q_data["number"]
            )
            db.add(question)
            await db.flush()
            
            for ans_data in q_data["answers"]:
                answer = Answer(
                    question_id=question.id,
                    text=ans_data["text"],
                    weight=ans_data["weight"]
                )
                db.add(answer)
                
        # Commit transaction
        await db.commit()
        print("\n✓ Database successfully populated with the new IT proforientation tests!")
        print("  - 7 Specialties configured")
        print("  - 1 General Test (13 questions) created")
        print("  - 7 Specialized Tests (70 questions in total) created")


if __name__ == "__main__":
    asyncio.run(main())
