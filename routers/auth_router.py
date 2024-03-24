from models.auth import LoginRequest, SignupRequest
from handlers import auth_handler
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from config.db import get_db

router = APIRouter()

@router.post("/login", tags=['auth'])
async def login(body: LoginRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await auth_handler.login(request=body, db=db)


@router.post("/signup", tags=['auth'])
async def signup(body: SignupRequest, db: Session = Depends(get_db)) -> JSONResponse:
    return await auth_handler.signup(request=body, db=db)