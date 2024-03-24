from fastapi import FastAPI
from config.middleware import setup_cors_middleware, validate_token, log_request

from routers import auth_router, quiz_router, questions_router, sources_router

app = FastAPI()
setup_cors_middleware(app)
app.middleware('http')(validate_token)
app.middleware('http')(log_request)


app.include_router(auth_router.router, prefix="/auth")
app.include_router(quiz_router.router, prefix="/quiz")
app.include_router(questions_router.router, prefix="/questions")
app.include_router(sources_router.router, prefix='/sources')
