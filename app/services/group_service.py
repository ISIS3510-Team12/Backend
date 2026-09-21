from app.models import Group, User, Project
from app.repositories.group_repository import GroupRepository


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def create_group(self, group: Group) -> Group:
        ...

    def add_users_to_group(self, group: Group, users: list[User]) -> Group:
        ...
    
    def add_project_to_group(self, project: Project, group: Group) -> Project:
        ...
    
    def get_group_by_id(self, group_id: int) -> Group:
        ...

    def get_group_users(self, group_id: int) -> list[User]:
        ...

    def get_group_projects(self, group_id: int) -> list[Project]:
        ...

    def remove_group(self, group: Group) -> None:
        ...

    
        
