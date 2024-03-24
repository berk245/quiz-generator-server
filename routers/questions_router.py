from handlers import question_handler
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, File
from config.db import get_db

router = APIRouter()


@router.get('/')
async def get_questions(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return question_handler.get_quiz_questions(request=request, quiz_id=quiz_id, db=db)


@router.put('/')
async def edit_question(request: Request, db: Session = Depends(get_db)):
    return await question_handler.edit_question(request=request, db=db)


@router.post('/')
async def add_generated_questions_to_quiz(request: Request, db: Session = Depends(get_db)):
    return await question_handler.add_question_to_quiz(request=request, db=db)


@router.post('/generate')
async def generate_questions(request: Request, db: Session = Depends(get_db)):
    return await question_handler.generate_questions(request=request, db=db)


@router.post('/export')
async def get_questions_as_csv(request: Request, db: Session = Depends(get_db)):
    return await question_handler.get_questions_as_csv(request=request, db=db)