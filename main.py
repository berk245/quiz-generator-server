from fastapi import FastAPI, Depends, Request
from http_models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import setup_cors_middleware, validate_token
from handlers.auth_handler import handle_signup, handle_login
from database.db import get_db
from handlers import quiz_handler

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


@app.get('/quiz')
async def get_quizzes(request: Request, db: Session = Depends(get_db)):
    return quiz_handler.get_quizzes(request=request, db=db)
