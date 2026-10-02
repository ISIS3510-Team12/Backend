from . import BaseRepository
from app.models import UserLocation


class LocationRepository(BaseRepository):
    """
    LocationRepository class that provides database operations for user locations.
    """

    def get_by_user_id(self, user_id: str) -> UserLocation | None:
        return self.db.get(UserLocation, user_id)

    def save(self, location: UserLocation) -> UserLocation:
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location

    def delete(self, location: UserLocation) -> None:
        self.db.delete(location)
        self.db.commit()
