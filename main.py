from fastapi import FastAPI, Depends, Request
from http_models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import setup_cors_middleware, validate_token
from handlers.auth_handler import handle_signup, handle_login
from database.db import get_db
from handlers import quiz_handler, source_handler, question_handler
from fastapi import UploadFile, File


app = FastAPI()
setup_cors_middleware(app)
app.middleware('http')(validate_token)


@app.get("/")
async def root():
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


@app.get('/questions')
async def get_questions(request: Request, quiz_id: str, db: Session = Depends(get_db)):
    return question_handler.get_quiz_questions(request=request, quiz_id=quiz_id, db=db)


@app.put('/questions')
async def update_question(request: Request, db: Session = Depends(get_db)):
    return await question_handler.update_question(request=request, db=db)

