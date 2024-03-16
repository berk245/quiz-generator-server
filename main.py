from fastapi import FastAPI, Depends, Request
from models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import setup_cors_middleware, validate_token, log_request
from handlers.auth_handler import handle_signup, handle_login
from database.db import get_db
from handlers import quiz_handler, source_handler, question_handler
from fastapi import UploadFile, File
from cloudwatch_logger import cloudwatch_logger

app = FastAPI()
setup_cors_middleware(app)
app.middleware('http')(validate_token)
app.middleware('http')(log_request)


@app.get("/")
async def root():
    cloudwatch_logger.info('This is an info log. Letsgo')
    return {"message": "Hello World"}


@app.post("/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await handle_login(request=body, db=db)


@app.post("/signup")
async def signup(body: SignupRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await handle_signup(request=body, db=db)


@app.get('/quizzes')
async def get_quizzes(request: Request, db: Session = Depends(get_db)):
    return quiz_handler.get_quizzes(request=request, db=db)


@app.post('/quizzes')
async def post_quiz(request: Request,
                    source_file: UploadFile = File(...),
                    db: Session = Depends(get_db)):
    return await quiz_handler.add_quiz(request=request, source_file=source_file, db=db)


@app.get('/sources')
async def get_sources(request: Request, db: Session = Depends(get_db)):
    return source_handler.get_sources(request=request, db=db)


@app.get('/quiz')
async def get_quiz(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return quiz_handler.get_quiz_info(request=request, quiz_id=quiz_id, db=db)


@app.delete('/quiz')
async def delete_quiz(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return quiz_handler.delete_quiz(request=request, quiz_id=quiz_id, db=db)


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
