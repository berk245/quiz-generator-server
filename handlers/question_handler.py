from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from fastapi import Request
from io import BytesIO

from models.db_models import Question, Quiz
from helpers.question_helpers import serialize_questions, create_question_table
from starlette.exceptions import HTTPException
from helpers.generate_question_helpers import get_generated_questions
from cloudwatch_logger import cloudwatch_logger


def get_quiz_questions(request: Request, quiz_id: str, db: Session):
    try:
        user_id = request.state.user_id
        quiz = db.query(Quiz).filter(Quiz.user_id == user_id).first()
        if not quiz:
            return HTTPException(status_code=404, detail='Quiz not found')

        questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
        return JSONResponse(status_code=200, content={'data': {"questions": serialize_questions(questions)}})
    except Exception as e:
        cloudwatch_logger.error(f'Error while getting quiz questions for quiz id: {quiz_id}\n'
                                f'Details: {str(e)}')
        raise e


async def edit_question(request: Request, db: Session):
    try:
        user_id = request.state.user_id
        updated_question = await request.json()

        query = (
            db.query(Question)
            .join(Quiz, Question.quiz_id == Quiz.quiz_id)
            .filter(Question.question_id == updated_question.get('question_id'), Quiz.user_id == user_id)
        )

        # Attempt to get the question
        db_question = query.first()
        if not db_question:
            raise HTTPException(status_code=404, detail="Question not found or you do not have permission to update it")

        # Update the question fields
        for field, value in updated_question.items():
            setattr(db_question, field, value)

        # Flag the question as edited for statistics
        db_question.is_edited = True
        db.commit()

        return JSONResponse(status_code=200, content={'data': 'Update successful'})
    except Exception as e:
        cloudwatch_logger.error(f'Error while updating question.'
                                f'Details: {str(e)}')
        raise e


async def generate_questions(request: Request, db: Session):
    try:
        user_id = request.state.user_id
        question_generation_settings = await request.json()
        generated_questions = get_generated_questions(user_id=user_id,
                                                      question_generation_settings=question_generation_settings,
                                                      db=db)
        
        return JSONResponse(status_code=200, content={'questions': generated_questions})
    except Exception as e:
        cloudwatch_logger.error(f'Error while generating questions: {str(e)}')
        raise


async def add_question_to_quiz(request: Request, db: Session):
    try:
        user_id = request.state.user_id

        request_data = await request.json()

        quiz_id = request_data.get('quiz_id')
        new_question_data = request_data.get('question')

        # Ensure quiz exists
        quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()
        if not quiz:
            return HTTPException(status_code=404, detail='Quiz not found')

        # Create a Question table linked to the quiz
        create_question_table(question_data=new_question_data, quiz_id=quiz_id, db=db)

        return JSONResponse(status_code=200, content={'data': 'Question added successfully'})
    except Exception as e:
        cloudwatch_logger.error(f'Error adding question to quiz: {str(e)}')
        raise


async def get_questions_as_csv(request: Request, db: Session):
    try:
        questions = await request.json()
        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(questions)
        df = df.rename(columns={
            'question_text': 'Question Text',
            'correct_answer': 'Correct Answer',
            'multiple_choices': 'Multiple Choices'
        })
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)

        return StreamingResponse(iter([csv_buffer.getvalue()]), media_type="text/csv",
                                 headers={'Content-Disposition': 'attachment; filename=output.csv'})
    except Exception as e:
        cloudwatch_logger.error(f'Error while exporting questions as CSV: {str(e)}')
        raise
