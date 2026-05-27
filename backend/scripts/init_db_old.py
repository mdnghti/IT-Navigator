"""
Database initialization script.

Creates initial data:
- Admin user
- Specialties (F1-F7)
- Sample general test with questions
"""

import asyncio

from app.core.security import get_password_hash
from app.db.models.specialty import Specialty
from app.db.models.user import User
from app.db.session import AsyncSessionLocal


async def init_db() -> None:
    """Initialize database with sample data."""
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
        specialties_data = [
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

        specialties = {}
        for spec_data in specialties_data:
            specialty = Specialty(**spec_data)
            db.add(specialty)
            await db.flush()
            specialties[spec_data["code"]] = specialty

        await db.commit()
        print("✓ Database initialized successfully!")
        print("\nAdmin credentials:")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("\nAccess admin panel at: http://localhost:8000/admin")
        print("\nNext step: Run 'python scripts/load_it_tests.py' to load test questions")


if __name__ == "__main__":
    asyncio.run(init_db())
