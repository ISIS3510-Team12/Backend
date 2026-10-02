from app.exceptions import UserLocationNotFoundException
from app.models import UserLocation
from app.repositories.location_repository import LocationRepository
from app.schemas import UserLocationUpsert


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

    def get_location(self, user_id: str) -> UserLocation:
        location = self.repository.get_by_user_id(user_id)
        if location is None:
            raise UserLocationNotFoundException(user_id)
        return location

    def save_location(self, user_id: str, data: UserLocationUpsert) -> UserLocation:
        location = self.repository.get_by_user_id(user_id)
        if location is None:
            location = UserLocation(user_id=user_id, **data.model_dump())
        else:
            location.sqlmodel_update(data.model_dump())
        return self.repository.save(location)

    def delete_location(self, user_id: str) -> None:
        self.repository.delete(self.get_location(user_id))
