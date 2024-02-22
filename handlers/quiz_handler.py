from dotenv import load_dotenv
from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from database.db_models import Quiz
from helpers.quiz_helpers import serialize_quiz

from . import source_handler
from helpers.quiz_helpers import get_file_hash
from helpers.vectorstore_helpers import add_quiz_to_vectorstore


def get_quizzes(request: Request, db: Session):
    user_id = request.state.user_id
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()

    serialized_quizzes = [serialize_quiz(quiz) for quiz in quizzes]

    return JSONResponse(status_code=200, content={"data": serialized_quizzes})


async def add_quiz(request: Request, source_file: UploadFile, db: Session):
    load_dotenv()
    try:
        quiz_info = await request.form()
        file_hash = get_file_hash(source_file.file)
        
        # Create quiz in DB
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

        # Create source in DB
        new_source = source_handler.add_source(user_id=request.state.user_id, file=source_file, file_hash=file_hash,
                                               db=db)
        # Connect the source with the quiz by creating a QuizSource table
        source_handler.add_quiz_source(new_source=new_source, quiz_id=new_quiz.quiz_id, db=db)
        
        add_quiz_to_vectorstore(source_file=source_file, new_quiz=new_quiz, file_hash=file_hash)
        return JSONResponse(status_code=200, content={"quiz_id": new_quiz.quiz_id})

    except Exception as e:
        # Todo: implement solid rollback method
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail='Internal server error')
