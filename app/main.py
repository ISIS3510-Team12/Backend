from fastapi import FastAPI
from sqlmodel import text
from app.routers import users_router, s3_router, tasks_router, projects_router, groups_router, telemetry_router
from app.core.dependencies.database import DatabaseSession
from app.core.lifespan import lifespan
from fastapi.responses import RedirectResponse

app = FastAPI(title="Juggle Backend",lifespan=lifespan)

app.include_router(s3_router.router)
app.include_router(users_router.router)
app.include_router(tasks_router.router)
app.include_router(projects_router.router)
app.include_router(groups_router.router)
app.include_router(telemetry_router.router)

@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")

@app.get("/health")
async def get_health():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/health/db")
def get_db_health(db: DatabaseSession) -> dict:
    try:
        db.exec(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}