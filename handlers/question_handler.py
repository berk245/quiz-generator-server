from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db_models import Question
from helpers.question_helpers import serialize_questions


def get_quiz_questions(quiz_id: str, db: Session):
    questions = db.query(Question).filter(Question.quiz_id == quiz_id, Question.is_accepted == True).all()
    return JSONResponse(status_code=200, content={'data': {"questions": serialize_questions(questions)}})
