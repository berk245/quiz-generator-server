from fastapi import FastAPI
from http_models.auth import LoginRequest, SignupRequest
from fastapi.responses import JSONResponse
from middleware import setup_cors_middleware


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
async def signup(body: SignupRequest):
    try:
        print(body)
        return JSONResponse(status_code=200, content={"login": 'success', 'user_token': '123456'})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"login": 'error'})
