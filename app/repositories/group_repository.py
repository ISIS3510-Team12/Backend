from . import BaseRepository
from app.models import Group, User, Project

class GroupRepository(BaseRepository):

    def save(self, group: Group) -> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    

