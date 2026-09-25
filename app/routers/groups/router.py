from fastapi import APIRouter, Response, status
from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import GroupServiceDep
from app.schemas import GroupCreate, GroupResponse

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(data:GroupCreate, current_user: CurrentUser, service:GroupServiceDep):
        return service.create_group(current_user.user_id, data)
    

@router.get("", response_model=list[GroupResponse], status_code=status.HTTP_200_OK)
def get_groups_by_user(current_user: CurrentUser, service: GroupServiceDep):
    return service.get_groups_by_user(current_user.user_id)


@router.get("/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK)
def get_group_by_user(group_id: int, current_user: CurrentUser, service: GroupServiceDep):
    return service.get_group_by_user(group_id, current_user.user_id)


@router.patch("/{group_id}", response_model=GroupResponse, status_code=status.HTTP_200_OK)
def update_group(group_id: int, data: GroupCreate, current_user: CurrentUser, service: GroupServiceDep):
    return service.update_group(group_id, current_user.user_id, data)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, current_user: CurrentUser, service: GroupServiceDep):
    service.delete_group(group_id, current_user.user_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)