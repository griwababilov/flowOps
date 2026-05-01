from fastapi import FastAPI

from app.api.batch import router as batch_router
from app.db.base import Base

app = FastAPI(title="Production Service")

app.include_router(batch_router)


@app.get("/health")
def health():
    return {"status": "ok"}
