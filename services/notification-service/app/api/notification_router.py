from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notification"])


@router.post("/", response_model=NotificationResponse, status_code=201)
def create(notification_data: NotificationCreate, db: Session = Depends(get_db)):
    return NotificationService.create_notification(db, notification_data)


@router.get("/", response_model=list[NotificationResponse])
def get_all(db: Session = Depends(get_db)):
    return NotificationService.get_notifications(db)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_by_id(notification_id: int, db: Session = Depends(get_db)):
    return NotificationService.get_notification(db, notification_id)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def update_notification(notification_id: int, db: Session = Depends(get_db)):
    return NotificationService.mark_notification_as_read(db, notification_id)


@router.delete("/{notification_id}", status_code=204)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    return NotificationService.delete_notification(db, notification_id)
