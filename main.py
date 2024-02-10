from fastapi import FastAPI, Depends
from http_models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import setup_cors_middleware
from handlers.auth_handler import handle_signup, handle_login
from database.db import get_db

app = FastAPI()
setup_cors_middleware(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/login")
async def login(body: LoginRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await handle_login(request=body, db=db)


@app.post("/signup")
async def signup(body: SignupRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await handle_signup(request=body, db=db)
