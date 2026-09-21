from . import BaseRepository
from app.models import Group, User, Project

class GroupRepository(BaseRepository):

    def save(self, group: Group) -> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_by_id(self, group_id: str) -> Group | None:
        return self.db.get(Group, group_id)

    def get_group_users(self, group_id: str) -> list[User] | None:
        group = self.db.get(Group, group_id)
        if group:
            return group.users
        return None

    def get_group_projects(self, group_id: str) -> list[Project] | None:
        group = self.db.get(Group, group_id)
        if group:
            return group.projects
        return None

    def remove(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()

