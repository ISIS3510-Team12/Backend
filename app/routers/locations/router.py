from fastapi import APIRouter, Response, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import LocationServiceDep
from app.schemas import UserLocationResponse, UserLocationUpsert

router = APIRouter(
    prefix="/users/me/location",
    tags=["locations"]
)


@router.get("", response_model=UserLocationResponse, status_code=status.HTTP_200_OK)
def get_location(current_user: CurrentUser, service: LocationServiceDep):
    return service.get_location(current_user.user_id)


@router.put("", response_model=UserLocationResponse, status_code=status.HTTP_200_OK)
def save_location(data: UserLocationUpsert, current_user: CurrentUser, service: LocationServiceDep):
    return service.save_location(current_user.user_id, data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(current_user: CurrentUser, service: LocationServiceDep):
    service.delete_location(current_user.user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
