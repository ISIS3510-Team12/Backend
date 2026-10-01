import csv
from datetime import datetime
from io import StringIO

from app.analytics.analytics_repository import AnalyticsRepository
from app.core.consts import PERSONAL_GROUP_NAME


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def task_completion_time_csv(self) -> str:
        rows = self.repository.get_task_completion_times()

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "task_id",
            "task_title",
            "project_id",
            "group_id",
            "owner_id",
            "first_viewed_at",
            "completed_at",
            "seconds_to_complete",
            "minutes_to_complete",
        ])

        for row in rows:
            first_viewed_at = row.first_viewed_at
            completed_at = row.completed_at
            seconds = (completed_at - first_viewed_at).total_seconds()
            writer.writerow([
                row.task_id,
                row.task_title,
                row.project_id,
                row.group_id,
                row.owner_id,
                first_viewed_at.isoformat(),
                completed_at.isoformat(),
                seconds,
                round(seconds / 60, 2),
            ])

        return buffer.getvalue()



    def screen_load_time_csv(self) -> str:
        rows = self.repository.get_screen_load_times()

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "screen",
            "average_load_time_ms",
        ])

        for row in rows:
            writer.writerow([
                row.screen,
                round(float(row.average_load_time_ms), 2),
            ])

        return buffer.getvalue()

    def upcoming_tasks_due_csv(self, days: int) -> str:
        now = datetime.now()
        rows = self.repository.get_upcoming_tasks_due(now, days)

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "user_id",
            "user_role",
            "task_id",
            "task_title",
            "task_type",
            "status",
            "is_priority",
            "needs_help",
            "deadline",
            "hours_until_due",
            "days_until_due",
            "group_id",
            "group_name",
            "is_personal_group",
            "project_id",
            "project_name",
            "generated_at",
        ])

        for row in rows:
            seconds_until_due = (row.deadline - now).total_seconds()
            writer.writerow([
                row.user_id,
                row.user_role,
                row.task_id,
                row.task_title,
                row.task_type,
                row.task_status.value,
                row.is_priority,
                row.needs_help,
                row.deadline.isoformat(),
                round(seconds_until_due / 3600, 2),
                round(seconds_until_due / 86400, 2),
                row.group_id,
                row.group_name,
                row.group_name == PERSONAL_GROUP_NAME,
                row.project_id,
                row.project_name,
                now.isoformat(),
            ])

        return buffer.getvalue()
