from dotenv import load_dotenv
from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette.datastructures import FormData
from starlette.exceptions import HTTPException

from models.db_models import Quiz
from helpers.quiz_helpers import serialize_quiz

from . import source_handler
from helpers.quiz_helpers import get_file_hash
from helpers.vectorstore_helpers import add_quiz_to_vectorstore
from config.cloudwatch_logger import cloudwatch_logger


load_dotenv()


def get_quizzes(request: Request, db: Session):
    try:
        user_id = request.state.user_id
        quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()

        serialized_quizzes = [serialize_quiz(quiz) for quiz in quizzes]

        return JSONResponse(status_code=200, content={"data": serialized_quizzes})
    except Exception as e:
        cloudwatch_logger.error(f'Error while accessing user {user_id} quizzes\n'
                                f'Details: {str(e)}')
        raise e


async def add_quiz(request: Request, source_file: UploadFile, db: Session):
    try:

        user_id = request.state.user_id
        quiz_info = await request.form()
        file_hash = get_file_hash(source_file.file)

        cloudwatch_logger.info('New quiz request received.\n'
                               f'User id: {user_id}\n'
                               f'Quiz title: {quiz_info.get("quiz_title")} \n'
                               f'File: {source_file.filename}, size: {source_file.size} \n'
                               )

        # Create DB tables
        new_quiz = _add_quiz_table(quiz_info=quiz_info, user_id=user_id, db=db)
        new_source = source_handler.add_source_table(user_id=user_id, file=source_file, file_hash=file_hash,
                                                     db=db)
        source_handler.add_quiz_source_table(new_source=new_source, quiz_id=new_quiz.quiz_id, db=db)
        
        await add_quiz_to_vectorstore(source_file=source_file, new_quiz=new_quiz, file_hash=file_hash)
        cloudwatch_logger.info(f"Quiz created successfully. Quiz ID: {new_quiz.quiz_id}")
        return JSONResponse(status_code=200, content={"quiz_id": new_quiz.quiz_id})

    except Exception as e:
        cloudwatch_logger.error('Error while creating quiz.\n'
                                f'Exception: {str(e)}')
        _delete_quiz_from_db(new_quiz, db)
        source_handler.delete_source(new_source, db)
        raise HTTPException(status_code=500, detail='Internal server error')


def delete_quiz(request: Request, quiz_id: str, db: Session):
    try:
        cloudwatch_logger.info(f'Delete request received: Quiz ID: {quiz_id}')
        user_id = request.state.user_id
        quiz_to_delete = db.query(Quiz).filter(Quiz.quiz_id == quiz_id, Quiz.user_id == user_id).first()
        if quiz_to_delete:
            db.delete(quiz_to_delete)
            db.commit()
            return JSONResponse(status_code=200, content='Quiz successfully deleted')
        else:
            return HTTPException(status_code=404, detail='Quiz not found or user not authorized.')
    except Exception as e:
        cloudwatch_logger.error(f'Error while deleting quiz\n'
                                f'Details: {str(e)}')
        raise e


def get_quiz_info(request: Request, quiz_id: str, db: Session):
    try:
        user_id = request.state.user_id

        quiz = db.query(Quiz).filter(Quiz.user_id == user_id,
                                     Quiz.quiz_id == quiz_id).first()

        if not quiz:
            raise HTTPException(detail='Quiz not found', status_code=404)

        quiz_sources = source_handler.get_quiz_sources(quiz_id=quiz_id, db=db)

        return JSONResponse(status_code=200, content={'data': {"quiz": serialize_quiz(quiz), "sources": quiz_sources}})
    except Exception as e:
        cloudwatch_logger.error(f'Error while accessing quiz info\n'
                                f'Details: {str(e)}')
        raise e


def _add_quiz_table(quiz_info: FormData, user_id, db: Session):
    new_quiz = Quiz(
        quiz_title=quiz_info.get('quiz_title'),
        quiz_description=quiz_info.get('quiz_description'),
        keywords=quiz_info.get('keywords'),
        meta_prompt=quiz_info.get('meta_prompt'),
        user_id=user_id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return new_quiz


def _delete_quiz_from_db(quiz: Quiz, db: Session):
    to_delete = db.query(Quiz).filter(Quiz.quiz_id == quiz.quiz_id).first()
    if to_delete:
        db.delete(to_delete)
        db.commit()
    
    return
