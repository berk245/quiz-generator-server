from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Request

from database.db_models import Question, Quiz
from helpers.question_helpers import serialize_questions
from starlette.exceptions import HTTPException

import time

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
    user_id = request.state.user_id
    
    question_generation_settings = await request.json()
    amount = question_generation_settings.get('amount')
    quiz_id= question_generation_settings.get('quiz_id')
    instructions = question_generation_settings.get('instructions')
    
    # Add a check for ensuring the user is authorized to genreate questions 
    # in this quiz. Ensure quiz ownership!
        
    if amount == None or quiz_id == None:
        raise HTTPException(status_code=400, detail="Bad request. Check for amount and quiz id.")
        
    
    questions = [
    {   
        'question_id': 1,
        'question_text': 'Who was the king of France before the French Revolution?',
        'correct_answer': 'Louis XVI',
        'multiple_choices': 'Napoleon Bonaparte, Marie Antoinette, Maximilien Robespierre, Louis XVI',
        'question_type': 'multi'

    },
    {'question_id': 2,
        'question_text': 'What event marked the beginning of the French Revolution in 1789?',
        'correct_answer': 'The Storming of the Bastille',
        'multiple_choices': 'The Reign of Terror, The Declaration of the Rights of Man, The Storming of the Bastille, The Tennis Court Oath',
            'question_type': 'multi'
    },
    {'question_id': 3,
        'question_text': 'Which social class primarily led the French Revolution?',
        'correct_answer': 'The Third Estate',
        'multiple_choices': 'The First Estate, The Second Estate, The Third Estate, The Fourth Estate',
            'question_type': 'multi'
    },
    {'question_id': 4,
        'question_text': 'Who wrote "The Rights of Man" during the French Revolution?',
        'correct_answer': 'Thomas Paine',
        'multiple_choices': 'Jean-Jacques Rousseau, Voltaire, Maximilien Robespierre, Thomas Paine',
            'question_type': 'multi'
    },
    {'question_id': 5,
        'question_text': 'In which year did the French Revolution end?',
        'correct_answer': '1799',
        'multiple_choices': '1789, 1792, 1799, 1804',
            'question_type': 'multi'
    },
]
    time.sleep(3)
    return JSONResponse(status_code=200, content={'questions': questions})
    
    
async def add_question_to_quiz(request: Request, db: Session):
    user_id = request.state.user_id
    
    request_data = await request.json()
    
    quiz_id = request_data.get('quiz_id')
    new_question_data= request_data.get('question')
    
    # Ensure quiz exists
    quiz = db.query(Quiz).filter(Quiz.user_id == user_id, Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return HTTPException(status_code=404, detail='Quiz not found')
    
    # Create a Question table linked to the quiz
    _add_question_table(question_data=new_question_data, quiz_id=quiz_id, db=db)
    
    return JSONResponse(status_code=200, content={'data': 'Question added successfully'})


def _add_question_table(question_data: Question, quiz_id: str, db:Session):
    new_question = Question(
        quiz_id = quiz_id,
        question_type = question_data.get('question_type'),
        question_text = question_data.get('question_text'),
        multiple_choices = question_data.get('multiple_choices'),
        correct_answer = question_data.get('correct_answer'), 
    )
    db.add(new_question)
    db.commit()
    
    return