from sqlalchemy import func, or_
from sqlmodel import delete, select

from . import BaseRepository
from app.core.consts import TaskStatus
from app.models import (
    Attachment,
    Group,
    Project,
    Reminder,
    Task,
    TaskAssignee,
    TaskEvent,
    TaskRelation,
    TimeBlock,
    User,
    UserGroup,
)


class GroupRepository(BaseRepository):

    def create_group(self, group: Group) -> Group:
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
        task_ids = select(Task.id).where(Task.group_id == group.id)
        self.db.exec(delete(TaskAssignee).where(TaskAssignee.task_id.in_(task_ids)))
        self.db.exec(
            delete(TaskRelation).where(
                or_(
                    TaskRelation.task_id.in_(task_ids),
                    TaskRelation.related_task_id.in_(task_ids),
                )
            )
        )
        self.db.exec(delete(Reminder).where(Reminder.task_id.in_(task_ids)))
        self.db.exec(delete(TimeBlock).where(TimeBlock.task_id.in_(task_ids)))
        self.db.exec(delete(Attachment).where(Attachment.task_id.in_(task_ids)))
        self.db.exec(delete(TaskEvent).where(TaskEvent.task_id.in_(task_ids)))
        self.db.exec(delete(Task).where(Task.group_id == group.id))
        self.db.exec(delete(Project).where(Project.group_id == group.id))
        self.db.exec(delete(UserGroup).where(UserGroup.group_id == group.id))
        self.db.exec(delete(Group).where(Group.id == group.id))
        self.db.commit()

    def get_group_by_id(self, group_id: int, user_id: str) -> Group | None:
        statement = (
            select(Group)
            .join(
                UserGroup,
                UserGroup.group_id == Group.id
            )
            .where(
                Group.id == group_id,
                UserGroup.user_id == user_id
            )
        )
        return self.db.exec(statement).first()

    def search_groups_by_name(self, name: str) -> list[Group]:
        statement = select(Group).where(
            Group.name.ilike(f"%{name}%")
        )
        results = self.db.exec(statement).all()
        return list(results)

    def get_groups_by_user_id(self, user_id: str) -> list[Group]:
        user = self.db.get(User, user_id)
        if user:
            return list(user.groups)
        return []

    def get_projects_by_group_id(
        self,
        group_id: int
    ) -> list[Project]:
        statement = select(Project).where(
            Project.group_id == group_id
        )
        results = self.db.exec(statement).all()

        return list(results)

    def count_pending_tasks_by_group(self) -> dict[int, int]:
        """Count incomplete tasks per group in a single query."""
        statement = (
            select(
                Task.group_id,
                func.count(Task.id)
            )
            .where(
                Task.group_id.is_not(None),
                Task.status != TaskStatus.COMPLETED
            )
            .group_by(Task.group_id)
        )
        results = self.db.exec(statement).all()
        counts: dict[int, int] = {}
        for group_id, count in results:
            counts[group_id] = count

        return counts

    def add_user_to_group(self, user_id: str, group_id: int) -> UserGroup:
        user_group = UserGroup(
            user_id=user_id,
            group_id=group_id
        )
        self.db.add(user_group)
        self.db.commit()
        self.db.refresh(user_group)

        return user_group

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.strip().lower())
        return self.db.exec(statement).first()

    def count_members(self, group_id: int) -> int:
        statement = select(func.count()).select_from(UserGroup).where(
            UserGroup.group_id == group_id
        )
        return self.db.exec(statement).one()

    def remove_user_from_group(self, user_id: str, group_id: int) -> None:
        statement = select(UserGroup).where(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id
        )
        user_group = self.db.exec(statement).first()
        if user_group is not None:
            self.db.delete(user_group)
            self.db.commit()
            
    def create_group_with_members(self, group: Group, user_ids: list[str]) -> Group:
        try:
            self.db.add(group)
            self.db.flush()

            for user_id in user_ids:
                self.db.add(
                    UserGroup(
                        user_id=user_id,
                        group_id=group.id,
                    )
                )

            self.db.commit()
            self.db.refresh(group)

            return group

        except Exception:
            self.db.rollback()
            raise