import csv
from io import StringIO

from app.analytics.analytics_repository import AnalyticsRepository


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
