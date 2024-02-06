from fastapi import FastAPI, Depends
from http_models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from middleware import setup_cors_middleware
from handlers.auth_handler import handle_signup
from database.db import get_db

app = FastAPI()
setup_cors_middleware(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/login")
async def login(body: LoginRequest):
    try:
        print(body)
        return JSONResponse(status_code=200, content={"login": 'success', 'user_token': '123456'})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"login": 'error'})


@app.post("/signup")
async def signup(body: SignupRequest, db: Session = Depends(get_db)):
    return await handle_signup(request=body, db=db)
