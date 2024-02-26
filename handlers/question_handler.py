from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Request

from database.db_models import Question, Quiz
from helpers.question_helpers import serialize_questions
from starlette.exceptions import HTTPException


def get_quiz_questions(request: Request, quiz_id: str, db: Session):
    user_id = request.state.user_id
    quiz = db.query(Quiz).filter(Quiz.user_id == user_id).first()
    if not quiz:
        return HTTPException(status_code=404, detail='Quiz not found')
    
    questions = db.query(Question).filter(Question.quiz_id == quiz_id, Question.is_accepted == True).all()
    return JSONResponse(status_code=200, content={'data': {"questions": serialize_questions(questions)}})


async def update_question(request: Request, db: Session):
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
    
    db.commit()
    
    return JSONResponse(status_code=200, content={'data': 'Update successful'})
    
    