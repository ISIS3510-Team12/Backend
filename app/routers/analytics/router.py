from fastapi import APIRouter, status
from fastapi.responses import Response

from app.core.dependencies.auth import CurrentUser
from app.core.dependencies.services import AnalyticsServiceDep

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)


@router.get("/task-completion-time", status_code=status.HTTP_200_OK)
def get_task_completion_time(
    service: AnalyticsServiceDep
) -> Response:
    """
    This is the answer to the Business Question:
    "How long does it take users to complete a task after first opening it?"
    It returns a CSV file with the needed data.
    """
    csv_content = service.task_completion_time_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="task_completion_time.csv"'
        },
    )

@router.get("/screen-load-time", status_code=status.HTTP_200_OK)
def get_screen_load_time(service: AnalyticsServiceDep) -> Response:
    """
    This is the answer to the Business Question:
    "What is the average screen-load time for each major screen?"
    And it returns a CSV file with the needed data
    """

    csv_content = service.screen_load_time_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                'attachment; filename="screen_load_time.csv"'
            )
        },
    )
