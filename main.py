from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.middleware import setup_cors_middleware, validate_token, log_request
from config.db import get_db
from handlers import auth_handler, quiz_handler, source_handler, question_handler
from fastapi import UploadFile, File
from config.cloudwatch_logger import cloudwatch_logger

from routers import auth_router, quiz_router

app = FastAPI()
setup_cors_middleware(app)
app.middleware('http')(validate_token)
app.middleware('http')(log_request)


app.include_router(auth_router.router, prefix="/auth")
app.include_router(quiz_router.router, prefix="/quiz")



@app.get('/sources')
async def get_sources(request: Request, db: Session = Depends(get_db)):
    return source_handler.get_sources(request=request, db=db)




@app.get('/questions')
async def get_questions(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return question_handler.get_quiz_questions(request=request, quiz_id=quiz_id, db=db)


@app.put('/questions')
async def edit_question(request: Request, db: Session = Depends(get_db)):
    return await question_handler.edit_question(request=request, db=db)


@app.post('/questions/generate')
async def generate_questions(request: Request, db: Session = Depends(get_db)):
    return await question_handler.generate_questions(request=request, db=db)


@app.post('/questions')
async def add_generated_questions_to_quiz(request: Request, db: Session = Depends(get_db)):
    return await question_handler.add_question_to_quiz(request=request, db=db)


@app.post('/questions/csv')
async def get_questions_as_csv(request: Request, db: Session = Depends(get_db)):
    return await question_handler.get_questions_as_csv(request=request, db=db)


@app.delete('/cypress-user')
async def delete_user(request: Request, db: Session = Depends(get_db)):
    return await auth_handler.delete_cypress_user(request=request, db=db)