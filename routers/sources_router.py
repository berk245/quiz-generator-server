from handlers import source_handler
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from config.db import get_db

router = APIRouter()

@router.get('/', tags=['sources'])
async def get_sources(request: Request, db: Session = Depends(get_db)):
    return source_handler.get_sources(request=request, db=db)