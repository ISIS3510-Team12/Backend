from fastapi import APIRouter, Query, status
from fastapi.responses import Response

from app.core.consts import FEATURE_TIME_BUCKET_SECONDS
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


@router.get("/task-detail-closed-without-update", status_code=status.HTTP_200_OK)
def get_task_detail_closed_without_update(
    service: AnalyticsServiceDep,
) -> Response:
    """
    This is the answer to the Business Question:
    "How many times per week does a user open a task detail and close it without updating its progress?"
    It returns a CSV file with one row per user and week.
    """
    csv_content = service.task_detail_closed_without_update_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="task_detail_closed_without_update.csv"'
        },
    )


@router.get("/task-updates-concentration-periods", status_code=status.HTTP_200_OK)
def get_task_updates_concentration_periods(
    service: AnalyticsServiceDep,
) -> Response:
    """
    This is the answer to the Business Question:
    "What are the time periods with the highest concentration of task updates on the platform?"

    It returns a CSV file with the needed data.
    """
    csv_content = service.task_updates_concentration_periods_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="task_updates_concentration_periods.csv"'
        },
    )

@router.get("/features-under-five-seconds", status_code=status.HTTP_200_OK)
def get_features_under_five_seconds(service: AnalyticsServiceDep) -> Response:
    """
    This is the answer to the Business Question:
    "Which features have an average session time under 5 seconds?"

    It returns a CSV file with the needed data.
    """
    csv_content = service.features_under_five_seconds_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                'attachment; filename="features_under_five_seconds.csv"'
        },
    )


@router.get("/feature-abandonment-time", status_code=status.HTTP_200_OK)
def get_feature_abandonment_time(
    service: AnalyticsServiceDep,
    bucket_seconds: int = Query(FEATURE_TIME_BUCKET_SECONDS, ge=1),
    feature: str | None = Query(None),
) -> Response:
    """
    This is the answer to the Business Question:
    "How long do users spend in a specific feature before abandoning it?"

    Only abandoned sessions count, the ones the user left without using the feature.
    For each feature, it gives the percentage of those sessions still active as time spent increases.
    The time axis goes in steps of bucket_seconds. Pass feature to get a single feature.
    It returns a CSV file with one row per feature and time step.
    """
    csv_content = service.feature_abandonment_time_csv(bucket_seconds, feature)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="feature_abandonment_time.csv"'
        },
    )


@router.get("/frequently-opened-rarely-used-features", status_code=status.HTTP_200_OK)
def get_frequently_opened_rarely_used_features(
    service: AnalyticsServiceDep,
    min_opens: int | None = Query(None, ge=1),
    max_completion_ratio: float | None = Query(None, ge=0, le=1),
) -> Response:
    """
    This is the answer to the Business Question:
    "Which features are opened frequently but rarely used afterward?"

    A feature is frequently opened when it has at least min_opens sessions.
    By default, that is the 75th percentile of opens among all features.
    It is rarely used when the share of completed sessions is at most max_completion_ratio (default 0.25).
    It returns a CSV file with one row per feature, with the matching ones flagged.
    """
    csv_content = service.frequently_opened_rarely_used_csv(min_opens, max_completion_ratio)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="frequently_opened_rarely_used_features.csv"'
        },
    )


@router.get("/most-used-features-in-active-projects", status_code=status.HTTP_200_OK)
def get_most_used_features_in_active_projects(
    service: AnalyticsServiceDep,
    min_completed_tasks: int | None = Query(None, ge=1),
) -> Response:
    """
    This is the answer to the Business Question:
    "Which task-management features are most frequently used in projects with a high number of completed tasks?"

    A project is highly active when it has at least min_completed_tasks completed tasks.
    By default, that is the 75th percentile of completed tasks among projects with any.
    Feature usage comes from the current state of the tasks, not from interface events.
    It returns a CSV file with one row per feature.
    """
    csv_content = service.most_used_features_in_active_projects_csv(min_completed_tasks)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="most_used_features_in_active_projects.csv"'
        },
    )


@router.get("/days-since-last-progress", status_code=status.HTTP_200_OK)
def get_days_since_last_progress(
    service: AnalyticsServiceDep,
) -> Response:
    """
    This is the answer to the Business Question:
    "How many days have passed since the user recorded their progress on their tasks on the app?"
    It returns a CSV file with one row per user. Users who never changed the
    status of a task have empty values.
    """
    csv_content = service.days_since_last_progress_csv()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="days_since_last_progress.csv"'
        },
    )
