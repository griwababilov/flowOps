from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.base import Base
from app.db.session import engine

# временно (потом заменим на Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}