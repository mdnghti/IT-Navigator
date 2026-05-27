"""
Generate multi-dimensional weights from single-weight data.

This script converts old single-weight format to new multi-dimensional format
where each answer has weights for all 7 specialties.
"""

# Define related specialties (which specialties are similar)
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
    """
    Generate multi-dimensional weights from single weight.

    Args:
        primary_specialty: The main specialty for this question (F1-F7)
        single_weight: Original weight (0-10)

    Returns:
        Dictionary with weights for all specialties
    """
    weights = {}
    related = RELATED_SPECIALTIES.get(primary_specialty, [])

    for specialty in ALL_SPECIALTIES:
        if specialty == primary_specialty:
            # Primary specialty gets the full weight
            weights[specialty] = single_weight
        elif specialty in related:
            # Related specialties get 30-50% of the weight
            if single_weight >= 10:
                weights[specialty] = 5
            elif single_weight >= 5:
                weights[specialty] = 3
            elif single_weight >= 2:
                weights[specialty] = 1
            else:
                weights[specialty] = 0
        else:
            # Unrelated specialties get minimal weight
            if single_weight >= 10:
                weights[specialty] = 1
            else:
                weights[specialty] = 0

    return weights


def convert_question_data(question_data: dict) -> dict:
    """
    Convert question from old format to new format with multi-dimensional weights.

    Old format:
    {
        "text": "Question text",
        "specialty": "F1",
        "answers": [
            {"text": "Answer 1", "weight": 10},
            {"text": "Answer 2", "weight": 5},
        ]
    }

    New format:
    {
        "text": "Question text",
        "specialty": "F1",
        "answers": [
            {"text": "Answer 1", "weights": {"F1": 10, "F2": 1, "F3": 5, ...}},
            {"text": "Answer 2", "weights": {"F1": 5, "F2": 0, "F3": 3, ...}},
        ]
    }
    """
    primary_specialty = question_data["specialty"]
    new_question = {
        "text": question_data["text"],
        "specialty": primary_specialty,
        "answers": []
    }

    for answer in question_data["answers"]:
        new_answer = {
            "text": answer["text"],
            "weights": generate_weights(primary_specialty, answer["weight"])
        }
        new_question["answers"].append(new_answer)

    return new_question


if __name__ == "__main__":
    # Test the function
    test_question = {
        "text": "Яке число має бути наступним у ряду: 2, 4, 8, 16, ?",
        "specialty": "F1",
        "answers": [
            {"text": "18", "weight": 0},
            {"text": "24", "weight": 5},
            {"text": "32", "weight": 10},
            {"text": "36", "weight": 0},
        ],
    }

    converted = convert_question_data(test_question)
    print("Original question:")
    print(f"  Specialty: {test_question['specialty']}")
    print(f"  Text: {test_question['text']}")
    print("\nConverted answers:")
    for answer in converted["answers"]:
        print(f"  {answer['text']}: {answer['weights']}")
