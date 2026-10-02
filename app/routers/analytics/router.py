from fastapi import APIRouter, Query, status
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


@router.get("/upcoming-tasks-due", status_code=status.HTTP_200_OK)
def get_upcoming_tasks_due(
    service: AnalyticsServiceDep,
    days: int = Query(7, ge=1, le=30),
) -> Response:
    """
    This is the answer to the Business Question:
    "Which upcoming tasks does the user have due in the next week?"
    It returns a CSV file with one row per user and pending task due in the
    next `days` days (7 by default).
    """
    csv_content = service.upcoming_tasks_due_csv(days)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="upcoming_tasks_due.csv"'
        },
    )

@router.get("/average-task-completion-time-before-deadline", status_code=status.HTTP_200_OK)
def get_average_task_completion_time_before_deadline(
    service: AnalyticsServiceDep,
) -> Response:
    """
    This is the answer to the Business Question:
    "What is the average time it takes users to complete tasks before their deadlines?"
    It returns a CSV file with the needed data.
    """
    csv_content = service.average_task_completion_time_before_deadline_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="average_task_completion_time_before_deadline.csv"'
        },
    )

@router.get("/most-frecuently-task-types", status_code=status.HTTP_200_OK)
def get_most_frecuently_task_types(
    service: AnalyticsServiceDep,
) -> Response:
    """
    This is the answer to the Business Question:
    "Which types of tasks are created most frequently by students?"

    It returns a CSV file with the needed data.
    """
    csv_content = service.frecuently_task_types_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="most_frecuently_task_types.csv"'
        },
    )