from . import BaseRepository
from app.models import Group, User, Project

class GroupRepository(BaseRepository):

    def save(self, group: Group) -> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def save_users_to_group(self, group: Group, users: list[User]) -> Group:
        ...

    def save_project_to_group(self, project: Project, group: Group) -> Project:
        ...

    def get_by_id(self, group_id: int) -> Group | None:
        ...

    def get_group_users(self, group_id: int) -> list[User] | None:
        ...

    def get_group_projects(self, group_id: int) -> list[Project] | None:
        ...

    def remove(self, group: Group) -> None:
        ...

