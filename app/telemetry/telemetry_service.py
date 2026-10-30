from datetime import datetime
from app.exceptions import TaskNotFoundException
from app.models import ScreenLoadEvent, TaskDetailSession
from app.repositories.task_repository import TaskRepository
from app.telemetry.telemetry_repository import TelemetryRepository
from app.schemas import ScreenLoadEventCreate, TaskDetailSessionCreate
from app.models import FeatureSession
from app.schemas import FeatureSessionCreate
from datetime import timezone

class TelemetryService:

    def __init__(self, repository: TelemetryRepository, task_repository: TaskRepository):
        self.repository = repository
        self.task_repository = task_repository

    def register_screen_load(self, user_id: str, data: ScreenLoadEventCreate) -> ScreenLoadEvent:

        event = ScreenLoadEvent(
            screen=data.screen,
            load_time_ms=data.load_time_ms,
            occurred_at=datetime.now(),
            user_id=user_id,
        )

        return self.repository.register_screen_load_event(event)

    def register_task_detail_session(self, user_id: str, data: TaskDetailSessionCreate) -> TaskDetailSession:
        if self.task_repository.get_task_for_user(data.task_id, user_id) is None:
            raise TaskNotFoundException(data.task_id)

        # Dates are stored without timezone, like the rest of the task dates.
        session = TaskDetailSession(
            task_id=data.task_id,
            user_id=user_id,
            opened_at=data.opened_at.replace(tzinfo=None),
            closed_at=data.closed_at.replace(tzinfo=None),
            progress_updated=data.progress_updated,
        )

        return self.repository.register_task_detail_session(session)

    def register_feature_session(self, user_id: str, data: FeatureSessionCreate) -> FeatureSession:
        opened_at = data.opened_at
        closed_at = data.closed_at

        if opened_at.tzinfo is not None:
            opened_at = opened_at.astimezone(timezone.utc).replace(tzinfo=None)

        if closed_at.tzinfo is not None:
            closed_at = closed_at.astimezone(timezone.utc).replace(tzinfo=None)

        session = FeatureSession(
            feature=data.feature,
            opened_at=opened_at,
            closed_at=closed_at,
            user_id=user_id,
        )
        return self.repository.register_feature_session(session)
