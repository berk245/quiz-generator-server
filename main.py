from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from config.middleware import setup_cors_middleware, validate_token, log_request
from config.db import get_db
from handlers import source_handler

from routers import auth_router, quiz_router, questions_router

app = FastAPI()
setup_cors_middleware(app)
app.middleware('http')(validate_token)
app.middleware('http')(log_request)


app.include_router(auth_router.router, prefix="/auth")
app.include_router(quiz_router.router, prefix="/quiz")
app.include_router(questions_router.router, prefix="/questions")


@app.get('/sources')
async def get_sources(request: Request, db: Session = Depends(get_db)):
    return source_handler.get_sources(request=request, db=db)
