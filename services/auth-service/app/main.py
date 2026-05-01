from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.session import engine


app = FastAPI(title="Auth Service")

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}