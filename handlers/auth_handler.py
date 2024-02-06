from fastapi import HTTPException
from http_models.auth import SignupRequest
from sqlalchemy.orm import Session
from database.db_models import User
from fastapi.responses import JSONResponse
from helpers.auth_helpers import hash_password


async def handle_signup(request: SignupRequest, db: Session):
    new_user = User(email=request.email, password=hash_password(password=request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(status_code=200, content={"signup": 'success', 'user_token': '123456'})


