import csv
import math
from datetime import datetime, timedelta
from io import StringIO

from app.analytics.analytics_repository import AnalyticsRepository
from app.core.consts import (
    FEATURE_TIME_BUCKET_SECONDS,
    FREQUENT_FEATURE_OPEN_PERCENTILE,
    HIGH_ACTIVITY_PROJECT_PERCENTILE,
    RARE_FEATURE_USAGE_RATIO,
    SECONDS_PER_DAY,
    TaskEventType,
)

# (feature name in the CSV, column of get_project_feature_usage with its task count)
TASK_FEATURES = [
    ("priority", "priority_tasks"),
    ("needs_help", "needs_help_tasks"),
    ("description", "description_tasks"),
    ("shared_assignees", "shared_assignees_tasks"),
    ("related_tasks", "related_tasks_tasks"),
    ("reminders", "reminders_tasks"),
    ("time_blocks", "time_blocks_tasks"),
    ("photo_attachment", "photo_attachment_tasks"),
]


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
                row.project_id,
                row.project_name,
                now.isoformat(),
            ])

        return buffer.getvalue()

    def average_task_completion_time_before_deadline_csv(self) -> str:
        rows = self.repository.get_task_completion_deadlines()
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
            "task_count",
        ])
        for row in rows:
            writer.writerow([row["task_type"], row["task_count"]])

        return buffer.getvalue()

    def task_detail_closed_without_update_csv(self) -> str:
        rows = self.repository.get_task_detail_sessions_per_week()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "user_id",
            "week_start",
            "sessions_total",
            "sessions_without_update",
            "abandon_ratio",
        ])
        for row in rows:
            sessions_without_update = int(row.sessions_without_update)
            writer.writerow([
                row.user_id,
                row.week_start.isoformat(),
                row.sessions_total,
                sessions_without_update,
                round(sessions_without_update / row.sessions_total, 4),
            ])

        return buffer.getvalue()


    def task_updates_concentration_periods_csv(self) -> str:
        rows = self.repository.get_task_updates_concentration_periods()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "period",
            "event_type",
            "task_update_count"
        ])

        for row in rows:
            writer.writerow([
                f"{row['period']:02d}:00",
                row["event_type"].name if isinstance(row["event_type"], TaskEventType) else str(row["event_type"]),
                row["task_update_count"],
            ])
        return buffer.getvalue()


    def features_under_five_seconds_csv(self) -> str:
        rows = self.repository.get_features_under_five_seconds()

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "feature",
            "session_count",
            "average_session_seconds",
        ])

        for feature, session_count, average_seconds in rows:
            writer.writerow([
                feature,
                session_count,
                f"{float(average_seconds):.2f}",
            ])

        return buffer.getvalue()

    def feature_abandonment_time_csv(
        self,
        bucket_seconds: int = FEATURE_TIME_BUCKET_SECONDS,
        feature: str | None = None,
    ) -> str:
        rows = self.repository.get_feature_session_duration_buckets(bucket_seconds, feature)

        buckets_by_feature: dict[str, dict[int, int]] = {}
        for feature_name, bucket, session_count in rows:
            buckets_by_feature.setdefault(feature_name, {})[bucket] = session_count

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "feature",
            "seconds",
            "sessions_still_active",
            "percentage_still_active",
        ])

        for feature_name, buckets in buckets_by_feature.items():
            total = sum(buckets.values())
            still_active = total

            for bucket in range(max(buckets) + 2):
                writer.writerow([
                    feature_name,
                    bucket * bucket_seconds,
                    still_active,
                    f"{still_active / total * 100:.2f}",
                ])
                still_active -= buckets.get(bucket, 0)

        return buffer.getvalue()

    def frequently_opened_rarely_used_csv(
        self,
        min_opens: int | None = None,
        max_completion_ratio: float | None = None,
    ) -> str:
        rows = self.repository.get_feature_open_vs_usage()

        if min_opens is None:
            min_opens = self.frequent_open_threshold(rows)
        if max_completion_ratio is None:
            max_completion_ratio = RARE_FEATURE_USAGE_RATIO

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow([
            "feature",
            "open_count",
            "completed_count",
            "completion_ratio",
            "flagged",
        ])

        for feature, open_count, completed_count in rows:
            completed_count = int(completed_count)
            completion_ratio = completed_count / open_count
            flagged = (
                min_opens is not None
                and open_count >= min_opens
                and completion_ratio <= max_completion_ratio
            )
            writer.writerow([
                feature,
                open_count,
                completed_count,
                f"{completion_ratio:.2f}",
                str(flagged).lower(),
            ])

        return buffer.getvalue()

    def frequent_open_threshold(self, rows: list) -> int | None:
        """
        Minimum opens for a feature to count as frequently opened: the
        percentile of open counts among all features.
        """
        counts = sorted(row.open_count for row in rows)
        if not counts:
            return None

        position = (len(counts) - 1) * FREQUENT_FEATURE_OPEN_PERCENTILE
        lower = math.floor(position)
        upper = math.ceil(position)
        value = counts[lower] + (counts[upper] - counts[lower]) * (position - lower)

        return math.ceil(value)

    def most_used_features_in_active_projects_csv(
        self, min_completed_tasks: int | None = None
    ) -> str:
        rows = self.repository.get_project_feature_usage()

        threshold = min_completed_tasks
        if threshold is None:
            threshold = self.active_project_threshold(rows)

        active = []
        other = []
        for row in rows:
            if threshold is not None and row.completed_tasks >= threshold:
                active.append(row)
            else:
                other.append(row)

        active_tasks_total = sum(row.total_tasks for row in active)
        other_tasks_total = sum(row.total_tasks for row in other)

        features = []
        for feature, column in TASK_FEATURES:
            active_tasks_using = sum(int(getattr(row, column)) for row in active)
            other_tasks_using = sum(int(getattr(row, column)) for row in other)
            active_projects_using = sum(1 for row in active if getattr(row, column) > 0)
            features.append({
                "feature": feature,
                "active_projects_using": active_projects_using,
                "active_tasks_using": active_tasks_using,
                "other_tasks_using": other_tasks_using,
            })
        features.sort(key=lambda item: item["active_tasks_using"], reverse=True)

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "feature",
            "completed_tasks_threshold",
            "active_projects_using",
            "active_projects_total",
            "active_project_usage_pct",
            "active_tasks_using",
            "active_tasks_total",
            "active_task_usage_pct",
            "other_task_usage_pct",
        ])

        # Without active projects there is nothing to report.
        if not active:
            return buffer.getvalue()

        for item in features:
            writer.writerow([
                item["feature"],
                threshold,
                item["active_projects_using"],
                len(active),
                round(item["active_projects_using"] / len(active), 4),
                item["active_tasks_using"],
                active_tasks_total,
                round(item["active_tasks_using"] / active_tasks_total, 4),
                round(item["other_tasks_using"] / other_tasks_total, 4) if other_tasks_total else 0,
            ])

        return buffer.getvalue()

    def days_since_last_progress_csv(self) -> str:
        now = datetime.now()
        rows = self.repository.get_days_since_last_progress()

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "user_id",
            "last_progress_at",
            "days_since_last_progress",
        ])

        for row in rows:
            if row.last_progress_at is None:
                writer.writerow([row.user_id, "", ""])
                continue
            writer.writerow([
                row.user_id,
                row.last_progress_at.isoformat(),
                (now - row.last_progress_at).days,
            ])

        return buffer.getvalue()

    def active_project_threshold(self, rows: list) -> int | None:
        """
        Minimum completed tasks for a project to be highly active: the
        percentile of completed tasks among projects with at least one.
        """
        counts = sorted(row.completed_tasks for row in rows if row.completed_tasks > 0)
        if not counts:
            return None

        position = (len(counts) - 1) * HIGH_ACTIVITY_PROJECT_PERCENTILE
        lower = math.floor(position)
        upper = math.ceil(position)
        value = counts[lower] + (counts[upper] - counts[lower]) * (position - lower)

        return math.ceil(value)


    def task_reopen_frequency_csv(self) -> str:
        rows = self.repository.get_task_reopen_frequency()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "user_id",
            "week_start",
            "occurrences",
            "distinct_tasks",
            "total_opens",
            "total_reopens",
            "avg_reopens_per_occurrence",
        ])

        buckets: dict[tuple[str, object], dict] = {}
        for row in rows:
            week_start = row.day - timedelta(days=row.day.weekday())
            bucket = buckets.setdefault(
                (row.user_id, week_start),
                {
                    "occurrences": 0,
                    "tasks": set(),
                    "opens": 0,
                    "reopens": 0,
                },
            )
            bucket["occurrences"] += 1
            bucket["tasks"].add(row.task_id)
            bucket["opens"] += int(row.opens)
            bucket["reopens"] += int(row.reopens)

        for (user_id, week_start), bucket in sorted(
            buckets.items(), key=lambda item: (item[0][1], item[0][0])
        ):
            occurrences = bucket["occurrences"]
            writer.writerow([
                user_id,
                week_start.isoformat(),
                occurrences,
                len(bucket["tasks"]),
                bucket["opens"],
                bucket["reopens"],
                round(bucket["reopens"] / occurrences, 2),
            ])

        return buffer.getvalue()
