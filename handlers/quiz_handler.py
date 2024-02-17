from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db_models import Quiz
from helpers.quiz_helpers import serialize_quiz


def get_quizzes(request: Request, db: Session):
    user_id = request.state.user_id
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()

    serialized_quizzes = [serialize_quiz(quiz) for quiz in quizzes]

    return JSONResponse(status_code=200, content={"data": serialized_quizzes})


async def add_quiz(request: Request, source_file: UploadFile, db:Session):
    quiz_info = await request.form()
    new_quiz = Quiz(
        quiz_title=quiz_info.get('quiz_title'),
        quiz_description=quiz_info.get('quiz_description'),
        keywords=quiz_info.get('keywords'),
        meta_prompt=quiz_info.get('meta_prompt'),
        user_id=request.state.user_id
    )
    db.add(new_quiz)
    db.commit()
    # To-do handle documents
    db.refresh(new_quiz)

    return JSONResponse(status_code=200, content={"quiz_id": new_quiz.quiz_id})
