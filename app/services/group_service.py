from app.models import Group
from app.repositories.group_repository import GroupRepository


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

        
