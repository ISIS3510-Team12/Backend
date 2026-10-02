import csv
from datetime import datetime
from io import StringIO

from app.analytics.analytics_repository import AnalyticsRepository
from app.core.consts import PERSONAL_GROUP_NAME, SECONDS_PER_DAY


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
            days_until_due = (row.deadline - now).total_seconds() / SECONDS_PER_DAY
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
                round(days_until_due * 24, 2),
                round(days_until_due, 2),
                row.group_id,
                row.group_name,
                row.group_name == PERSONAL_GROUP_NAME,
                row.project_id,
                row.project_name,
                now.isoformat(),
            ])

        return buffer.getvalue()
    
    def average_task_completion_time_before_deadline_csv(self) -> str:
        rows = self.repository.get_task_completion_times()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "owner_id",
            "average_completion_time_before_deadline_seconds",
        ])
        total_seconds = 0
        count = 0
        current_user_id = None

        for row in rows:
            if current_user_id is None:
                current_user_id = row.owner_id

            if row.owner_id != current_user_id:
                if count > 0:
                    average_seconds = total_seconds / count
                else:
                    average_seconds = 0
                writer.writerow([current_user_id, round(average_seconds, 2)])
                total_seconds = 0
                count = 0
                current_user_id = row.owner_id

            seconds_before_deadline = (row.deadline - row.completed_at).total_seconds()
            total_seconds += seconds_before_deadline
            count += 1
        
        average_seconds = total_seconds / count if count > 0 else 0
        writer.writerow([current_user_id, round(average_seconds, 2)])
        
        return buffer.getvalue()

    def frecuently_task_types_csv(self) -> str:
        rows = self.repository.get_frecuently_task_types()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "task_type",
            "count",
        ])
        for row in rows:
            writer.writerow([row.task_type, row.count])
        return buffer.getvalue()