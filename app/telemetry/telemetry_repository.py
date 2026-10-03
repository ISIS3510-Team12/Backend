from app.models import ScreenLoadEvent, TaskDetailSession
from app.repositories import BaseRepository


class TelemetryRepository(BaseRepository):

    def register_screen_load_event(self, event: ScreenLoadEvent) -> ScreenLoadEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def register_task_detail_session(self, session: TaskDetailSession) -> TaskDetailSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session
