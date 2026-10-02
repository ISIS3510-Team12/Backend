from datetime import datetime, timedelta

from . import BaseRepository
from app.core.consts import AttachmentKind, TaskStatus
from app.models import (
    Attachment,
    Reminder,
    Task,
    TaskAssignee,
    TaskEvent,
    TaskRelation,
    TimeBlock,
    User,
    UserGroup,
)
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import delete, select

class TaskRepository(BaseRepository):
    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def get_task_by_user_id(self, task_id: int, user_id: int) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id, 
            Task.user_id == user_id
        )
        return self.db.exec(statement).first()

    def get_task_for_user(self, task_id: int, user_id: str) -> Task | None:
        """A task is accessible if the user owns it, is assigned to it, or
        belongs to the group the task lives in."""
        assigned_task_ids = select(TaskAssignee.task_id).where(
            TaskAssignee.user_id == user_id
        )
        user_group_ids = select(UserGroup.group_id).where(
            UserGroup.user_id == user_id
        )
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(
                Task.id == task_id,
                or_(
                    Task.user_id == user_id,
                    Task.id.in_(assigned_task_ids),
                    Task.group_id.in_(user_group_ids),
                ),
            )
        )
        return self.db.exec(statement).first()

    def get_accessible_task_ids(self, task_ids: list[int], user_id: str) -> set[int]:
        if not task_ids:
            return set()
        assigned_task_ids = select(TaskAssignee.task_id).where(
            TaskAssignee.user_id == user_id
        )
        user_group_ids = select(UserGroup.group_id).where(
            UserGroup.user_id == user_id
        )
        statement = (
            select(Task.id)
            .where(
                Task.id.in_(task_ids),
                or_(
                    Task.user_id == user_id,
                    Task.id.in_(assigned_task_ids),
                    Task.group_id.in_(user_group_ids),
                ),
            )
        )
        return set(self.db.exec(statement).all())

    def get_all_tasks_by_user(self, user_id: int) -> list[Task]:
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(Task.user_id == user_id)
        )
        results = self.db.exec(statement).all()
        return list(results)

    def get_all_tasks_by_project(self, project_id: int) -> list[Task]:
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(Task.project_id == project_id)
        )
        results = self.db.exec(statement)
        return results.all()

    def get_own_tasks_by_group(self, user_id: str, group_id: int) -> list[Task]:
        """Pending tasks in the group where the user is the owner or an assignee."""
        assigned_task_ids = select(TaskAssignee.task_id).where(
            TaskAssignee.user_id == user_id
        )
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(
                Task.group_id == group_id,
                Task.status != TaskStatus.COMPLETED,
                or_(Task.user_id == user_id, Task.id.in_(assigned_task_ids)),
            )
        )
        return list(self.db.exec(statement).all())

    def get_group_tasks_by_group(self, user_id: str, group_id: int) -> list[Task]:
        """Pending tasks in the group where the user is neither owner nor assignee."""
        assigned_task_ids = select(TaskAssignee.task_id).where(
            TaskAssignee.user_id == user_id
        )
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(
                Task.group_id == group_id,
                Task.status != TaskStatus.COMPLETED,
                Task.user_id != user_id,
                ~Task.id.in_(assigned_task_ids),
            )
        )
        return list(self.db.exec(statement).all())

    def get_all_tasks_by_user_groups(
        self,
        user_id: str,
        due_within_days: int | None = None,
        mine: bool = False,
        priority: bool = False,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Task]:
        """Every task in any group the user belongs to, with optional filters."""
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .join(UserGroup, UserGroup.group_id == Task.group_id)
            .where(UserGroup.user_id == user_id)
        )

        if mine:
            assigned_task_ids = select(TaskAssignee.task_id).where(
                TaskAssignee.user_id == user_id
            )
            statement = statement.where(
                or_(Task.user_id == user_id, Task.id.in_(assigned_task_ids))
            )

        if priority:
            statement = statement.where(Task.is_priority)

        if due_within_days is not None:
            now = datetime.now()
            deadline_limit = now + timedelta(days=due_within_days)
            statement = statement.where(
                Task.status != TaskStatus.COMPLETED,
                Task.deadline.is_not(None),
                Task.deadline >= now,
                Task.deadline <= deadline_limit,
            )

        if start_date:
            statement = statement.where(Task.deadline >= start_date)
            
        if end_date:
            statement = statement.where(Task.deadline <= end_date)

        return list(self.db.exec(statement).all())

    def get_pending_tasks_due_until(self, user_id: str, end: datetime) -> list[Task]:
        """Unfinished tasks the user owns or is assigned to, with a deadline up to `end` (overdue included)."""
        assigned_task_ids = select(TaskAssignee.task_id).where(
            TaskAssignee.user_id == user_id
        )
        statement = (
            select(Task)
            .join(UserGroup, UserGroup.group_id == Task.group_id)
            .where(
                UserGroup.user_id == user_id,
                or_(Task.user_id == user_id, Task.id.in_(assigned_task_ids)),
                Task.status != TaskStatus.COMPLETED,
                Task.deadline.is_not(None),
                Task.deadline <= end,
            )
            .order_by(Task.deadline)
        )
        return list(self.db.exec(statement).all())

    def get_task_by_project(self, task_id: int, project_id: int):
        statement = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.attachments))
            .where(
                Task.id == task_id,
                Task.project_id == project_id
            )
        )
        return self.db.exec(statement).first()
    
    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update_task(self, task: Task, data:dict) -> Task:
        for field, value in data.items():
            setattr(task, field, value)
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_task(self, task: Task) -> None:
        task_id = task.id
        self.db.exec(delete(TaskAssignee).where(TaskAssignee.task_id == task_id))
        self.db.exec(
            delete(TaskRelation).where(
                or_(
                    TaskRelation.task_id == task_id,
                    TaskRelation.related_task_id == task_id,
                )
            )
        )
        self.db.exec(delete(Reminder).where(Reminder.task_id == task_id))
        self.db.exec(delete(TimeBlock).where(TimeBlock.task_id == task_id))
        self.db.exec(delete(Attachment).where(Attachment.task_id == task_id))
        self.db.exec(delete(TaskEvent).where(TaskEvent.task_id == task_id))
        self.db.exec(delete(Task).where(Task.id == task_id))
        self.db.commit()

    # --- Assignees / related tasks (link tables) -------------------------

    def replace_assignees(self, task: Task, user_ids: list[str]) -> None:
        """Replace the task's assignees with the given user ids."""
        self.db.exec(delete(TaskAssignee).where(TaskAssignee.task_id == task.id))
        rows: list[TaskAssignee] = []
        for user_id in user_ids:
            rows.append(TaskAssignee(task_id=task.id, user_id=user_id))
        self.db.add_all(rows)
        self.db.commit()
        self.db.refresh(task)

    def replace_related_tasks(self, task: Task, related_task_ids: list[int]) -> None:
        """Replace the task's related tasks with the given task ids."""
        self.db.exec(delete(TaskRelation).where(TaskRelation.task_id == task.id))
        rows: list[TaskRelation] = []
        for related_task_id in related_task_ids:
            rows.append(TaskRelation(task_id=task.id, related_task_id=related_task_id))
        self.db.add_all(rows)
        self.db.commit()
        self.db.refresh(task)

    # --- Reminders -------------------------------------------------------

    def get_reminders_by_task(self, task_id: int) -> list[Reminder]:
        statement = (
            select(Reminder)
            .where(Reminder.task_id == task_id)
            .order_by(Reminder.id)
        )
        return list(self.db.exec(statement).all())

    def get_reminder_by_task(self, reminder_id: int, task_id: int) -> Reminder | None:
        statement = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.task_id == task_id,
        )
        return self.db.exec(statement).first()

    def create_reminder(self, reminder: Reminder) -> Reminder:
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def update_reminder(self, reminder: Reminder, data: dict) -> Reminder:
        for field, value in data.items():
            setattr(reminder, field, value)
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def delete_reminder(self, reminder: Reminder) -> None:
        self.db.delete(reminder)
        self.db.commit()

    # --- Time blocks -----------------------------------------------------

    def get_time_blocks_by_task(self, task_id: int) -> list[TimeBlock]:
        statement = (
            select(TimeBlock)
            .where(TimeBlock.task_id == task_id)
            .order_by(TimeBlock.start_at)
        )
        return list(self.db.exec(statement).all())

    def get_time_block_by_task(self, time_block_id: int, task_id: int) -> TimeBlock | None:
        statement = select(TimeBlock).where(
            TimeBlock.id == time_block_id,
            TimeBlock.task_id == task_id,
        )
        return self.db.exec(statement).first()

    def create_time_block(self, time_block: TimeBlock) -> TimeBlock:
        self.db.add(time_block)
        self.db.commit()
        self.db.refresh(time_block)
        return time_block

    def update_time_block(self, time_block: TimeBlock, data: dict) -> TimeBlock:
        for field, value in data.items():
            setattr(time_block, field, value)
        self.db.add(time_block)
        self.db.commit()
        self.db.refresh(time_block)
        return time_block

    def delete_time_block(self, time_block: TimeBlock) -> None:
        self.db.delete(time_block)
        self.db.commit()

    # --- Photo Attachments ----------------------------------------------------------

    def get_photo_attachments(self, task_id: int) -> list[Attachment]:
        statement = (
            select(Attachment)
            .where(Attachment.task_id == task_id, Attachment.kind == AttachmentKind.PHOTO)
            .order_by(Attachment.last_modified_date.desc(), Attachment.id.desc())
        )
        return list(self.db.exec(statement).all())

    def replace_photo_attachments(
        self, task_id: int, attachment: Attachment
    ) -> None:
        self.db.exec(
            delete(Attachment).where(
                Attachment.task_id == task_id, Attachment.kind == AttachmentKind.PHOTO
            )
        )
        self.db.add(attachment)
        self.db.commit()
