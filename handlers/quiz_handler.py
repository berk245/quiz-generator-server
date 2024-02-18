from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db_models import Quiz
from helpers.quiz_helpers import serialize_quiz
from . import  source_handler

def get_quizzes(request: Request, db: Session):
    user_id = request.state.user_id
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()

    serialized_quizzes = [serialize_quiz(quiz) for quiz in quizzes]

    return JSONResponse(status_code=200, content={"data": serialized_quizzes})


async def add_quiz(request: Request, source_file: UploadFile, db: Session):
    quiz_info = await request.form()

    # Create quiz
    new_quiz = Quiz(
        quiz_title=quiz_info.get('quiz_title'),
        quiz_description=quiz_info.get('quiz_description'),
        keywords=quiz_info.get('keywords'),
        meta_prompt=quiz_info.get('meta_prompt'),
        user_id=request.state.user_id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    # Add source
    new_source = source_handler.add_source(user_id=request.state.user_id,
                                           file=source_file,
                                           db=db)

    # Connect the source with the quiz by creating a QuizSource table
    source_handler.add_quiz_source(new_source=new_source, quiz_id=new_quiz.quiz_id, db=db)

    return JSONResponse(status_code=200, content={"quiz_id": new_quiz.quiz_id})

