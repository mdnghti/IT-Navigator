"""
Update existing specialties to IT specialties.
"""

import asyncio

from sqlalchemy import select

from app.db.models.specialty import Specialty
from app.db.session import AsyncSessionLocal


async def update_specialties() -> None:
    """Update specialties to IT specialties."""
    specialties_data = {
        "F1": {
            "name": "Прикладна математика",
            "description": "Математичне моделювання, аналіз даних, статистика",
        },
        "F2": {
            "name": "Інженерія програмного забезпечення",
            "description": "Розробка, тестування та підтримка програмного забезпечення",
        },
        "F3": {
            "name": "Комп'ютерні науки",
            "description": "Алгоритми, структури даних, штучний інтелект",
        },
        "F4": {
            "name": "Системний аналіз та Data Science",
            "description": "Аналіз даних, бізнес-аналітика, прогнозування",
        },
        "F5": {
            "name": "Кібербезпека",
            "description": "Захист інформації, мережева безпека, криптографія",
        },
        "F6": {
            "name": "Інформаційні системи та технології",
            "description": "Проектування та управління ІТ-системами, DevOps",
        },
        "F7": {
            "name": "Комп'ютерна інженерія",
            "description": "Апаратне забезпечення, embedded-системи, мікроконтролери",
        },
    }

    async with AsyncSessionLocal() as db:
        print("Updating specialties...")
        result = await db.execute(select(Specialty))
        specialties = {s.code: s for s in result.scalars().all()}

        for code, data in specialties_data.items():
            if code in specialties:
                specialty = specialties[code]
                specialty.name = data["name"]
                specialty.description = data["description"]
                print(f"  Updated {code}: {data['name']}")
            else:
                specialty = Specialty(code=code, **data)
                db.add(specialty)
                print(f"  Created {code}: {data['name']}")

        await db.commit()
        print("✓ Specialties updated successfully!")


if __name__ == "__main__":
    asyncio.run(update_specialties())
