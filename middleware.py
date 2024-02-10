from fastapi.middleware.cors import CORSMiddleware


def setup_cors_middleware(app) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_headers=['*'],
        allow_methods=['*']
    )
    