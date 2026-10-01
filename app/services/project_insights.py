from datetime import datetime, timedelta

from app.core.consts import SECONDS_PER_DAY, TaskStatus
from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_event_repository import TaskEventRepository
from app.repositories.task_repository import TaskRepository


class ProjectInsightsService:
    """
    Smart feature, looks at the pace at which a project's tasks have been
    completed so far and predicts whether the project will be finished before
    its deadline.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        task_repository: TaskRepository,
        task_event_repository: TaskEventRepository,
    ):
        self.project_repository = project_repository
        self.task_repository = task_repository
        self.task_event_repository = task_event_repository

    def get_accessible_project(self, project_id: int, user_id: str) -> Project | None:
        """
        A project is accessible when the user belongs to its group.
        """
        return self.project_repository.get_project_by_id(project_id, user_id)

    def predict_deadline(self, project: Project) -> dict:
        tasks = self.task_repository.get_all_tasks_by_project(project.id)

        total_tasks = 0
        completed_tasks = 0
        for task in tasks:
            total_tasks = total_tasks + 1
            if task.status == TaskStatus.COMPLETED:
                completed_tasks = completed_tasks + 1

        remaining_tasks = total_tasks - completed_tasks

        now = datetime.now()
        days_left = (project.deadline - now).total_seconds() / SECONDS_PER_DAY

        pace = self.completion_pace(project.id, completed_tasks, now)

        if remaining_tasks == 0:
            predicted_completion_date = now
            will_meet_deadline = True
        elif pace <= 0:
            predicted_completion_date = None
            will_meet_deadline = False
        else:
            days_needed = remaining_tasks / pace
            predicted_completion_date = now + timedelta(days=days_needed)
            will_meet_deadline = predicted_completion_date <= project.deadline

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "remaining_tasks": remaining_tasks,
            "days_left": round(days_left, 2),
            "pace_tasks_per_day": round(pace, 2),
            "predicted_completion_date": predicted_completion_date,
            "will_meet_deadline": will_meet_deadline,
        }

    def completion_pace(self, project_id: int, completed_tasks: int, now: datetime) -> float:
        """
        Tasks completed per day since the project's first tracked task event.
        """
        started_at = self.task_event_repository.get_project_first_event_at(project_id)
        if started_at is None:
            return 0.0

        elapsed_days = (now - started_at).total_seconds() / SECONDS_PER_DAY
        if elapsed_days <= 0:
            return 0.0

        return completed_tasks / elapsed_days
