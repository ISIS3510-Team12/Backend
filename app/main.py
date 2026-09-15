from fastapi import Depends, FastAPI
from sqlmodel import Session, text
from app.routers.s3.router import router as s3_router
from app.routers.auth.router import router as auth_router
from app.db import get_db
from app.core.lifespan import lifespan


app = FastAPI(title="Back-end",lifespan=lifespan)

app.include_router(s3_router)
app.include_router(auth_router)

@app.get("/")
def root() -> dict:
    return {"message": "Hola :)"}

@app.get("/health")
def health(db : Session= Depends(get_db)) -> dict:
    result = db.exec(text("SELECT 1"))
    if result.scalar() == 1:
        return {"status": "healthy"}
    else:
        return {"status": "unhealthy"}