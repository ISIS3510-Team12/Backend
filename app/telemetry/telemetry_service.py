from datetime import datetime
from app.models import ScreenLoadEvent
from app.telemetry.telemetry_repository import TelemetryRepository
from app.schemas import ScreenLoadEventCreate

class TelemetryService:

    def __init__(self, repository: TelemetryRepository):
        self.repository = repository

    def register_screen_load(self, user_id: str, data: ScreenLoadEventCreate) -> ScreenLoadEvent:

        event = ScreenLoadEvent(
            screen=data.screen,
            load_time_ms=data.load_time_ms,
            occurred_at=datetime.now(),
            user_id=user_id,
        )

        return self.repository.register_screen_load_event(event)