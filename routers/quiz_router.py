from models.auth import LoginRequest, SignupRequest
from handlers import quiz_handler
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request, UploadFile, File
from config.db import get_db

router = APIRouter()

@router.get('/all')
async def get_quizzes(request: Request, db: Session = Depends(get_db)):
    return quiz_handler.get_quizzes(request=request, db=db)


@router.post('/')
async def post_quiz(request: Request,
                    source_file: UploadFile = File(...),
                    db: Session = Depends(get_db)):
    return await quiz_handler.add_quiz(request=request, source_file=source_file, db=db)

@router.get('/')
async def get_quiz(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return quiz_handler.get_quiz_info(request=request, quiz_id=quiz_id, db=db)


@router.delete('/')
async def delete_quiz(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return quiz_handler.delete_quiz(request=request, quiz_id=quiz_id, db=db)
