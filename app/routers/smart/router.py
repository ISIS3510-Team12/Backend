from fastapi import APIRouter, status

from app.core.consts import NEXT_TASK_HORIZON_DAYS
from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import TaskServiceDep
from app.schemas import NextTaskResponse

router = APIRouter(
    prefix="/smart",
    tags=["smart"]
)


@router.get(
    "/next-task",
    response_model=NextTaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_next_task(
    current_user: CurrentUser,
    service: TaskServiceDep,
) -> NextTaskResponse:
    """
    Smart feature. Returns the one pending task the user should open next,
    including overdue tasks, with the reason for the recommendation.

    When there is no pending task in the recommendation horizon, the response
    has no task and includes a message for the user.
    """
    task = service.get_next_task(current_user.user_id)

    if task is None:
        # Tell the user that the horizon is empty.
        message = (
            "You have no pending tasks in the next "
            f"{NEXT_TASK_HORIZON_DAYS} days."
        )
        return NextTaskResponse(message=message)

    return NextTaskResponse(task=task)
