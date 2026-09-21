from app.models import Group, User, Project
from app.repositories.group_repository import GroupRepository


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def create_group(self, group: Group) -> Group:
        ...

