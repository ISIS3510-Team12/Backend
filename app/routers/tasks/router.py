from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db import get_db
from app.models import Task, User

router = APIRouter(
    prefix="/tasks",
)
