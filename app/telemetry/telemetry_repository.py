from app.models import ScreenLoadEvent
from app.repositories import BaseRepository


class TelemetryRepository(BaseRepository):

    def register_screen_load_event(self, event: ScreenLoadEvent) -> ScreenLoadEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event