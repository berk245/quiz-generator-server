from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from helpers.auth_helpers import validate_jwt


def setup_cors_middleware(app) -> None:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=['*'],
        allow_credentials=True,
        allow_headers=['*'],
        allow_methods=['*']
    )


async def validate_token(request, call_next) -> JSONResponse:
    try:
        if request.url.path not in ['/signup', '/login'] and request.method != 'OPTIONS':
            user_token = request.headers.get('authorization')
            user_id = validate_jwt(user_token)

            if not user_id:
                raise Exception
            # attach extracted user info to request for future access
            request.state.user_id = user_id

    except:
        return JSONResponse(status_code=401,
                            content={'error': 'Invalid or expired token'},
                            headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*',
                                     'Access-Control-Allow-Methods': '*'})
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print('Uncaught exception while processing a request:', e)

    return JSONResponse(status_code=500, content={'error': 'Internal server error'},
                        headers={'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*',
                                 'Access-Control-Allow-Methods': '*'})
