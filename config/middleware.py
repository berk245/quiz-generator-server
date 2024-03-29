from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from helpers.auth_helpers import validate_jwt
from config.cloudwatch_logger import cloudwatch_logger
from fastapi import Request
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Local development env variable is only defined locally
IS_LOCALHOST = os.getenv('LOCAL_DEVELOPMENT') is not None 

def setup_cors_middleware(app) -> None:
    middleware_params = {
        "allow_credentials": True,
        "allow_headers": ["Authorization"],
        "allow_methods": ["*"]
    }

    if IS_LOCALHOST:
        middleware_params["allow_origins"] = ['*']

    app.add_middleware(CORSMiddleware, **middleware_params)
    


async def validate_token(request, call_next) -> JSONResponse:
    try:
        print(request.url.path)
        if request.url.path not in ['/auth/signup', '/auth/login', '/auth/cypress-user', '/docs', '/openapi.json'] and request.method != 'OPTIONS':
            user_token = request.headers.get('authorization')
            user_id = validate_jwt(user_token)

            if not user_id:
                raise Exception
            # attach extracted user info to request for future access
            request.state.user_id = user_id

    except:
        cloudwatch_logger.error('Invalid or expired token')
        return JSONResponse(status_code=401,
                            content={'error': 'Invalid or expired token'},
                            headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*',
                                     'Access-Control-Allow-Methods': '*'})
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        cloudwatch_logger.error(f'Uncaught exception: {str(e)}')
        print('Uncaught exception while processing a request:', e)

    return JSONResponse(status_code=500, content={'error': 'Internal server error'},
                        headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*',
                                 'Access-Control-Allow-Methods': '*'})


async def log_request(request: Request, call_next):
    try:
        if request.method == "OPTIONS":
            # Check if it's a preflight request (OPTIONS method) and ignore it
            return await call_next(request)

        log_message = f"Received request: {request.method} {request.url}"

        if request.method == "GET" and request.query_params:
            log_message += f"\nURL parameters: {request.query_params}"

        elif request.method == "POST":
            body = await request.body()
            # Check if the content type is JSON, handle form request separately
            if "application/json" in request.headers.get("content-type", ""):
                try:
                    body_json = json.loads(body)
                    if request.url.path in ["/login", "/signup"]:
                        log_message = f"Auth request: {request.url.path}, email: {body_json.get('email')} "
                    else:
                        log_message += f"\nRequest body (JSON): {body_json}"
                except json.JSONDecodeError:
                    log_message += f"\nRequest body (JSON): Unable to parse JSON"

        cloudwatch_logger.info(log_message)

        # Call the next middleware or handler
        response = await call_next(request)
        return response

    except Exception as e:
        cloudwatch_logger.info(f'Request log failed. \n'
                               f'Exception: {str(e)}')
        # Call the next middleware or handler
        response = await call_next(request)

        return response
