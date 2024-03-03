from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from fastapi import Request
from io import BytesIO

from database.db_models import Question, Quiz
from helpers.question_helpers import serialize_questions
from starlette.exceptions import HTTPException
from helpers.generate_question_helpers import get_generated_questions


def get_quiz_questions(request: Request, quiz_id: str, db: Session):
    user_id = request.state.user_id
    quiz = db.query(Quiz).filter(Quiz.user_id == user_id).first()
    if not quiz:
        return HTTPException(status_code=404, detail='Quiz not found')

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    return JSONResponse(status_code=200, content={'data': {"questions": serialize_questions(questions)}})


async def edit_question(request: Request, db: Session):
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


async def generate_questions(request: Request, db: Session):
    try:
        user_id = request.state.user_id
        question_generation_settings = await request.json()
        generated_questions = get_generated_questions(user_id=user_id,
                                                      question_generation_settings=question_generation_settings,
                                                      db=db)
        return JSONResponse(status_code=200, content={'questions': generated_questions})
    except HTTPException:
        raise


async def add_question_to_quiz(request: Request, db: Session):
    user_id = request.state.user_id

    request_data = await request.json()

    quiz_id = request_data.get('quiz_id')
    new_question_data = request_data.get('question')

    # Ensure quiz exists
    quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return HTTPException(status_code=404, detail='Quiz not found')

    # Create a Question table linked to the quiz
    _add_question_table(question_data=new_question_data, quiz_id=quiz_id, db=db)

    return JSONResponse(status_code=200, content={'data': 'Question added successfully'})


def _add_question_table(question_data: Question, quiz_id: str, db: Session):
    new_question = Question(
        quiz_id=quiz_id,
        question_type=question_data.get('question_type'),
        question_text=question_data.get('question_text'),
        multiple_choices=question_data.get('multiple_choices'),
        correct_answer=question_data.get('correct_answer'),
    )
    db.add(new_question)
    db.commit()

    return


async def get_questions_as_csv(request: Request, db: Session):
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
