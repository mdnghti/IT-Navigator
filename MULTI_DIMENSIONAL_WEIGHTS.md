# Multi-Dimensional Weight System

## Overview

The system now uses **multi-dimensional weights** where each answer contributes to ALL specialties simultaneously, not just one.

## How It Works

### Old System (Single Weight)
Each answer had one weight for one specialty:
```
Answer "32": weight = 10 → only F1 gets 10 points
```

### New System (Multi-Dimensional)
Each answer has weights for ALL 7 specialties:
```
Answer "32": {
  "F1": 10,  // Primary specialty (Математика)
  "F2": 1,   // Unrelated
  "F3": 5,   // Related (Комп. науки)
  "F4": 5,   // Related (Data Science)
  "F5": 1,   // Unrelated
  "F6": 1,   // Unrelated
  "F7": 1    // Unrelated
}
```

## Weight Distribution Logic

### Related Specialties
```python
RELATED_SPECIALTIES = {
    "F1": ["F3", "F4"],  # Математика ↔ Комп. науки, Data Science
    "F2": ["F3", "F6"],  # Інженерія ПЗ ↔ Комп. науки, Інф. системи
    "F3": ["F1", "F2", "F4"],  # Комп. науки ↔ Математика, Інженерія, Data Science
    "F4": ["F1", "F3", "F6"],  # Data Science ↔ Математика, Комп. науки, Інф. системи
    "F5": ["F2", "F6", "F7"],  # Кібербезпека ↔ Інженерія, Інф. системи, Комп. інженерія
    "F6": ["F2", "F4", "F5"],  # Інф. системи ↔ Інженерія, Data Science, Кібербезпека
    "F7": ["F2", "F5"],  # Комп. інженерія ↔ Інженерія, Кібербезпека
}
```

### Weight Calculation Rules

| Original Weight | Primary Specialty | Related Specialties | Unrelated Specialties |
|----------------|-------------------|---------------------|----------------------|
| 10 (correct)   | 10                | 5                   | 1                    |
| 5 (partial)    | 5                 | 3                   | 0                    |
| 2-3 (minor)    | 2-3               | 1                   | 0                    |
| 0 (wrong)      | 0                 | 0                   | 0                    |

## Database Schema

### Answer Model
```python
class Answer(Base):
    id: int
    question_id: int
    text: str
    weights: dict  # JSONB: {"F1": 10, "F2": 5, ...}
    weight: int    # Legacy field (kept for compatibility)
```

### Example Data
```sql
SELECT text, weights FROM answers WHERE question_id = 1;

text | weights
-----|--------
"32" | {"F1": 10, "F2": 1, "F3": 5, "F4": 5, "F5": 1, "F6": 1, "F7": 1}
"24" | {"F1": 5, "F2": 0, "F3": 3, "F4": 3, "F5": 0, "F6": 0, "F7": 0}
```

## Scoring Algorithm

### Old Algorithm
1. For each answer, add weight to ONE specialty
2. Calculate percentage per specialty
3. Recommend highest percentage

### New Algorithm
1. For each answer, add weights to ALL specialties
2. For each specialty, calculate max possible score (sum of max weights from all questions)
3. Calculate percentage: `(earned / max_possible) × 100%`
4. Recommend highest percentage

### Example Calculation

**Question 1** (F1 - Математика):
- User selects "32" → F1: +10, F3: +5, F4: +5, others: +1

**Question 2** (F5 - Кібербезпека):
- User selects correct answer → F5: +10, F2: +5, F6: +5, F7: +5, others: +1

**Final Scores**:
```
F1: 11 / 130 = 8.5%
F2: 6 / 130 = 4.6%
F3: 6 / 130 = 4.6%
F4: 6 / 130 = 4.6%
F5: 11 / 130 = 8.5%
F6: 6 / 130 = 4.6%
F7: 6 / 130 = 4.6%
```

## Benefits

1. **More Accurate**: Answers can indicate interest in multiple related fields
2. **Fairer**: All specialties are evaluated equally (13 questions × max 10 points each)
3. **Flexible**: Easy to adjust relationships between specialties
4. **Realistic**: Reflects that IT specialties overlap

## Migration

The system automatically generates multi-dimensional weights from old single-weight data using the `generate_weights()` function in `scripts/init_db.py`.

## Files Changed

- `app/db/models/answer.py` - Added `weights` JSONB field
- `app/crud/scoring.py` - Updated scoring algorithm
- `scripts/init_db.py` - Added weight generation logic
- `alembic/versions/...` - Migration to add `weights` column

## Testing

```bash
# Check weights in database
docker compose exec -T db psql -U career_user -d career_platform -c \
  "SELECT text, weights FROM answers WHERE question_id = 1;"

# Test API
curl http://localhost/api/v1/tests/general/questions

# Submit test and check results
curl -X POST http://localhost/api/v1/tests/general/submit \
  -H "Authorization: Bearer <token>" \
  -d '{"answers": [...]}'
```
