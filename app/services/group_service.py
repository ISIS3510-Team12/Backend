from fastapi import HTTPException, status

from app.core.consts import PERSONAL_GROUP_NAME
from app.exceptions import (
    AlreadyGroupMemberException,
    LastGroupMemberException,
    PersonalGroupProtectedException,
    ReservedGroupNameException,
    UserEmailNotFoundException,
)
from app.models import Group
from app.repositories.group_repository import GroupRepository
from app.schemas import GroupCreate, GroupMemberAdd, GroupUpdate, GroupResponse
from app.services.mappers import to_group_response


def is_reserved_group_name(name: str) -> bool:
    return name.strip().casefold() == PERSONAL_GROUP_NAME.casefold()


class GroupService:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def create_group(self, user_id: str, data: GroupCreate) -> GroupResponse:
        if is_reserved_group_name(data.name):
            raise ReservedGroupNameException(data.name)
        group = Group(
            name=data.name,
            description=data.description
        )
        created = self.repository.create_group(group)
        self.repository.add_user_to_group(
            user_id,
            created.id
        )
        return to_group_response(
            self.repository.get_group_by_id(
                created.id,
                user_id
            )
        )

    def get_groups_by_user(self, user_id: str) -> list[GroupResponse]:
        self.repository.get_or_create_personal_group(user_id)
        groups = self.repository.get_groups_by_user_id(user_id)
        pending_counts = self.repository.count_pending_tasks_by_group()
        responses: list[GroupResponse] = []

        for group in groups:
            responses.append(
                to_group_response(
                    group,
                    pending_counts.get(group.id, 0)
                )
            )

        return responses

    def get_group_by_user(self, group_id: int, user_id: str) -> GroupResponse:
        group = self.repository.get_group_by_id(
            group_id,
            user_id
        )
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        pending_counts = self.repository.count_pending_tasks_by_group()

        return to_group_response(group, pending_counts.get(group.id, 0))

    def update_group(self, group_id: int, user_id: str, data: GroupUpdate) -> GroupResponse:
        group = self.repository.get_group_by_id(
            group_id,
            user_id
        )
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        if group.name == PERSONAL_GROUP_NAME:
            raise PersonalGroupProtectedException()
        if data.name is not None and is_reserved_group_name(data.name):
            raise ReservedGroupNameException(data.name)
        updated = self.repository.update_group(
            group,
            data.model_dump(exclude_unset=True)
        )

        return to_group_response(updated)

    def delete_group(self, group_id: int, user_id: str) -> None:
        group = self.repository.get_group_by_id(
            group_id,
            user_id
        )
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        if group.name == PERSONAL_GROUP_NAME:
            raise PersonalGroupProtectedException()

        self.repository.delete_group(group)

    def _get_group_or_raise(self, group_id: int, user_id: str) -> Group:
        group = self.repository.get_group_by_id(group_id, user_id)
        if group is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with ID {group_id} not found.",
            )
        return group

    def add_member(self, group_id: int, user_id: str, data: GroupMemberAdd) -> GroupResponse:
        group = self._get_group_or_raise(group_id, user_id)
        if group.name == PERSONAL_GROUP_NAME:
            raise PersonalGroupProtectedException()
        new_member = self.repository.get_user_by_email(data.email)
        if new_member is None:
            raise UserEmailNotFoundException(data.email)
        if any(member.user_id == new_member.user_id for member in group.users):
            raise AlreadyGroupMemberException(data.email)
        self.repository.add_user_to_group(new_member.user_id, group.id)
        return self.get_group_by_user(group_id, user_id)

    def leave_group(self, group_id: int, user_id: str) -> None:
        group = self._get_group_or_raise(group_id, user_id)
        if group.name == PERSONAL_GROUP_NAME:
            raise PersonalGroupProtectedException()
        if self.repository.count_members(group.id) <= 1:
            raise LastGroupMemberException()
        self.repository.remove_user_from_group(user_id, group.id)

    def remove_member(self, group_id: int, current_user_id: str, member_user_id: str) -> None:
        group = self._get_group_or_raise(
            group_id,
            current_user_id,
        )

        if group.name == PERSONAL_GROUP_NAME:
            raise PersonalGroupProtectedException()

        if not any(
            member.user_id == member_user_id
            for member in group.users
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this group.",
            )

        if self.repository.count_members(group.id) <= 1:
            raise LastGroupMemberException()

        self.repository.remove_user_from_group(member_user_id, group.id)