from fastapi import APIRouter, Response, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import ProjectServiceDep
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, current_user: CurrentUser, service: ProjectServiceDep):
    return service.create_project(current_user.user_id, data)

@router.get("/group/{group_id}", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def get_projects_by_group(group_id: int, current_user: CurrentUser, service: ProjectServiceDep):
    return service.get_projects_by_group(group_id, current_user.user_id)

