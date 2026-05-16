from fastapi import FastAPI
import logging

from app.api.notification_router import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="Notification Service")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
