from fastapi import APIRouter, Response, status

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import ProjectInsightsServiceDep, ProjectServiceDep
from app.exceptions import ProjectNotFoundException
from app.schemas import (
    DeadlinePredictionResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, current_user: CurrentUser, service: ProjectServiceDep):
    return service.create_project(current_user.user_id,
                                  data
                                )

@router.get("/group/{group_id}", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def get_projects_by_group(group_id: int, current_user: CurrentUser, service: ProjectServiceDep):
    return service.get_projects_by_group(
        group_id,
        current_user.user_id
    )

@router.get(
    "/{project_id}/deadline-prediction",
    response_model=DeadlinePredictionResponse,
    status_code=status.HTTP_200_OK,
)
def get_deadline_prediction(
    project_id: int,
    current_user: CurrentUser,
    service: ProjectInsightsServiceDep,
) -> DeadlinePredictionResponse:
    """
    Smart feature. It predicts whether the project will be completed before its
    deadline, from the pace at which its tasks have been completed.
    """
    project = service.get_accessible_project(project_id, current_user.user_id)
    if project is None:
        raise ProjectNotFoundException(project_id)

    prediction = service.predict_deadline(project)

    return DeadlinePredictionResponse(
        project_id=project.id,
        project_name=project.name,
        deadline=project.deadline,
        days_left=prediction["days_left"],
        total_tasks=prediction["total_tasks"],
        completed_tasks=prediction["completed_tasks"],
        remaining_tasks=prediction["remaining_tasks"],
        pace_tasks_per_day=prediction["pace_tasks_per_day"],
        predicted_completion_date=prediction["predicted_completion_date"],
        will_meet_deadline=prediction["will_meet_deadline"],
    )


@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_user(project_id: int, current_user: CurrentUser, service: ProjectServiceDep):
    return service.get_project_by_user(
        project_id,
        current_user.user_id
    )
    
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, current_user: CurrentUser, service: ProjectServiceDep):
    service.delete_project(
        project_id,
        current_user.user_id
    )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
    
@router.patch("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(project_id: int, data: ProjectUpdate, current_user: CurrentUser, service: ProjectServiceDep):
    return service.update_project(
        project_id,
        current_user.user_id,
        data
    )