from typing import Type, List
from database.db_models import Question


def serialize_questions(questions: List[Type[Question]]):
    serialized = []
    for question in questions:
        serialized.append(
            {
                "question_id": question.question_id,
                "instructions": question.instructions,
                "question_type": question.question_type,
                "question_text": question.question_text,
                "multiple_choices": question.multiple_choices,
                "correct_answer": question.correct_answer,
                "difficulty": question.difficulty,
                "score": question.score,
                "created_at": question.created_at.isoformat() if question.created_at else None,
            }
        )
    return serialized
