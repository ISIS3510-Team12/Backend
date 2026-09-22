from datetime import UTC, datetime

from sqlmodel import select

from app.models import DeviceToken
from app.repositories import BaseRepository


class DeviceTokenRepository(BaseRepository):
    def get_by_token(self, token: str) -> DeviceToken | None:
        statement = select(DeviceToken).where(DeviceToken.token == token)
        return self.db.exec(statement).first()

    def get_tokens_for_user(self, user_id: str) -> list[DeviceToken]:
        statement = select(DeviceToken).where(DeviceToken.user_id == user_id)
        results = self.db.exec(statement).all()
        return list(results)

    def save_token(self, user_id: str, token: str, platform: str) -> DeviceToken:
        now = datetime.now(UTC).replace(tzinfo=None)
        device_token = self.get_by_token(token)

        if device_token is None:
            device_token = DeviceToken(
                user_id=user_id,
                token=token,
                platform=platform,
                created_at=now,
                last_seen_at=now,
            )
        else:
            device_token.user_id = user_id
            device_token.platform = platform
            device_token.last_seen_at = now

        self.db.add(device_token)
        self.db.commit()
        self.db.refresh(device_token)
        return device_token

    def delete_token(self, token: str) -> None:
        device_token = self.get_by_token(token)

        if device_token is None:
            return

        self.db.delete(device_token)
        self.db.commit()
