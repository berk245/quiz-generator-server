from fastapi import HTTPException, Request
from models.auth import SignupRequest, LoginRequest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.db_models import User
from fastapi.responses import JSONResponse
from helpers.auth_helpers import hash_password, verify_password, create_jwt, is_signup_data_valid
from config.cloudwatch_logger import cloudwatch_logger
import os


async def signup(request: SignupRequest, db: Session):
    try:
        if not is_signup_data_valid(request=request):
            raise HTTPException(status_code=400, detail="Bad request.")
        
        new_user = User(email=request.email, password=hash_password(password=request.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(status_code=200, content={"signup": 'success'})
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Email already exists.")


async def login(request: LoginRequest, db: Session):
    login_user = db.query(User).filter(User.email == request.email).first()

    if login_user and verify_password(input_password=request.password, hashed_password=login_user.password):
        return JSONResponse(status_code=200, content={"login": 'success', 'user_token': create_jwt(login_user)})
    else:
        # Invalid email or password
        raise HTTPException(status_code=404, detail="Invalid email or password.")


async def delete_cypress_user(request: Request, db: Session):
    try:
        user_to_delete = db.query(User).filter(User.email == os.getenv('CYPRESS_TEST_USER')).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            cloudwatch_logger.info(f'Cypress user successfully deleted.')
            return JSONResponse(status_code=200, content='User successfully deleted')
        else:
            return HTTPException(status_code=404, detail='Quiz not found or user not authorized.')
    
    except Exception as e:
        cloudwatch_logger.error(f'Error while deleting quiz\n'
                                f'Details: {str(e)}')
        raise e
    