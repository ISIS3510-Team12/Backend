from datetime import UTC, datetime

from sqlmodel import select

from app.core.consts import EventType
from app.models import TaskEvent
from app.repositories import BaseRepository


class TaskEventRepository(BaseRepository):
    def add_event(self, task_id: int, event_type: EventType) -> TaskEvent:
        event = TaskEvent(
            event_type=event_type,
            occurred_at=datetime.now(UTC).replace(tzinfo=None),
            task_id=task_id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events_for_task(self, task_id: int) -> list[TaskEvent]:
        statement = select(TaskEvent).where(TaskEvent.task_id == task_id)
        results = self.db.exec(statement).all()
        return list(results)
