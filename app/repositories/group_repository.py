import select
from . import BaseRepository
from app.models import Group, User, Project, UserGroup

class GroupRepository(BaseRepository):
    
    def create_group(self, group:Group)-> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def update_group(self, group: Group, data: dict) -> Group:
        for field, value in data.items():
            setattr(group, field, value)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        
        return group
    
    def delete_group(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()
        
    def get_group_by_id(self, group_id:int, user_id: int) -> Group|None:
        # TODO: check if user can access this project
        return self.db.get(Group, group_id)
    
    def search_groups_by_name(self, name: str) -> list[Group]:
        statement = select(Group).where(Group.name.ilike(f"%{name}%"))
        results = self.db.exec(statement).all()
        return list(results)
        
    def get_groups_by_user_id(self, user_id: str) -> list[Group]:
        user = self.db.get(User, user_id)
        if user:
            return user.groups
        return []
    
    def get_projects_by_group_id(self, group_id: int)-> list[Project]:
        projects = select(Project).where(Project.group_id == group_id)
        results = self.db.exec(projects).all
        return list(results)
    
    def add_user_to_group(self, user_id: str, group_id: int)-> UserGroup:
        user_group = UserGroup(user_id=user_id,group_id=group_id)
        self.db.add(user_group)
        self.commit()
        self.db.refresh(user_group)
        
        return user_group
    
    def add_user_to_group(self, user_id: str, group_id: int)-> None:    
        statement = select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
        user_group = self.db.exec(statement).first()
        self.db.delete(user_group)
        self.commit()
    
                
    

    

