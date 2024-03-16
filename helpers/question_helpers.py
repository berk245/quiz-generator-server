from typing import Type, List
from models.db_models import Question
from sqlalchemy.orm import Session


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


def create_question_table(question_data: Question, quiz_id: str, db: Session):
    new_question = Question(
        quiz_id=quiz_id,
        question_type=question_data.get('question_type'),
        question_text=question_data.get('question_text'),
        multiple_choices=question_data.get('multiple_choices'),
        correct_answer=question_data.get('correct_answer'),
        difficulty=question_data.get('difficulty'),
        score=question_data.get('score'),
    )
    db.add(new_question)
    db.commit()

    return
