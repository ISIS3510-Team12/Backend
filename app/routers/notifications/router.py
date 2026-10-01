from fastapi import APIRouter, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import NotificationServiceDep

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get("", status_code=status.HTTP_200_OK)
def get_notifications(
    current_user: CurrentUser,
    service: NotificationServiceDep
):
    return service.get_notifications(current_user.user_id)
