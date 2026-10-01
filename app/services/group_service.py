from fastapi import HTTPException, status

from app.models import Group
from app.repositories.group_repository import GroupRepository
from app.schemas import GroupCreate, GroupResponse
from app.services.mappers import to_group_response


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def create_group(self, user_id: str, data: GroupCreate) -> GroupResponse:
        group = Group(
            name=data.name,
            description=data.description,
            deadline=data.deadline,
        )
        created = self.repository.create_group(group)
        self.repository.add_user_to_group(user_id, created.id)
        return to_group_response(self.repository.get_group_by_id(created.id, user_id))

    def get_groups_by_user(self, user_id: str) -> list[GroupResponse]:
        groups = self.repository.get_groups_by_user_id(user_id)
        pending_counts = self.repository.count_pending_tasks_by_group()
        responses: list[GroupResponse] = []
        for group in groups:
            responses.append(to_group_response(group, pending_counts.get(group.id, 0)))
        return responses

    def get_group_by_user(self, group_id: int, user_id: str) -> GroupResponse:
        group = self.repository.get_group_by_id(group_id, user_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        pending_counts = self.repository.count_pending_tasks_by_group()
        return to_group_response(group, pending_counts.get(group.id, 0))

    def update_group(self, group_id: int, user_id: str, data: GroupCreate) -> GroupResponse:
        group = self.repository.get_group_by_id(group_id, user_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        updated = self.repository.update_group(group, data.model_dump())
        return to_group_response(updated)

    def delete_group(self, group_id: int, user_id: str) -> None:
        group = self.repository.get_group_by_id(group_id, user_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        self.repository.delete_group(group)
