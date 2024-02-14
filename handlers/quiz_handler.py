from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db_models import Quiz
from helpers.quiz_helpers import serialize_quiz


def get_quizzes(request: Request, db: Session):
    user_id = request.state.user_id
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()

    serialized_quizzes = [serialize_quiz(quiz) for quiz in quizzes]

    return JSONResponse(status_code=200, content={"data": serialized_quizzes})
