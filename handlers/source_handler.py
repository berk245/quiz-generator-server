from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db_models import Source, QuizSource
# from helpers.quiz_helpers import serialize_quiz


def get_sources(request: Request, db: Session):
    user_id = request.state.user_id
    sources = db.query(Source).filter(Source.user_id == user_id).all()

    return JSONResponse(status_code=200, content={"data": sources})


def add_source_table(user_id: str, file: UploadFile, file_hash: str, db: Session):
    new_source = Source(
        file_name=file.filename,
        user_id=user_id,
        file_hash=file_hash
    )

    db.add(new_source)
    db.commit()

    db.refresh(new_source)

    return new_source


def add_quiz_source_table(new_source: Source, quiz_id: int, db: Session):
    new_quiz_source = QuizSource(
        source_id=new_source.source_id,
        quiz_id=quiz_id,
    )

    db.add(new_quiz_source)
    db.commit()

    db.refresh(new_quiz_source)

    return new_quiz_source
