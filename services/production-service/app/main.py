from fastapi import FastAPI

from app.api.batch_router import router as batch_router
from app.api.part_router import router as part_router

app = FastAPI(title="Production Service")

app.include_router(batch_router)
app.include_router(part_router)


@app.get("/health")
def health():
    return {"status": "ok"}
