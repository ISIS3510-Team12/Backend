from app.core.consts import TaskEventType
from app.repositories.task_event_repository import TaskEventRepository
from app.schemas import TaskNotificationResponse


class NotificationService:
    def __init__(self, repository: TaskEventRepository):
        self.repository = repository

    def get_notifications(self, user_id: str) -> list[TaskNotificationResponse]:
        rows = self.repository.get_notifications_by_user_groups(user_id)
        responses: list[TaskNotificationResponse] = []
        
        for event, task, group in rows:
            responses.append(
                TaskNotificationResponse(
                    id=event.id,
                    task_id=task.id,
                    task_title=task.title,
                    group_id=group.id,
                    group_name=group.name,
                    event_type=self.notification_type(event.event_type),
                    occurred_at=event.occurred_at,
                    author_id=event.author_id,
                )
            )
        return responses

    def notification_type(self, event_type: TaskEventType) -> str:
        if event_type == TaskEventType.STATUS_CHANGED:
            return "completed"
        return str(event_type)
